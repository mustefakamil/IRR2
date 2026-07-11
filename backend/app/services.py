"""Bridge between ORM projects and the pure calculation engine."""
from __future__ import annotations

from datetime import date

from . import models
from .engine.scheduler import (
    build_schedule, ClimateDay, SoilParams, SiteParams, SalinityParams,
    StrategyParams, ScheduleResult,
)
from .engine.kc import CropStageParams
from .engine import irrigation, eto as eto_engine


def crop_params(crop: models.Crop) -> CropStageParams:
    return CropStageParams(
        l_ini=crop.l_ini, l_dev=crop.l_dev, l_mid=crop.l_mid, l_late=crop.l_late,
        kc_ini=crop.kc_ini, kc_mid=crop.kc_mid, kc_end=crop.kc_end,
        zr_min=crop.zr_min, zr_max=crop.zr_max, depletion_fraction=crop.p,
        height=crop.height,
    )


def climate_days(project: models.Project) -> list[ClimateDay]:
    return [
        ClimateDay(
            the_date=cd.the_date, julian_day=cd.julian_day, tmax=cd.tmax,
            tmin=cd.tmin, wind_speed=cd.wind_speed, rainfall=cd.rainfall,
            rh_max=cd.rh_max, rh_min=cd.rh_min, rh_mean=cd.rh_mean,
            solar_rad=cd.solar_rad, sunshine_hours=cd.sunshine_hours,
        )
        for cd in sorted(project.climate, key=lambda c: c.the_date)
    ]


def run_schedule(project: models.Project) -> ScheduleResult:
    crop = project.crop
    soil = project.soil
    drip = None
    if project.n_emitters and project.n_emitters > 0:
        drip = irrigation.DripSystem(project.n_emitters, project.emitter_flow_lph)
    return build_schedule(
        crop=crop_params(crop),
        soil=SoilParams(theta_fc=soil.theta_fc, theta_wp=soil.theta_wp, p_table=crop.p),
        site=SiteParams(
            latitude_deg=project.latitude, elevation_m=project.elevation,
            area_m2=project.area_m2, efficiency_pct=project.efficiency_pct,
            wind_height_m=project.wind_height,
        ),
        climate=climate_days(project),
        planting_date=project.planting_date,
        salinity=SalinityParams(ecw=project.ecw or None, ece=project.ece or None),
        strategy=StrategyParams(
            mode=project.strategy_mode, deficit_fraction=project.deficit_fraction,
            rainfall_method=project.rainfall_method,
        ),
        drip=drip,
    )


def eto_detail(project: models.Project, cd: models.ClimateData,
               julian_day: int | None = None) -> dict:
    """Full ETo intermediate breakdown for one day (Show Calculation Details)."""
    r = eto_engine.compute_eto(
        julian_day=julian_day or cd.the_date.timetuple().tm_yday,
        tmax_c=cd.tmax, tmin_c=cd.tmin,
        latitude_deg=project.latitude, elevation_m=project.elevation,
        wind_speed=cd.wind_speed, wind_height_m=project.wind_height,
        rh_max=cd.rh_max, rh_min=cd.rh_min, rh_mean=cd.rh_mean,
        solar_rad=cd.solar_rad, sunshine_hours=cd.sunshine_hours,
    )
    return {k: (round(v, 6) if isinstance(v, float) else v)
            for k, v in r.to_dict().items()}
