"""SQLAlchemy ORM models (spec section 35 database architecture)."""
from __future__ import annotations

from datetime import date, datetime
from sqlalchemy import String, Float, Integer, ForeignKey, Date, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Crop(Base):
    __tablename__ = "crops"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_en: Mapped[str] = mapped_column(String, index=True)
    name_ar: Mapped[str] = mapped_column(String, default="")
    scientific_name: Mapped[str] = mapped_column(String, default="")
    category: Mapped[str] = mapped_column(String, index=True)
    l_ini: Mapped[int]
    l_dev: Mapped[int]
    l_mid: Mapped[int]
    l_late: Mapped[int]
    kc_ini: Mapped[float]
    kc_mid: Mapped[float]
    kc_end: Mapped[float]
    zr_min: Mapped[float]
    zr_max: Mapped[float]
    p: Mapped[float]
    height: Mapped[float] = mapped_column(default=1.0)
    ky: Mapped[float] = mapped_column(default=1.0)
    source: Mapped[str] = mapped_column(String, default="fao56")


class Soil(Base):
    __tablename__ = "soils"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_en: Mapped[str] = mapped_column(String, index=True)
    name_ar: Mapped[str] = mapped_column(String, default="")
    theta_fc: Mapped[float]
    theta_wp: Mapped[float]
    bulk_density: Mapped[float] = mapped_column(default=1.4)
    infiltration_mm_hr: Mapped[float] = mapped_column(default=10.0)


class IrrigationSystem(Base):
    __tablename__ = "irrigation_systems"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_en: Mapped[str] = mapped_column(String, index=True)
    name_ar: Mapped[str] = mapped_column(String, default="")
    default_efficiency_pct: Mapped[float]


class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_en: Mapped[str] = mapped_column(String, index=True)
    name_ar: Mapped[str] = mapped_column(String, default="")
    country: Mapped[str] = mapped_column(String, default="Saudi Arabia")
    region: Mapped[str] = mapped_column(String, index=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    elevation: Mapped[float]


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    salt: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String, default="")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    # identification
    project_name: Mapped[str] = mapped_column(String, index=True)
    farm_name: Mapped[str] = mapped_column(String, default="")
    field_name: Mapped[str] = mapped_column(String, default="")
    country: Mapped[str] = mapped_column(String, default="")
    region: Mapped[str] = mapped_column(String, default="")
    city: Mapped[str] = mapped_column(String, default="")
    # location
    latitude: Mapped[float] = mapped_column(default=24.0)
    longitude: Mapped[float] = mapped_column(default=46.0)
    elevation: Mapped[float] = mapped_column(default=600.0)
    wind_height: Mapped[float] = mapped_column(default=2.0)
    # field
    area_value: Mapped[float] = mapped_column(default=1.0)
    area_unit: Mapped[str] = mapped_column(String, default="ha")   # ha | m2 | acre
    planting_date: Mapped[date] = mapped_column(Date, default=date.today)
    # references
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"))
    soil_id: Mapped[int] = mapped_column(ForeignKey("soils.id"))
    system_id: Mapped[int] = mapped_column(ForeignKey("irrigation_systems.id"))
    crop: Mapped["Crop"] = relationship()
    soil: Mapped["Soil"] = relationship()
    system: Mapped["IrrigationSystem"] = relationship()
    # irrigation / salinity
    efficiency_pct: Mapped[float] = mapped_column(default=90.0)
    ecw: Mapped[float] = mapped_column(default=0.0)
    ece: Mapped[float] = mapped_column(default=0.0)
    # strategy
    strategy_mode: Mapped[str] = mapped_column(String, default="refill")
    deficit_fraction: Mapped[float] = mapped_column(default=1.0)
    rainfall_method: Mapped[str] = mapped_column(String, default="usda_scs")
    # drip system geometry (optional)
    n_emitters: Mapped[int] = mapped_column(default=0)
    emitter_flow_lph: Mapped[float] = mapped_column(default=4.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    climate: Mapped[list["ClimateData"]] = relationship(
        back_populates="project", cascade="all, delete-orphan")

    @property
    def area_m2(self) -> float:
        if self.area_unit == "ha":
            return self.area_value * 10000
        if self.area_unit == "acre":
            return self.area_value * 4046.856
        return self.area_value  # m2


class ClimateData(Base):
    __tablename__ = "climate_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    the_date: Mapped[date] = mapped_column(Date, index=True)
    julian_day: Mapped[int]
    tmax: Mapped[float]
    tmin: Mapped[float]
    wind_speed: Mapped[float] = mapped_column(default=2.0)
    rainfall: Mapped[float] = mapped_column(default=0.0)
    rh_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    rh_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    rh_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    solar_rad: Mapped[float | None] = mapped_column(Float, nullable=True)
    sunshine_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="climate")
