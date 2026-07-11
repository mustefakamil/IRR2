"""Climate data: manual entry, bulk entry, CSV/Excel upload."""
from __future__ import annotations

import csv
import io
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/projects/{project_id}/climate", tags=["climate"])


def _proj(db: Session, project_id: int) -> models.Project:
    proj = db.get(models.Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    return proj


def _julian(d: date) -> int:
    return d.timetuple().tm_yday


@router.get("", response_model=list[schemas.ClimateDayOut])
def list_climate(project_id: int, db: Session = Depends(get_db)):
    _proj(db, project_id)
    return (db.query(models.ClimateData)
            .filter_by(project_id=project_id)
            .order_by(models.ClimateData.the_date).all())


@router.post("/bulk", response_model=dict)
def set_climate(project_id: int, payload: schemas.ClimateBulkIn,
                db: Session = Depends(get_db)):
    _proj(db, project_id)
    if payload.replace:
        db.query(models.ClimateData).filter_by(project_id=project_id).delete()
    for d in payload.days:
        db.add(_row_from_in(project_id, d))
    db.commit()
    return {"inserted": len(payload.days)}


def _row_from_in(project_id: int, d: schemas.ClimateDayIn) -> models.ClimateData:
    if d.tmax < d.tmin:
        raise HTTPException(400, f"Tmax < Tmin on {d.the_date}")
    for rh in (d.rh_max, d.rh_min, d.rh_mean):
        if rh is not None and not (0 <= rh <= 100):
            raise HTTPException(400, f"RH out of range on {d.the_date}")
    return models.ClimateData(
        project_id=project_id, the_date=d.the_date, julian_day=_julian(d.the_date),
        tmax=d.tmax, tmin=d.tmin, wind_speed=d.wind_speed, rainfall=d.rainfall,
        rh_max=d.rh_max, rh_min=d.rh_min, rh_mean=d.rh_mean,
        solar_rad=d.solar_rad, sunshine_hours=d.sunshine_hours,
    )


@router.delete("", status_code=204)
def clear_climate(project_id: int, db: Session = Depends(get_db)):
    _proj(db, project_id)
    db.query(models.ClimateData).filter_by(project_id=project_id).delete()
    db.commit()


# --- CSV / Excel upload -----------------------------------------------------
_ALIASES = {
    "date": "the_date", "tmax": "tmax", "tmin": "tmin", "wind": "wind_speed",
    "windspeed": "wind_speed", "wind_speed": "wind_speed", "u2": "wind_speed",
    "rain": "rainfall", "rainfall": "rainfall", "precip": "rainfall",
    "rhmax": "rh_max", "rh_max": "rh_max", "rhmin": "rh_min", "rh_min": "rh_min",
    "rhmean": "rh_mean", "rh_mean": "rh_mean", "rh": "rh_mean",
    "rs": "solar_rad", "solar": "solar_rad", "solar_rad": "solar_rad",
    "radiation": "solar_rad", "sunshine": "sunshine_hours",
    "sunshine_hours": "sunshine_hours", "n": "sunshine_hours",
}


def _parse_date(v) -> date:
    if isinstance(v, (datetime, date)):
        return v if isinstance(v, date) and not isinstance(v, datetime) else v.date()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(v).strip(), fmt).date()
        except ValueError:
            continue
    raise HTTPException(400, f"Unrecognised date: {v}")


def _num(v):
    if v is None or str(v).strip() == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


@router.post("/upload", response_model=dict)
async def upload_climate(project_id: int, file: UploadFile = File(...),
                         replace: bool = True, db: Session = Depends(get_db)):
    _proj(db, project_id)
    content = await file.read()
    name = (file.filename or "").lower()
    rows: list[dict] = []

    if name.endswith((".xlsx", ".xlsm")):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=True)
        ws = wb.active
        it = ws.iter_rows(values_only=True)
        headers = [str(h).strip().lower().replace(" ", "") if h is not None else ""
                   for h in next(it)]
        for raw in it:
            rows.append(dict(zip(headers, raw)))
    else:  # CSV
        text = content.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        for raw in reader:
            rows.append({(k or "").strip().lower().replace(" ", ""): v
                         for k, v in raw.items()})

    parsed: list[schemas.ClimateDayIn] = []
    for raw in rows:
        mapped: dict = {}
        for key, val in raw.items():
            field = _ALIASES.get(key)
            if not field:
                continue
            mapped[field] = _parse_date(val) if field == "the_date" else _num(val)
        if not mapped.get("the_date") or mapped.get("tmax") is None or mapped.get("tmin") is None:
            continue
        parsed.append(schemas.ClimateDayIn(**mapped))

    if not parsed:
        raise HTTPException(400, "No valid rows found. Need at least Date, Tmax, Tmin.")
    if replace:
        db.query(models.ClimateData).filter_by(project_id=project_id).delete()
    for d in parsed:
        db.add(_row_from_in(project_id, d))
    db.commit()
    return {"inserted": len(parsed), "columns_detected": sorted(
        {f for r in rows for f in (_ALIASES.get(k) for k in r) if f})}
