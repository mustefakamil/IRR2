"""Unit tests for the FAO-56 engine.

The vapour-pressure, slope, psychrometric and wind terms are validated against
the reference "Irrigation Schedule program" workbook (Riyadh, 1 Jan). Ra is
validated against the *correct* FAO-56 Eq. 21 (the workbook multiplies the
inverse-distance dr onto only the first bracket term, which slightly inflates
its Ra/ETo; we implement the paper's formula instead).
"""
import math
from datetime import date

import pytest

from app.engine import eto as e
from app.engine.kc import CropStageParams, kc_for_day, stage_for_day, root_depth_for_day
from app.engine import soil, salinity, irrigation, rainfall
from app.engine.scheduler import (
    build_schedule, ClimateDay, SoilParams, SiteParams, SalinityParams, StrategyParams,
)

# Jan-1 Riyadh inputs from the workbook
JAN1 = dict(julian_day=1, tmax_c=21, tmin_c=7, latitude_deg=24, elevation_m=635,
            wind_speed=2.7, rh_max=71.6, rh_min=30.5, solar_rad=13.8)


def test_vapour_pressure_matches_workbook():
    r = e.compute_eto(**JAN1)
    assert r.e_tmax == pytest.approx(2.4870054, abs=1e-6)
    assert r.e_tmin == pytest.approx(1.0018584, abs=1e-6)
    assert r.es == pytest.approx(1.7444319, abs=1e-6)
    assert r.ea == pytest.approx(0.7379336, abs=1e-6)
    assert r.delta == pytest.approx(0.1037357, abs=1e-6)


def test_pressure_and_gamma():
    r = e.compute_eto(**JAN1)
    # Workbook P uses same eq.; gamma coef 0.000665 (spec) vs 0.00066474 (workbook)
    assert r.pressure == pytest.approx(94.02, abs=0.05)
    assert r.gamma == pytest.approx(0.0625, abs=0.001)


def test_wind_at_2m_is_identity():
    r = e.compute_eto(**JAN1)
    assert r.u2 == pytest.approx(2.7, abs=1e-6)


def test_extraterrestrial_radiation_follows_fao56():
    # Correct FAO-56 Eq. 21 with dr across the whole bracket -> 23.552
    r = e.compute_eto(**JAN1)
    assert r.ra == pytest.approx(23.552, abs=0.01)
    assert r.rso == pytest.approx(0.75 * r.ra, abs=1e-6)


def test_eto_regression_jan1():
    # Correct FAO-56 value (~3.413). Workbook shows 3.761 due to its Ra bug.
    r = e.compute_eto(**JAN1)
    assert r.eto == pytest.approx(3.413, abs=0.01)


def test_eto_requires_radiation_input():
    with pytest.raises(ValueError):
        e.compute_eto(julian_day=1, tmax_c=21, tmin_c=7, latitude_deg=24,
                      elevation_m=635, wind_speed=2.7, rh_mean=50)


def test_ea_preference_order():
    etmax, etmin = 2.487, 1.002
    both = e.compute_ea(etmax, etmin, 71.6, 30.5)
    rhmax_only = e.compute_ea(etmax, etmin, 71.6, None)
    rhmean = e.compute_ea(etmax, etmin, None, None, 50)
    assert both == pytest.approx((etmin * 0.716 + etmax * 0.305) / 2)
    assert rhmax_only == pytest.approx(etmin * 0.716)
    assert rhmean == pytest.approx(0.5 * (etmax + etmin) / 2)


# --- Kc curve ---------------------------------------------------------------
CROP = CropStageParams(l_ini=30, l_dev=40, l_mid=40, l_late=30,
                       kc_ini=0.6, kc_mid=1.15, kc_end=0.8,
                       zr_min=0.3, zr_max=1.0, depletion_fraction=0.4)


def test_kc_stage_boundaries():
    assert stage_for_day(1, CROP) == "initial"
    assert stage_for_day(30, CROP) == "initial"
    assert stage_for_day(31, CROP) == "development"
    assert stage_for_day(70, CROP) == "development"
    assert stage_for_day(71, CROP) == "mid"
    assert stage_for_day(110, CROP) == "mid"
    assert stage_for_day(111, CROP) == "late"
    assert stage_for_day(140, CROP) == "late"
    assert stage_for_day(141, CROP) == "end"


def test_kc_interpolation():
    assert kc_for_day(1, CROP) == pytest.approx(0.6)
    assert kc_for_day(50, CROP) == pytest.approx(0.6 + (20 / 40) * (1.15 - 0.6))
    assert kc_for_day(90, CROP) == pytest.approx(1.15)
    # midpoint of late stage: halfway from 1.15 to 0.8
    assert kc_for_day(125, CROP) == pytest.approx(1.15 + (15 / 30) * (0.8 - 1.15))


def test_root_depth_growth():
    assert root_depth_for_day(1, CROP) == pytest.approx(0.3 + (1 / 70) * 0.7)
    assert root_depth_for_day(70, CROP) == pytest.approx(1.0)
    assert root_depth_for_day(120, CROP) == pytest.approx(1.0)


# --- Soil -------------------------------------------------------------------
def test_taw_and_raw():
    taw = soil.total_available_water(0.21, 0.09, 1.0)   # sandy loam, 1 m
    assert taw == pytest.approx(120.0)
    raw = soil.readily_available_water(0.5, taw)
    assert raw == pytest.approx(60.0)


def test_p_adjustment_bounds():
    assert soil.adjusted_depletion_fraction(0.5, 5) == pytest.approx(0.5)
    assert soil.adjusted_depletion_fraction(0.5, 0) == pytest.approx(0.7)
    assert soil.adjusted_depletion_fraction(0.8, 0) == 0.8   # capped upper


# --- Salinity / irrigation --------------------------------------------------
def test_leaching_requirement():
    assert salinity.leaching_requirement(5.8, 9) == pytest.approx(5.8 / (45 - 5.8))
    with pytest.raises(ValueError):
        salinity.leaching_requirement(50, 9)


def test_gross_depth_and_volume():
    assert irrigation.gross_depth(10, 90) == pytest.approx(10 / 0.9)
    assert irrigation.water_volume_m3(10, 10000) == pytest.approx(100.0)


def test_runtime():
    sys = irrigation.DripSystem(n_emitters=1000, emitter_flow_lph=4)
    assert sys.system_flow_lph == 4000
    assert irrigation.runtime_hours(4, 4000) == pytest.approx(1.0)


def test_rainfall_methods():
    assert rainfall.effective_rainfall(0, "usda_scs") == 0
    assert rainfall.effective_rainfall(20, "fixed", 0.8) == pytest.approx(16.0)
    assert rainfall.effective_rainfall(100, "fao") == pytest.approx(55.0)
    assert rainfall.effective_rainfall(30, "manual", manual_value=12) == 12


# --- End-to-end schedule ----------------------------------------------------
def test_schedule_runs_and_triggers_irrigation():
    crop = CropStageParams(l_ini=10, l_dev=10, l_mid=10, l_late=5,
                           kc_ini=0.6, kc_mid=1.15, kc_end=0.8,
                           zr_min=0.3, zr_max=0.6, depletion_fraction=0.5)
    climate = []
    for i in range(crop.season_length):
        d = date(2025, 1, 1)
        from datetime import timedelta
        dd = d + timedelta(days=i)
        jd = dd.timetuple().tm_yday
        climate.append(ClimateDay(the_date=dd, julian_day=jd, tmax=32, tmin=18,
                                  wind_speed=2.0, rh_max=60, rh_min=25, solar_rad=22))
    res = build_schedule(
        crop=crop,
        soil=SoilParams(theta_fc=0.21, theta_wp=0.09, p_table=0.5),
        site=SiteParams(latitude_deg=24, elevation_m=635, area_m2=10000, efficiency_pct=90),
        climate=climate, planting_date=date(2025, 1, 1),
        strategy=StrategyParams(mode="refill"),
        drip=irrigation.DripSystem(n_emitters=5000, emitter_flow_lph=4),
    )
    assert len(res.daily) == crop.season_length
    assert res.summary.n_irrigations >= 1
    # every depletion stays within [0, TAW]
    for row in res.daily:
        assert 0 <= row.ds_end <= row.taw + 1e-6
    # volume must equal Dg * area / 1000 on an irrigation day
    irr_days = [r for r in res.daily if r.irrigate]
    assert irr_days
    r0 = irr_days[0]
    assert r0.volume_m3 == pytest.approx(r0.dg * 10000 / 1000, abs=0.1)
