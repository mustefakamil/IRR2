"""Project CRUD and the 'Load Sample Project' endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, seed

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _validate_refs(db: Session, payload: schemas.ProjectBase):
    if not db.get(models.Crop, payload.crop_id):
        raise HTTPException(400, "Invalid crop_id")
    if not db.get(models.Soil, payload.soil_id):
        raise HTTPException(400, "Invalid soil_id")
    if not db.get(models.IrrigationSystem, payload.system_id):
        raise HTTPException(400, "Invalid system_id")


@router.get("", response_model=list[schemas.ProjectSummary])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).order_by(models.Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    proj = db.get(models.Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    return proj


@router.post("", response_model=schemas.ProjectOut, status_code=201)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    _validate_refs(db, payload)
    proj = models.Project(**payload.model_dump())
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


@router.put("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, payload: schemas.ProjectUpdate,
                   db: Session = Depends(get_db)):
    proj = db.get(models.Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    _validate_refs(db, payload)
    for k, v in payload.model_dump().items():
        setattr(proj, k, v)
    db.commit()
    db.refresh(proj)
    return proj


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    proj = db.get(models.Project, project_id)
    if not proj:
        raise HTTPException(404, "Project not found")
    db.delete(proj)
    db.commit()


@router.post("/load-sample", response_model=schemas.ProjectOut, status_code=201)
def load_sample(db: Session = Depends(get_db)):
    """Create the Jazan/Riyadh demo project pre-filled with a year of climate."""
    proj = seed.create_sample_project(db)
    return proj
