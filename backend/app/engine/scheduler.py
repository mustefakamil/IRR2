"""Daily irrigation-scheduling orchestrator.

Combines the ETo, Kc, soil, salinity, rainfall and irrigation engines into a
day-by-day soil-water balance and irrigation schedule following FAO-56
(spec sections 14-22). Pure and deterministic: given the same inputs it always
returns the same schedule.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from typing import List, Optional

from . import eto as eto_engine
from . import soil as soil_engine
from . import salinity as salinity_engine
from . import irrigation as irr_engine
from .kc import CropStageParams, crop_state_for_day, STAGE_END
from .rainfall import effective_rainfall


# --- Input containers -------------------------------------------------------
@dataclass
class ClimateDay:
    the_date: date
    julian_day: int
    tmax: float
    tmin: float
    wind_speed: float
    rainfall: float = 0.0
    rh_max: Optional[float] = None
    rh_min: Optional[float] = None
    rh_mean: Optional[float] = None
    solar_rad: Optional[float] = None       # measured Rs, MJ/m2/day
    sunshine_hours: Optional[float] = None


@dataclass
class SoilParams:
    theta_fc: float          # volumetric fraction
    theta_wp: float          # volumetric fraction
    p_table: float           # depletion fraction (MAD)


@dataclass
class SiteParams:
    latitude_deg: float
    elevation_m: float
    area_m2: float
    efficiency_pct: float
    wind_height_m: float = 2.0


@dataclass
class SalinityParams:
    ecw: Optional[float] = None      # water EC (dS/m)
    ece: Optional[float] = None      # crop threshold ECe (dS/m)


@dataclass
class StrategyParams:
    mode: str = "refill"             # refill | mad | deficit
    deficit_fraction: float = 1.0    # fraction of ETc / net depth applied
    rainfall_method: str = "usda_scs"
    fixed_rain_fraction: float = 0.8
    adjust_p_for_et: bool = True
    initial_depletion_mm: float = 0.0


@dataclass
class DailySchedule:
    day: int
    the_date: str
    julian_day: int
    stage: str
    eto: float
    kc: float
    etc: float
    rainfall: float
    pe: float
    lr: float
    iwr: float
    root_depth: float
    taw: float
    raw: float
    p: float
    ds_begin: float
    daily_water_use: float
    ds_end: float
    irrigate: bool
    dn: float
    dg: float
    volume_m3: float
    runtime_hours: Optional[float]
    deep_percolation: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SeasonSummary:
    days: int
    n_irrigations: int
    total_etc: float
    total_eto: float
    total_effective_rain: float
    total_net_depth: float
    total_gross_depth: float
    total_net_volume_m3: float
    total_gross_volume_m3: float
    total_runtime_hours: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScheduleResult:
    daily: List[DailySchedule]
    summary: SeasonSummary

    def to_dict(self) -> dict:
        return {"daily": [d.to_dict() for d in self.daily],
                "summary": self.summary.to_dict()}


def build_schedule(
    *,
    crop: CropStageParams,
    soil: SoilParams,
    site: SiteParams,
    climate: List[ClimateDay],
    planting_date: date,
    salinity: SalinityParams | None = None,
    strategy: StrategyParams | None = None,
    drip: irr_engine.DripSystem | None = None,
) -> ScheduleResult:
    strategy = strategy or StrategyParams()
    salinity = salinity or SalinityParams()

    # Leaching fraction (constant over the season if salinity provided)
    lr_fraction = 0.0
    if salinity.ecw and salinity.ece:
        try:
            lr_fraction = salinity_engine.leaching_requirement(salinity.ecw, salinity.ece)
        except ValueError:
            lr_fraction = 0.0

    # Index climate as a climatology keyed by (month, day) so a growing season
    # can span a year boundary or a leap year regardless of the source year.
    climate_by_md = {(c.the_date.month, c.the_date.day): c for c in climate}

    daily: List[DailySchedule] = []
    dr_prev = strategy.initial_depletion_mm
    n_irr = 0
    tot = dict(etc=0.0, eto=0.0, pe=0.0, dn=0.0, dg=0.0, netv=0.0, grossv=0.0, rt=0.0)

    season_len = crop.season_length
    for dap in range(1, season_len + 1):
        the_date = planting_date + timedelta(days=dap - 1)
        state = crop_state_for_day(dap, crop)
        if state.stage == STAGE_END or state.kc is None or state.root_depth is None:
            break

        cd = climate_by_md.get((the_date.month, the_date.day))
        if cd is None:
            # No climate for this day -> skip ET but keep the row for continuity
            continue
        # Use the real day-of-year of the scheduled date for solar geometry
        jday = the_date.timetuple().tm_yday

        r = eto_engine.compute_eto(
            julian_day=jday, tmax_c=cd.tmax, tmin_c=cd.tmin,
            latitude_deg=site.latitude_deg, elevation_m=site.elevation_m,
            wind_speed=cd.wind_speed, wind_height_m=site.wind_height_m,
            rh_max=cd.rh_max, rh_min=cd.rh_min, rh_mean=cd.rh_mean,
            solar_rad=cd.solar_rad, sunshine_hours=cd.sunshine_hours,
        )
        eto = r.eto
        kc = state.kc
        etc = kc * eto

        # Soil storage for today's root depth
        taw = soil_engine.total_available_water(soil.theta_fc, soil.theta_wp, state.root_depth)
        p_adj = (soil_engine.adjusted_depletion_fraction(soil.p_table, etc)
                 if strategy.adjust_p_for_et else soil.p_table)
        raw = soil_engine.readily_available_water(p_adj, taw)

        pe = effective_rainfall(cd.rainfall, strategy.rainfall_method,
                                strategy.fixed_rain_fraction)
        iwr = max(0.0, etc - pe)

        # --- Water balance ---------------------------------------------------
        ds_begin = dr_prev
        dr_tent = dr_prev - pe + etc
        deep_perc = 0.0
        if dr_tent < 0:
            deep_perc = -dr_tent
            dr_tent = 0.0

        irrigate = dr_tent >= raw and raw > 0
        dn = dg = volume = 0.0
        runtime = None
        if irrigate:
            if strategy.mode == "mad":
                net_full = raw
            else:  # refill or deficit both refill toward FC, deficit scales it
                net_full = dr_tent
            dn = net_full * strategy.deficit_fraction
            dg = irr_engine.gross_depth(dn, site.efficiency_pct, lr_fraction)
            volume_net = irr_engine.water_volume_m3(dn, site.area_m2)
            volume = irr_engine.water_volume_m3(dg, site.area_m2)
            if drip:
                runtime = irr_engine.runtime_hours(volume, drip.system_flow_lph)
            dr_end = dr_tent - dn
            n_irr += 1
            tot["dn"] += dn
            tot["dg"] += dg
            tot["netv"] += volume_net
            tot["grossv"] += volume
            if runtime:
                tot["rt"] += runtime
        else:
            dr_end = dr_tent

        dr_prev = dr_end
        tot["etc"] += etc
        tot["eto"] += eto
        tot["pe"] += pe

        daily.append(DailySchedule(
            day=dap, the_date=the_date.isoformat(), julian_day=jday,
            stage=state.stage, eto=round(eto, 3), kc=round(kc, 3),
            etc=round(etc, 3), rainfall=round(cd.rainfall, 2), pe=round(pe, 2),
            lr=round(lr_fraction, 4), iwr=round(iwr, 3),
            root_depth=round(state.root_depth, 3), taw=round(taw, 2),
            raw=round(raw, 2), p=round(p_adj, 3), ds_begin=round(ds_begin, 2),
            daily_water_use=round(etc, 3), ds_end=round(dr_end, 2),
            irrigate=irrigate, dn=round(dn, 2), dg=round(dg, 2),
            volume_m3=round(volume, 3), runtime_hours=(round(runtime, 2) if runtime else None),
            deep_percolation=round(deep_perc, 2),
        ))

    summary = SeasonSummary(
        days=len(daily), n_irrigations=n_irr,
        total_etc=round(tot["etc"], 2), total_eto=round(tot["eto"], 2),
        total_effective_rain=round(tot["pe"], 2),
        total_net_depth=round(tot["dn"], 2), total_gross_depth=round(tot["dg"], 2),
        total_net_volume_m3=round(tot["netv"], 2),
        total_gross_volume_m3=round(tot["grossv"], 2),
        total_runtime_hours=round(tot["rt"], 2),
    )
    return ScheduleResult(daily=daily, summary=summary)
