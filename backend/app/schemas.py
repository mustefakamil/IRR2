"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Catalog ----------------------------------------------------------------
class CropOut(ORMModel):
    id: int
    name_en: str
    name_ar: str
    scientific_name: str
    category: str
    l_ini: int
    l_dev: int
    l_mid: int
    l_late: int
    kc_ini: float
    kc_mid: float
    kc_end: float
    zr_min: float
    zr_max: float
    p: float
    height: float
    ky: float
    source: str


class SoilOut(ORMModel):
    id: int
    name_en: str
    name_ar: str
    theta_fc: float
    theta_wp: float
    bulk_density: float
    infiltration_mm_hr: float


class SystemOut(ORMModel):
    id: int
    name_en: str
    name_ar: str
    default_efficiency_pct: float


# --- Projects ---------------------------------------------------------------
class ProjectBase(BaseModel):
    project_name: str
    farm_name: str = ""
    field_name: str = ""
    country: str = ""
    region: str = ""
    city: str = ""
    latitude: float = 24.0
    longitude: float = 46.0
    elevation: float = 600.0
    wind_height: float = 2.0
    area_value: float = 1.0
    area_unit: str = "ha"
    planting_date: date
    crop_id: int
    soil_id: int
    system_id: int
    efficiency_pct: float = 90.0
    ecw: float = 0.0
    ece: float = 0.0
    strategy_mode: str = "refill"
    deficit_fraction: float = 1.0
    rainfall_method: str = "usda_scs"
    n_emitters: int = 0
    emitter_flow_lph: float = 4.0


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectOut(ORMModel):
    id: int
    project_name: str
    farm_name: str
    field_name: str
    country: str
    region: str
    city: str
    latitude: float
    longitude: float
    elevation: float
    wind_height: float
    area_value: float
    area_unit: str
    planting_date: date
    crop_id: int
    soil_id: int
    system_id: int
    efficiency_pct: float
    ecw: float
    ece: float
    strategy_mode: str
    deficit_fraction: float
    rainfall_method: str
    n_emitters: int
    emitter_flow_lph: float
    crop: CropOut
    soil: SoilOut
    system: SystemOut


class ProjectSummary(ORMModel):
    id: int
    project_name: str
    farm_name: str
    field_name: str
    city: str
    planting_date: date
    crop: CropOut
    soil: SoilOut


# --- Climate ----------------------------------------------------------------
class ClimateDayIn(BaseModel):
    the_date: date
    tmax: float
    tmin: float
    wind_speed: float = 2.0
    rainfall: float = 0.0
    rh_max: Optional[float] = None
    rh_min: Optional[float] = None
    rh_mean: Optional[float] = None
    solar_rad: Optional[float] = None
    sunshine_hours: Optional[float] = None


class ClimateDayOut(ClimateDayIn):
    id: int
    julian_day: int
    model_config = ConfigDict(from_attributes=True)


class ClimateBulkIn(BaseModel):
    days: list[ClimateDayIn]
    replace: bool = True
