"""Populate the database with default catalogs and (optionally) a demo project."""
from __future__ import annotations

import json
import os
from datetime import date

from .database import Base, engine, SessionLocal
from . import models, seed_data

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RIYADH_CLIMATE = os.path.join(DATA_DIR, "riyadh_climate.json")


def _load_climate_json() -> list[dict]:
    with open(RIYADH_CLIMATE, encoding="utf-8") as fh:
        return json.load(fh)


def seed_catalogs(db) -> None:
    if db.query(models.Crop).count() == 0:
        for row in seed_data.CROPS:
            db.add(models.Crop(**dict(zip(seed_data.CROP_FIELDS, row))))
    if db.query(models.Soil).count() == 0:
        for row in seed_data.SOILS:
            db.add(models.Soil(**dict(zip(seed_data.SOIL_FIELDS, row))))
    if db.query(models.IrrigationSystem).count() == 0:
        for row in seed_data.SYSTEMS:
            db.add(models.IrrigationSystem(**dict(zip(seed_data.SYSTEM_FIELDS, row))))
    db.commit()


def create_sample_project(db, year: int = 2025) -> models.Project:
    """Jazan/Riyadh demo project with a full year of real climate (spec section 3)."""
    crop = db.query(models.Crop).filter_by(name_en="Tomato").first()
    soil = db.query(models.Soil).filter_by(name_en="Sandy Loam").first()
    system = db.query(models.IrrigationSystem).filter_by(name_en="Drip Irrigation").first()

    proj = models.Project(
        project_name="Jazan Smart Irrigation Demo",
        farm_name="Demo Farm", field_name="Field A",
        country="Saudi Arabia", region="Riyadh", city="Riyadh",
        latitude=24.0, longitude=46.7, elevation=635.0, wind_height=2.0,
        area_value=1.0, area_unit="ha",
        planting_date=date(year, 10, 1),
        crop_id=crop.id, soil_id=soil.id, system_id=system.id,
        efficiency_pct=90.0, ecw=5.8, ece=9.0,
        strategy_mode="refill", rainfall_method="usda_scs",
        n_emitters=6000, emitter_flow_lph=4.0,
    )
    db.add(proj)
    db.flush()

    # Climate is a climatology; store under the leap reference year (2024) so
    # all 366 month-days are valid. The scheduler matches on month-day.
    ref_year = 2024
    for r in _load_climate_json():
        mm, dd = (int(x) for x in r["date"].split("-"))
        the_date = date(ref_year, mm, dd)
        db.add(models.ClimateData(
            project_id=proj.id, the_date=the_date, julian_day=r["jday"],
            tmax=r["tmax"], tmin=r["tmin"], wind_speed=r["wind"],
            rh_max=r["rh_max"], rh_min=r["rh_min"], solar_rad=r["rs"],
            rainfall=0.0,
        ))
    db.commit()
    db.refresh(proj)
    return proj


def init_db(with_sample: bool = True) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_catalogs(db)
        if with_sample and db.query(models.Project).count() == 0:
            create_sample_project(db)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database seeded at:", os.path.join(DATA_DIR, "irrigation.db"))
