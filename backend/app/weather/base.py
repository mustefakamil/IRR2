"""Shared primitives for climate-data providers.

A daily record is a plain dict with these keys (any may be None if a provider
does not supply that parameter):
    date, tmax, tmin, rh_max, rh_min, rh_mean, wind (m/s @2m), rs (MJ/m2/day), rainfall
"""
from __future__ import annotations

import json
import math
import time
import urllib.error
import urllib.request
from datetime import date

# Parameters the merge engine understands
PARAMS = ["tmax", "tmin", "rh_max", "rh_min", "rh_mean", "wind", "rs", "rainfall"]

# Physically plausible ranges for quality control
RANGES = {
    "tmax": (-30.0, 60.0), "tmin": (-45.0, 55.0),
    "rh_max": (0.0, 100.0), "rh_min": (0.0, 100.0), "rh_mean": (0.0, 100.0),
    "wind": (0.0, 60.0), "rs": (0.0, 45.0), "rainfall": (0.0, 500.0),
}

# Absolute agreement tolerance used for outlier rejection when >=3 sources
ABS_TOL = {
    "tmax": 5.0, "tmin": 5.0, "rh_max": 20.0, "rh_min": 20.0, "rh_mean": 20.0,
    "wind": 3.0, "rs": 7.0, "rainfall": 12.0,
}

_UA = {"User-Agent": "FAO56-Irrigation/1.1 (+https://github.com/mustefakamil/IRR2)"}


def http_get_json(url: str, headers: dict | None = None,
                  retries: int = 3, timeout: int = 60) -> dict:
    """GET JSON with retries + exponential backoff on rate-limit / 5xx / timeout."""
    hdrs = {**_UA, **(headers or {})}
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    raise last  # pragma: no cover


def wind_10m_to_2m(u10: float) -> float:
    """FAO-56 Eq. 47 wind adjustment from a 10 m measurement height."""
    return u10 * (4.87 / math.log(67.8 * 10 - 5.42))


class WeatherProvider:
    """Base class for a climate-data source."""
    key: str = ""
    label: str = ""
    role: str = "driver"          # driver | validation
    priority: int = 99            # lower = preferred
    weight: float = 1.0           # reliability weight in the weighted average
    requires_auth: bool = False
    note: str = ""

    def is_available(self) -> bool:
        """Whether this provider can be used now (keys present, etc.)."""
        return True

    def fetch(self, lat: float, lon: float, start: date, end: date) -> list[dict]:
        raise NotImplementedError

    def info(self) -> dict:
        return {
            "key": self.key, "label": self.label, "role": self.role,
            "priority": self.priority, "weight": self.weight,
            "requires_auth": self.requires_auth, "available": self.is_available(),
            "note": self.note,
        }
