"""Reference catalog endpoints: crops, soils, irrigation systems."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.get("/crops", response_model=list[schemas.CropOut])
def list_crops(category: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Crop)
    if category:
        q = q.filter(models.Crop.category == category)
    return q.order_by(models.Crop.category, models.Crop.name_en).all()


@router.get("/crops/{crop_id}", response_model=schemas.CropOut)
def get_crop(crop_id: int, db: Session = Depends(get_db)):
    crop = db.get(models.Crop, crop_id)
    if not crop:
        raise HTTPException(404, "Crop not found")
    return crop


@router.put("/crops/{crop_id}", response_model=schemas.CropOut)
def update_crop(crop_id: int, payload: dict, db: Session = Depends(get_db)):
    crop = db.get(models.Crop, crop_id)
    if not crop:
        raise HTTPException(404, "Crop not found")
    editable = {"l_ini", "l_dev", "l_mid", "l_late", "kc_ini", "kc_mid",
                "kc_end", "zr_min", "zr_max", "p", "height", "ky"}
    for k, v in payload.items():
        if k in editable:
            setattr(crop, k, v)
    db.commit()
    db.refresh(crop)
    return crop


@router.get("/soils", response_model=list[schemas.SoilOut])
def list_soils(db: Session = Depends(get_db)):
    return db.query(models.Soil).order_by(models.Soil.id).all()


@router.get("/systems", response_model=list[schemas.SystemOut])
def list_systems(db: Session = Depends(get_db)):
    return db.query(models.IrrigationSystem).order_by(models.IrrigationSystem.id).all()


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(models.Crop.category).distinct().all()
    return sorted({r[0] for r in rows})
