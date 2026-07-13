"""Climate provisioning: guarantee a full daily climate series for any season.

Strategy (hybrid, never fails):
  * baseline  = long-term monthly **climate normals** (NASA POWER climatology,
    the CLIMWAT-equivalent) expanded to daily — works for past OR future dates.
  * overlay actual historical data (NASA POWER) on past days.
  * overlay near-future **forecast** (Open-Meteo) on the coming days.

So past days use observed data, the next ~2 weeks use forecast, and the rest of
a future season falls back to climate normals — a schedule is always available.
"""
from __future__ import annotations

import calendar
from datetime import date, timedelta

from .base import http_get_json
from .providers import NasaPower, OpenMeteo, _MISSING

_MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def climate_normals(lat: float, lon: float) -> dict[int, dict]:
    """Long-term monthly normals -> {month(1-12): {tmax,tmin,rh_mean,wind,rs,rainfall}}."""
    import urllib.parse
    params = {
        "parameters": "T2M_MAX,T2M_MIN,RH2M,WS2M,ALLSKY_SFC_SW_DWN,PRECTOTCORR",
        "community": "AG", "latitude": lat, "longitude": lon, "format": "JSON",
    }
    url = "https://power.larc.nasa.gov/api/temporal/climatology/point?" + urllib.parse.urlencode(params)
    data = http_get_json(url)
    p = data["properties"]["parameter"]
    units = {k: v.get("units", "") for k, v in data.get("parameters", {}).items()}
    solar_kwh = "kw" in units.get("ALLSKY_SFC_SW_DWN", "").lower()

    normals: dict[int, dict] = {}
    for i, m in enumerate(_MONTHS, start=1):
        rs = p["ALLSKY_SFC_SW_DWN"].get(m)
        normals[i] = {
            "tmax": p["T2M_MAX"].get(m), "tmin": p["T2M_MIN"].get(m),
            "rh_mean": p["RH2M"].get(m), "wind": p["WS2M"].get(m),
            "rs": (rs * 3.6 if solar_kwh and rs is not None else rs),
            "rainfall": p["PRECTOTCORR"].get(m),  # mm/day (monthly average)
        }
    return normals


def _expand_normals(normals: dict[int, dict], start: date, end: date) -> dict[str, dict]:
    out: dict[str, dict] = {}
    d = start
    while d <= end:
        n = normals.get(d.month, {})
        out[d.isoformat()] = {
            "date": d.isoformat(), "tmax": _r(n.get("tmax")), "tmin": _r(n.get("tmin")),
            "rh_max": None, "rh_min": None, "rh_mean": _r(n.get("rh_mean")),
            "wind": _r(n.get("wind")) or 2.0, "rs": _r(n.get("rs")),
            "rainfall": _r(n.get("rainfall")) or 0.0, "source": "normals",
        }
        d += timedelta(days=1)
    return out


def _r(v):
    return round(v, 2) if isinstance(v, (int, float)) and v != _MISSING else (None if v == _MISSING else v)


def provision_season(lat: float, lon: float, start: date, end: date) -> dict:
    """Build a guaranteed daily series for [start, end]. Returns {records, report}."""
    # cap extremely long ranges
    if (end - start).days > 400:
        end = start + timedelta(days=400)

    by_date = _expand_normals(climate_normals(lat, lon), start, end)
    today = date.today()

    # overlay observed history
    hist_end = min(end, today - timedelta(days=2))
    if start <= hist_end:
        try:
            for r in NasaPower().fetch(lat, lon, start, hist_end):
                if r["date"] in by_date:
                    by_date[r["date"]] = {**_norm_row(r), "source": "nasa"}
        except Exception:
            pass

    # overlay near-term forecast
    fc_start = max(start, today - timedelta(days=5))
    fc_end = min(end, today + timedelta(days=15))
    if fc_start <= fc_end:
        try:
            for r in OpenMeteo().fetch(lat, lon, fc_start, fc_end):
                if r["date"] in by_date:
                    by_date[r["date"]] = {**_norm_row(r), "source": "forecast"}
        except Exception:
            pass

    records = [by_date[d] for d in sorted(by_date)]
    counts: dict[str, int] = {}
    for r in records:
        counts[r["source"]] = counts.get(r["source"], 0) + 1
    return {
        "records": records,
        "report": {"total_days": len(records), "by_source": counts,
                   "start": start.isoformat(), "end": end.isoformat()},
    }


def _norm_row(r: dict) -> dict:
    return {
        "date": r["date"], "tmax": _r(r.get("tmax")), "tmin": _r(r.get("tmin")),
        "rh_max": _r(r.get("rh_max")), "rh_min": _r(r.get("rh_min")),
        "rh_mean": _r(r.get("rh_mean")), "wind": _r(r.get("wind")) or 2.0,
        "rs": _r(r.get("rs")), "rainfall": _r(r.get("rainfall")) or 0.0,
    }
