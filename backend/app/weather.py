"""Fetch daily climate from NASA POWER and Open-Meteo (standard library only).

Both providers are normalised to the same daily record shape used by the
scheduling engine:
    {date, tmax, tmin, rh_max, rh_min, rh_mean, wind (m/s @2m), rs (MJ/m2/day), rainfall}
"""
from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from datetime import date, datetime

_TIMEOUT = 60
_MISSING = -999


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "FAO56-Irrigation/1.0"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode())


def _wind_10m_to_2m(u10: float) -> float:
    # FAO-56 eq. 47 for a 10 m measurement height
    return u10 * (4.87 / math.log(67.8 * 10 - 5.42))


# --- NASA POWER -------------------------------------------------------------
def fetch_nasa(lat: float, lon: float, start: date, end: date) -> list[dict]:
    params = {
        "parameters": "T2M_MAX,T2M_MIN,RH2M,WS2M,ALLSKY_SFC_SW_DWN,PRECTOTCORR",
        "community": "AG",
        "latitude": lat, "longitude": lon,
        "start": start.strftime("%Y%m%d"), "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }
    url = "https://power.larc.nasa.gov/api/temporal/daily/point?" + urllib.parse.urlencode(params)
    data = _get_json(url)
    p = data["properties"]["parameter"]
    units = {k: v.get("units", "") for k, v in data.get("parameters", {}).items()}
    solar_is_kwh = "kw" in units.get("ALLSKY_SFC_SW_DWN", "").lower()

    out = []
    for daykey in sorted(p["T2M_MAX"].keys()):
        tmax = p["T2M_MAX"][daykey]
        tmin = p["T2M_MIN"][daykey]
        if tmax == _MISSING or tmin == _MISSING:
            continue
        rs = p["ALLSKY_SFC_SW_DWN"].get(daykey, _MISSING)
        if rs == _MISSING:
            rs = None
        elif solar_is_kwh:
            rs = rs * 3.6  # kWh/m2/day -> MJ/m2/day
        rh = p["RH2M"].get(daykey, _MISSING)
        wind = p["WS2M"].get(daykey, _MISSING)
        rain = p["PRECTOTCORR"].get(daykey, _MISSING)
        out.append({
            "date": datetime.strptime(daykey, "%Y%m%d").date().isoformat(),
            "tmax": round(tmax, 2), "tmin": round(tmin, 2),
            "rh_max": None, "rh_min": None,
            "rh_mean": round(rh, 1) if rh != _MISSING else None,
            "wind": round(wind, 2) if wind != _MISSING else 2.0,
            "rs": round(rs, 2) if rs is not None else None,
            "rainfall": round(rain, 2) if rain != _MISSING else 0.0,
        })
    return out


# --- Open-Meteo -------------------------------------------------------------
def fetch_open_meteo(lat: float, lon: float, start: date, end: date) -> list[dict]:
    daily = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum",
             "wind_speed_10m_max", "shortwave_radiation_sum"]
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start.isoformat(), "end_date": end.isoformat(),
        "daily": ",".join(daily),
        "hourly": "relative_humidity_2m",
        "timezone": "auto", "wind_speed_unit": "ms",
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
    data = _get_json(url)
    if data.get("error"):
        raise ValueError(data.get("reason", "Open-Meteo error"))

    d = data["daily"]
    # aggregate hourly RH to daily max/min
    rh_by_day: dict[str, list[float]] = {}
    h = data.get("hourly", {})
    for t, rh in zip(h.get("time", []), h.get("relative_humidity_2m", [])):
        if rh is None:
            continue
        rh_by_day.setdefault(t[:10], []).append(rh)

    out = []
    for i, day in enumerate(d["time"]):
        tmax = d["temperature_2m_max"][i]
        tmin = d["temperature_2m_min"][i]
        if tmax is None or tmin is None:
            continue
        rhs = rh_by_day.get(day)
        u10 = d["wind_speed_10m_max"][i]
        out.append({
            "date": day, "tmax": round(tmax, 2), "tmin": round(tmin, 2),
            "rh_max": round(max(rhs), 1) if rhs else None,
            "rh_min": round(min(rhs), 1) if rhs else None,
            "rh_mean": round(sum(rhs) / len(rhs), 1) if rhs else None,
            "wind": round(_wind_10m_to_2m(u10), 2) if u10 is not None else 2.0,
            "rs": round(d["shortwave_radiation_sum"][i], 2)
                  if d["shortwave_radiation_sum"][i] is not None else None,
            "rainfall": round(d["precipitation_sum"][i], 2)
                        if d["precipitation_sum"][i] is not None else 0.0,
        })
    return out


PROVIDERS = {"nasa": fetch_nasa, "open-meteo": fetch_open_meteo}
