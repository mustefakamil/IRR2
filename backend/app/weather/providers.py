"""Concrete climate-data providers."""
from __future__ import annotations

import os
import urllib.parse
from datetime import date, datetime

from .base import WeatherProvider, http_get_json, wind_10m_to_2m

_MISSING = -999


# --- NASA POWER -------------------------------------------------------------
class NasaPower(WeatherProvider):
    key = "nasa"
    label = "NASA POWER"
    priority = 1
    weight = 1.0
    note = "Global satellite/MERRA-2 daily data. No key required."

    def fetch(self, lat, lon, start: date, end: date) -> list[dict]:
        params = {
            "parameters": "T2M_MAX,T2M_MIN,RH2M,WS2M,ALLSKY_SFC_SW_DWN,PRECTOTCORR",
            "community": "AG", "latitude": lat, "longitude": lon,
            "start": start.strftime("%Y%m%d"), "end": end.strftime("%Y%m%d"),
            "format": "JSON",
        }
        url = "https://power.larc.nasa.gov/api/temporal/daily/point?" + urllib.parse.urlencode(params)
        data = http_get_json(url)
        p = data["properties"]["parameter"]
        units = {k: v.get("units", "") for k, v in data.get("parameters", {}).items()}
        solar_kwh = "kw" in units.get("ALLSKY_SFC_SW_DWN", "").lower()

        out = []
        for k in sorted(p["T2M_MAX"]):
            tmax, tmin = p["T2M_MAX"][k], p["T2M_MIN"][k]
            if tmax == _MISSING or tmin == _MISSING:
                continue
            rs = p["ALLSKY_SFC_SW_DWN"].get(k, _MISSING)
            rs = None if rs == _MISSING else (rs * 3.6 if solar_kwh else rs)
            rh = p["RH2M"].get(k, _MISSING)
            wind = p["WS2M"].get(k, _MISSING)
            rain = p["PRECTOTCORR"].get(k, _MISSING)
            out.append({
                "date": datetime.strptime(k, "%Y%m%d").date().isoformat(),
                "tmax": tmax, "tmin": tmin, "rh_max": None, "rh_min": None,
                "rh_mean": rh if rh != _MISSING else None,
                "wind": wind if wind != _MISSING else None,
                "rs": rs, "rainfall": rain if rain != _MISSING else 0.0,
            })
        return out


# --- Copernicus ERA5 (via Open-Meteo archive) -------------------------------
class Era5(WeatherProvider):
    key = "era5"
    label = "Copernicus ERA5"
    priority = 2
    weight = 1.0
    note = "ERA5 reanalysis served synchronously via the Open-Meteo archive."

    _URL = "https://archive-api.open-meteo.com/v1/archive"

    def fetch(self, lat, lon, start: date, end: date) -> list[dict]:
        daily = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum",
                 "wind_speed_10m_max", "shortwave_radiation_sum"]
        params = {
            "latitude": lat, "longitude": lon,
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "daily": ",".join(daily), "hourly": "relative_humidity_2m",
            "timezone": "auto", "wind_speed_unit": "ms",
        }
        data = http_get_json(self._URL + "?" + urllib.parse.urlencode(params))
        if data.get("error"):
            raise ValueError(data.get("reason", "ERA5/Open-Meteo error"))
        return _parse_open_meteo(data)


# --- Open-Meteo operational model (recent past + short forecast) -------------
class OpenMeteo(WeatherProvider):
    key = "open-meteo"
    label = "Open-Meteo (forecast model)"
    priority = 4
    weight = 0.8
    note = "Operational best-match model. Covers ~recent 3 months and forecast."

    _URL = "https://api.open-meteo.com/v1/forecast"

    def fetch(self, lat, lon, start: date, end: date) -> list[dict]:
        daily = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum",
                 "wind_speed_10m_max", "shortwave_radiation_sum"]
        params = {
            "latitude": lat, "longitude": lon,
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "daily": ",".join(daily), "hourly": "relative_humidity_2m",
            "timezone": "auto", "wind_speed_unit": "ms",
        }
        data = http_get_json(self._URL + "?" + urllib.parse.urlencode(params))
        if data.get("error"):
            raise ValueError(data.get("reason", "Open-Meteo error"))
        return _parse_open_meteo(data)


def _parse_open_meteo(data: dict) -> list[dict]:
    d = data["daily"]
    rh_by_day: dict[str, list[float]] = {}
    h = data.get("hourly", {})
    for t, rh in zip(h.get("time", []), h.get("relative_humidity_2m", [])):
        if rh is not None:
            rh_by_day.setdefault(t[:10], []).append(rh)
    out = []
    for i, day in enumerate(d["time"]):
        tmax, tmin = d["temperature_2m_max"][i], d["temperature_2m_min"][i]
        if tmax is None or tmin is None:
            continue
        rhs = rh_by_day.get(day)
        u10 = d["wind_speed_10m_max"][i]
        out.append({
            "date": day, "tmax": tmax, "tmin": tmin,
            "rh_max": max(rhs) if rhs else None,
            "rh_min": min(rhs) if rhs else None,
            "rh_mean": (sum(rhs) / len(rhs)) if rhs else None,
            "wind": wind_10m_to_2m(u10) if u10 is not None else None,
            "rs": d["shortwave_radiation_sum"][i],
            "rainfall": d["precipitation_sum"][i] if d["precipitation_sum"][i] is not None else 0.0,
        })
    return out


# --- NOAA Climate Data Online (station data; requires a free token) ---------
class NoaaCdo(WeatherProvider):
    key = "noaa"
    label = "NOAA CDO (GHCND)"
    priority = 3
    weight = 0.9
    requires_auth = True
    note = "Station-based daily Tmax/Tmin/precip. Set NOAA_TOKEN (free)."

    _BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2"

    def is_available(self) -> bool:
        return bool(os.environ.get("NOAA_TOKEN"))

    def fetch(self, lat, lon, start: date, end: date) -> list[dict]:
        token = os.environ.get("NOAA_TOKEN")
        if not token:
            raise ValueError("NOAA_TOKEN not configured")
        hdr = {"token": token}
        # nearest GHCND station within a ~1.5 deg box
        ext = f"{lat-0.75},{lon-0.75},{lat+0.75},{lon+0.75}"
        sq = urllib.parse.urlencode({
            "datasetid": "GHCND", "extent": ext, "limit": 25,
            "startdate": start.isoformat(), "enddate": end.isoformat(),
        })
        stations = http_get_json(f"{self._BASE}/stations?{sq}", hdr).get("results", [])
        if not stations:
            raise ValueError("No NOAA station near this location for the range")
        station = min(stations, key=lambda s: (s.get("latitude", 0) - lat) ** 2
                      + (s.get("longitude", 0) - lon) ** 2)
        dq = urllib.parse.urlencode({
            "datasetid": "GHCND", "stationid": station["id"],
            "datatypeid": "TMAX,TMIN,PRCP", "units": "metric",
            "startdate": start.isoformat(), "enddate": end.isoformat(), "limit": 1000,
        })
        rows = http_get_json(f"{self._BASE}/data?{dq}", hdr).get("results", [])
        by_day: dict[str, dict] = {}
        for r in rows:
            day = r["date"][:10]
            by_day.setdefault(day, {})[r["datatype"]] = r["value"]
        out = []
        for day, vals in sorted(by_day.items()):
            if "TMAX" not in vals or "TMIN" not in vals:
                continue
            out.append({
                "date": day, "tmax": vals["TMAX"], "tmin": vals["TMIN"],
                "rh_max": None, "rh_min": None, "rh_mean": None, "wind": None,
                "rs": None, "rainfall": vals.get("PRCP", 0.0),
            })
        return out


# --- FAO WaPOR (validation of actual ET; requires an API key) ---------------
class Wapor(WeatherProvider):
    key = "wapor"
    label = "FAO WaPOR (validation)"
    role = "validation"
    priority = 9
    requires_auth = True
    note = ("Remote-sensing actual ET for validation, not scheduling. "
            "Set WAPOR_APIKEY to enable.")

    def is_available(self) -> bool:
        return bool(os.environ.get("WAPOR_APIKEY"))

    def fetch(self, lat, lon, start: date, end: date) -> list[dict]:
        raise ValueError("WaPOR provides actual ET for validation, not daily "
                         "weather; use the validation endpoint instead.")
