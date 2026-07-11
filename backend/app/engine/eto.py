"""FAO-56 Penman-Monteith reference evapotranspiration (ETo) engine.

All formulas follow *FAO Irrigation and Drainage Paper No. 56*
(Allen et al., 1998). Constants match the canonical FAO-56 values, which
reproduce the reference "Irrigation Schedule program" workbook (Riyadh)
to within ~0.001 mm/day.

Every public function is pure and unit-testable. `compute_eto` returns the
final ETo together with **all** intermediate variables so the UI can render
"Show Calculation Details" (spec section 6).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict, field
from typing import Optional

# --- Physical constants (FAO-56) -------------------------------------------
SOLAR_CONSTANT = 0.0820          # Gsc, MJ m-2 min-1
STEFAN_BOLTZMANN = 4.903e-9      # sigma, MJ K-4 m-2 day-1
ALBEDO_GRASS = 0.23             # alpha, reference grass
PSYCHROMETRIC_COEF = 0.000665    # gamma = coef * P  (FAO-56 eq. 8)
AS_COEF = 0.25                   # Angstrom a_s (Rs from sunshine)
BS_COEF = 0.50                   # Angstrom b_s


# --- Elementary FAO-56 relations -------------------------------------------
def saturation_vapour_pressure(t_c: float) -> float:
    """e degrees(T), saturation vapour pressure at temperature T (kPa). FAO-56 eq. 11."""
    return 0.6108 * math.exp((17.27 * t_c) / (t_c + 237.3))


def slope_svp(t_c: float) -> float:
    """Delta, slope of the saturation vapour pressure curve (kPa/degrees C). FAO-56 eq. 13."""
    return (4098 * saturation_vapour_pressure(t_c)) / (t_c + 237.3) ** 2


def atmospheric_pressure(elevation_m: float) -> float:
    """P, atmospheric pressure (kPa) from elevation. FAO-56 eq. 7."""
    return 101.3 * ((293 - 0.0065 * elevation_m) / 293) ** 5.26


def psychrometric_constant(pressure_kpa: float) -> float:
    """gamma, psychrometric constant (kPa/degrees C). FAO-56 eq. 8."""
    return PSYCHROMETRIC_COEF * pressure_kpa


def wind_speed_2m(u_z: float, meas_height_m: float = 2.0) -> float:
    """Adjust wind speed measured at height z to 2 m. FAO-56 eq. 47."""
    if meas_height_m == 2.0:
        return u_z
    return u_z * (4.87 / math.log(67.8 * meas_height_m - 5.42))


# --- Radiation block --------------------------------------------------------
def inverse_relative_distance(julian_day: int) -> float:
    """dr, inverse relative Earth-Sun distance. FAO-56 eq. 23."""
    return 1 + 0.033 * math.cos(2 * math.pi / 365 * julian_day)


def solar_declination(julian_day: int) -> float:
    """delta, solar declination (rad). FAO-56 eq. 24."""
    return 0.409 * math.sin(2 * math.pi / 365 * julian_day - 1.39)


def sunset_hour_angle(lat_rad: float, decl_rad: float) -> float:
    """omega_s, sunset hour angle (rad). FAO-56 eq. 25."""
    return math.acos(-math.tan(lat_rad) * math.tan(decl_rad))


def daylight_hours(sunset_angle: float) -> float:
    """N, maximum daylight hours. FAO-56 eq. 34."""
    return 24 / math.pi * sunset_angle


def extraterrestrial_radiation(julian_day: int, lat_rad: float) -> float:
    """Ra, extraterrestrial radiation (MJ m-2 day-1). FAO-56 eq. 21."""
    dr = inverse_relative_distance(julian_day)
    decl = solar_declination(julian_day)
    ws = sunset_hour_angle(lat_rad, decl)
    return (
        (24 * 60 / math.pi)
        * SOLAR_CONSTANT
        * dr
        * (
            ws * math.sin(lat_rad) * math.sin(decl)
            + math.cos(lat_rad) * math.cos(decl) * math.sin(ws)
        )
    )


def clear_sky_radiation(ra: float, a_s: float = AS_COEF, b_s: float = BS_COEF) -> float:
    """Rso, clear-sky solar radiation using calibrated Angstrom coefficients.

    Rso = (a_s + b_s) * Ra  (FAO-56 eq. 36 with local calibration). This matches
    the reference workbook (a_s=0.25, b_s=0.50 -> 0.75*Ra).
    """
    return (a_s + b_s) * ra


def solar_radiation_from_sunshine(
    ra: float, sunshine_hours: float, max_daylight: float,
    a_s: float = AS_COEF, b_s: float = BS_COEF,
) -> float:
    """Rs from sunshine hours. FAO-56 eq. 35."""
    return (a_s + b_s * (sunshine_hours / max_daylight)) * ra


def net_shortwave(rs: float, albedo: float = ALBEDO_GRASS) -> float:
    """Rns = (1 - alpha) * Rs. FAO-56 eq. 38."""
    return (1 - albedo) * rs


def net_longwave(tmax_c: float, tmin_c: float, ea: float, rs: float, rso: float) -> float:
    """Rnl, net longwave radiation (MJ m-2 day-1). FAO-56 eq. 39."""
    tmax_k = tmax_c + 273.16
    tmin_k = tmin_c + 273.16
    cloud = 1.35 * min(rs / rso, 1.0) - 0.35  # cap Rs/Rso at 1
    return (
        STEFAN_BOLTZMANN
        * ((tmax_k ** 4 + tmin_k ** 4) / 2)
        * (0.34 - 0.14 * math.sqrt(max(ea, 0.0)))
        * cloud
    )


# --- Result container -------------------------------------------------------
@dataclass
class EToResult:
    eto: float
    # inputs echoed
    tmean: float
    # vapour pressure
    e_tmax: float
    e_tmin: float
    es: float
    ea: float
    vpd: float
    delta: float
    pressure: float
    gamma: float
    # radiation
    lat_rad: float
    decl: float
    sunset_angle: float
    daylight_hours: float
    dr: float
    ra: float
    rs: float
    rso: float
    rns: float
    rnl: float
    rn: float
    g: float
    u2: float

    def to_dict(self) -> dict:
        return asdict(self)


def compute_ea(e_tmax: float, e_tmin: float,
               rh_max: Optional[float], rh_min: Optional[float],
               rh_mean: Optional[float] = None) -> float:
    """Actual vapour pressure ea (kPa).

    Preference order (FAO-56 3.9):
      1. RHmax & RHmin  -> eq. 17
      2. RHmax only     -> eq. 18
      3. RHmean         -> eq. 19
    """
    if rh_max is not None and rh_min is not None:
        return (e_tmin * (rh_max / 100) + e_tmax * (rh_min / 100)) / 2
    if rh_max is not None:
        return e_tmin * (rh_max / 100)
    if rh_mean is not None:
        return (rh_mean / 100) * ((e_tmax + e_tmin) / 2)
    raise ValueError("At least one of RHmax/RHmin or RHmean is required for ea")


def compute_eto(
    *,
    julian_day: int,
    tmax_c: float,
    tmin_c: float,
    latitude_deg: float,
    elevation_m: float,
    wind_speed: float,
    wind_height_m: float = 2.0,
    rh_max: Optional[float] = None,
    rh_min: Optional[float] = None,
    rh_mean: Optional[float] = None,
    solar_rad: Optional[float] = None,
    sunshine_hours: Optional[float] = None,
    soil_heat_flux: float = 0.0,
    a_s: float = AS_COEF,
    b_s: float = BS_COEF,
    albedo: float = ALBEDO_GRASS,
) -> EToResult:
    """Compute daily reference ET (mm/day) via FAO-56 Penman-Monteith.

    `solar_rad` (measured Rs, MJ m-2 day-1) is used if given; otherwise Rs is
    estimated from `sunshine_hours`. One of the two must be supplied.
    """
    tmean = (tmax_c + tmin_c) / 2

    # Vapour pressure
    e_tmax = saturation_vapour_pressure(tmax_c)
    e_tmin = saturation_vapour_pressure(tmin_c)
    es = (e_tmax + e_tmin) / 2
    ea = compute_ea(e_tmax, e_tmin, rh_max, rh_min, rh_mean)
    vpd = es - ea
    delta = slope_svp(tmean)

    # Pressure / psychrometric
    pressure = atmospheric_pressure(elevation_m)
    gamma = psychrometric_constant(pressure)

    # Wind
    u2 = wind_speed_2m(wind_speed, wind_height_m)

    # Radiation
    lat_rad = math.radians(latitude_deg)
    decl = solar_declination(julian_day)
    ws = sunset_hour_angle(lat_rad, decl)
    n_hours = daylight_hours(ws)
    dr = inverse_relative_distance(julian_day)
    ra = extraterrestrial_radiation(julian_day, lat_rad)
    rso = clear_sky_radiation(ra, a_s, b_s)

    if solar_rad is not None:
        rs = solar_rad
    elif sunshine_hours is not None:
        rs = solar_radiation_from_sunshine(ra, sunshine_hours, n_hours, a_s, b_s)
    else:
        raise ValueError("Provide either solar_rad (Rs) or sunshine_hours")

    rns = net_shortwave(rs, albedo)
    rnl = net_longwave(tmax_c, tmin_c, ea, rs, rso)
    rn = rns - rnl

    # Penman-Monteith (FAO-56 eq. 6)
    numerator = (
        0.408 * delta * (rn - soil_heat_flux)
        + gamma * (900 / (tmean + 273)) * u2 * vpd
    )
    denominator = delta + gamma * (1 + 0.34 * u2)
    eto = numerator / denominator

    return EToResult(
        eto=eto, tmean=tmean, e_tmax=e_tmax, e_tmin=e_tmin, es=es, ea=ea,
        vpd=vpd, delta=delta, pressure=pressure, gamma=gamma, lat_rad=lat_rad,
        decl=decl, sunset_angle=ws, daylight_hours=n_hours, dr=dr, ra=ra,
        rs=rs, rso=rso, rns=rns, rnl=rnl, rn=rn, g=soil_heat_flux, u2=u2,
    )
