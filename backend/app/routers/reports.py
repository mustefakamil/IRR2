"""Report exports: Excel schedule and CSV."""
from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, services

router = APIRouter(prefix="/api/projects/{project_id}/report", tags=["reports"])

COLUMNS = [
    ("day", "Day"), ("the_date", "Date"), ("julian_day", "Julian"),
    ("stage", "Stage"), ("eto", "ETo (mm)"), ("kc", "Kc"), ("etc", "ETc (mm)"),
    ("rainfall", "Rain (mm)"), ("pe", "Pe (mm)"), ("lr", "LR"), ("iwr", "IWR (mm)"),
    ("root_depth", "Zr (m)"), ("taw", "TAW (mm)"), ("raw", "RAW (mm)"),
    ("p", "p"), ("ds_begin", "Ds begin"), ("daily_water_use", "Daily use"),
    ("ds_end", "Ds end"), ("irrigate", "Irrigate"), ("dn", "Dn (mm)"),
    ("dg", "Dg (mm)"), ("volume_m3", "Volume (m3)"), ("runtime_hours", "Runtime (h)"),
]


def _proj(db, project_id):
    proj = db.get(models.Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    if not proj.climate:
        raise HTTPException(400, "Project has no climate data.")
    return proj


@router.get("/csv")
def report_csv(project_id: int, db: Session = Depends(get_db)):
    proj = _proj(db, project_id)
    res = services.run_schedule(proj)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([h for _, h in COLUMNS])
    for d in res.daily:
        row = d.to_dict()
        w.writerow([row.get(k) for k, _ in COLUMNS])
    buf.seek(0)
    fname = f"schedule_{proj.project_name.replace(' ', '_')}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@router.get("/excel")
def report_excel(project_id: int, db: Session = Depends(get_db)):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment

    proj = _proj(db, project_id)
    res = services.run_schedule(proj)
    wb = openpyxl.Workbook()

    # --- Summary sheet ---
    ws = wb.active
    ws.title = "Summary"
    crop, soil, system = proj.crop, proj.soil, proj.system
    info = [
        ("Smart Irrigation Scheduling Platform — FAO-56", ""),
        ("Project", proj.project_name), ("Farm", proj.farm_name),
        ("Field", proj.field_name),
        ("Location", f"{proj.city}, {proj.region}, {proj.country}"),
        ("Latitude / Longitude", f"{proj.latitude} / {proj.longitude}"),
        ("Elevation (m)", proj.elevation),
        ("Area", f"{proj.area_value} {proj.area_unit} ({proj.area_m2:.0f} m²)"),
        ("Planting date", proj.planting_date.isoformat()),
        ("Crop", f"{crop.name_en} ({crop.name_ar})"),
        ("Soil", f"{soil.name_en} (FC={soil.theta_fc}, WP={soil.theta_wp})"),
        ("Irrigation system", f"{system.name_en} @ {proj.efficiency_pct}%"),
        ("Water salinity ECw / ECe", f"{proj.ecw} / {proj.ece} dS/m"),
        ("", ""),
        ("Season length (days)", res.summary.days),
        ("Number of irrigations", res.summary.n_irrigations),
        ("Total ETo (mm)", res.summary.total_eto),
        ("Total ETc (mm)", res.summary.total_etc),
        ("Effective rainfall (mm)", res.summary.total_effective_rain),
        ("Total net depth (mm)", res.summary.total_net_depth),
        ("Total gross depth (mm)", res.summary.total_gross_depth),
        ("Gross water volume (m³)", res.summary.total_gross_volume_m3),
        ("Total runtime (hours)", res.summary.total_runtime_hours),
    ]
    ws["A1"].font = Font(bold=True, size=14)
    for i, (k, v) in enumerate(info, start=1):
        ws.cell(i, 1, k).font = Font(bold=True)
        ws.cell(i, 2, v)
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 40

    # --- Daily schedule sheet ---
    ds = wb.create_sheet("Daily Schedule")
    header_fill = PatternFill("solid", fgColor="1B5E20")
    for c, (_, h) in enumerate(COLUMNS, start=1):
        cell = ds.cell(1, c, h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
    irr_fill = PatternFill("solid", fgColor="C8E6C9")
    for r, d in enumerate(res.daily, start=2):
        row = d.to_dict()
        for c, (k, _) in enumerate(COLUMNS, start=1):
            cell = ds.cell(r, c, row.get(k))
            if row.get("irrigate"):
                cell.fill = irr_fill
    ds.freeze_panes = "A2"

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    fname = f"irrigation_report_{proj.project_name.replace(' ', '_')}.xlsx"
    return StreamingResponse(
        out, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'})
