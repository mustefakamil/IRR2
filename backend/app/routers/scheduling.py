"""Scheduling results, dashboard, calendar and formula details."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, services

router = APIRouter(prefix="/api/projects/{project_id}", tags=["scheduling"])


def _proj(db: Session, project_id: int) -> models.Project:
    proj = db.get(models.Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    if not proj.climate:
        raise HTTPException(400, "Project has no climate data. Add climate first.")
    return proj


@router.get("/schedule")
def get_schedule(project_id: int, db: Session = Depends(get_db)):
    proj = _proj(db, project_id)
    result = services.run_schedule(proj)
    return result.to_dict()


@router.get("/dashboard")
def get_dashboard(project_id: int, as_of: date | None = None,
                  db: Session = Depends(get_db)):
    proj = _proj(db, project_id)
    res = services.run_schedule(proj)
    daily = res.daily
    if not daily:
        raise HTTPException(400, "Schedule produced no days (check climate coverage).")

    # "Today" = as_of if within season else the first day
    idx = 0
    if as_of:
        for i, d in enumerate(daily):
            if d.the_date >= as_of.isoformat():
                idx = i
                break
    today = daily[idx]

    next_irr = next((d for d in daily[idx:] if d.irrigate), None)
    crop = proj.crop
    return {
        "project": {"id": proj.id, "name": proj.project_name,
                    "crop": crop.name_en, "crop_ar": crop.name_ar,
                    "field": proj.field_name, "city": proj.city},
        "today": today.to_dict(),
        "next_irrigation": next_irr.to_dict() if next_irr else None,
        "summary": res.summary.to_dict(),
        "kc_curve": [{"day": d.day, "kc": d.kc} for d in daily],
        "trends": [
            {"day": d.day, "date": d.the_date, "eto": d.eto, "etc": d.etc,
             "ds_end": d.ds_end, "raw": d.raw, "taw": d.taw,
             "dg": d.dg, "rainfall": d.rainfall, "pe": d.pe}
            for d in daily
        ],
    }


@router.get("/calendar")
def get_calendar(project_id: int, db: Session = Depends(get_db)):
    proj = _proj(db, project_id)
    res = services.run_schedule(proj)
    events = []
    # high-ET threshold = 80th percentile of ETc
    etcs = sorted(d.etc for d in res.daily)
    high_et = etcs[int(len(etcs) * 0.8)] if etcs else 0
    for d in res.daily:
        if d.irrigate:
            status = "irrigation_required"
        elif d.rainfall > 0:
            status = "rainfall_event"
        elif d.ds_end >= 0.9 * d.raw and d.raw > 0:
            status = "water_stress_risk"
        elif d.etc >= high_et:
            status = "high_et"
        else:
            status = "no_irrigation"
        events.append({"date": d.the_date, "day": d.day, "status": status,
                       "etc": d.etc, "ds_end": d.ds_end, "raw": d.raw,
                       "dg": d.dg, "volume_m3": d.volume_m3, "stage": d.stage})
    return {"events": events}


@router.get("/validate")
def validate(project_id: int, level: str = "L2", db: Session = Depends(get_db)):
    """Compare computed crop ET (ETc) against FAO WaPOR satellite actual ET.

    ETc is the modelled well-watered crop demand; WaPOR AETI is the observed
    actual evapotranspiration over the field. `level` selects the WaPOR
    resolution: L2 (100 m, finest available here) or L1 (300 m), with automatic
    fallback. Their ratio (AETI/ETc) indicates how closely real conditions met
    the crop demand.
    """
    from datetime import date, timedelta
    from ..weather import wapor as wapor_client

    proj = _proj(db, project_id)
    res = services.run_schedule(proj)
    computed = {
        "seasonal_etc_mm": res.summary.total_etc,
        "seasonal_eto_mm": res.summary.total_eto,
        "gross_applied_mm": res.summary.total_gross_depth,
        "days": res.summary.days,
    }

    if not res.daily:
        raise HTTPException(400, "No schedule days to validate.")
    span_start = date.fromisoformat(res.daily[0].the_date)
    span_end = date.fromisoformat(res.daily[-1].the_date)
    # WaPOR L1-AETI-D is published with a lag; clamp to a safe recent date.
    span_end = min(span_end, date.today() - timedelta(days=10))

    wapor_result: dict = {"available": wapor_client.is_ready()}
    if not wapor_client.is_ready():
        wapor_result["message"] = "rasterio/GDAL not installed on this server."
    elif span_start > span_end:
        wapor_result["message"] = ("The growing season is in the future; WaPOR "
                                    "actual ET is only available for past dates.")
    else:
        try:
            lvl = level if level in wapor_client.LEVELS else "L2"
            aeti = wapor_client.actual_et(proj.latitude, proj.longitude,
                                          span_start, span_end, level=lvl)
            etc_window = computed["seasonal_etc_mm"]
            ratio = round(aeti["total_mm"] / etc_window, 3) if etc_window else None
            wapor_result.update({
                "actual_et_mm": aeti["total_mm"],
                "dekads_found": aeti["dekads_found"],
                "dekads_expected": aeti["dekads_expected"],
                "level": aeti["level"],
                "resolution": aeti["resolution"],
                "window": {"start": span_start.isoformat(), "end": span_end.isoformat()},
                "ratio_aeti_over_etc": ratio,
                "series": aeti["series"],
                "note": ("AETI is the actual ET of the WaPOR pixel; the finer L2 "
                         "(100 m) is used where available, else L1 (300 m). The "
                         "pixel may still include non-irrigated surroundings."),
            })
        except Exception as e:
            wapor_result["message"] = f"WaPOR fetch failed: {e}"

    return {"computed": computed, "wapor": wapor_result}


@router.get("/eto-detail")
def eto_detail(project_id: int, the_date: date, db: Session = Depends(get_db)):
    """Full FAO-56 intermediate breakdown for one day (Show Calculation Details)."""
    proj = _proj(db, project_id)
    # Climate is a climatology keyed by month-day; match on those so a schedule
    # date in the planting year resolves to the stored reference-year record.
    cd = (db.query(models.ClimateData)
          .filter_by(project_id=project_id, the_date=the_date).first())
    if not cd:
        from sqlalchemy import extract
        cd = (db.query(models.ClimateData)
              .filter(models.ClimateData.project_id == project_id,
                      extract("month", models.ClimateData.the_date) == the_date.month,
                      extract("day", models.ClimateData.the_date) == the_date.day)
              .first())
    if not cd:
        raise HTTPException(404, "No climate data for that date")
    return services.eto_detail(proj, cd, julian_day=the_date.timetuple().tm_yday)
