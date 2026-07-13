"""FAO WaPOR v3 actual evapotranspiration (AETI) client.

Reads the public L1-AETI-D dekadal Cloud-Optimized GeoTIFFs (global, 300 m,
mm/day) directly from Google Cloud Storage via GDAL /vsicurl windowed reads —
so only the bytes for a single pixel are fetched, not the whole global raster.

No API key is required (WaPOR v3 data is open access). rasterio/GDAL is an
optional dependency; if it is not installed, `is_ready()` returns False.
"""
from __future__ import annotations

import calendar
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

# COG access tuning for single-pixel reads
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
os.environ.setdefault("GDAL_HTTP_TIMEOUT", "30")
os.environ.setdefault("VSI_CACHE", "TRUE")

_COG = ("/vsicurl/https://storage.googleapis.com/fao-gismgr-wapor-3-data/DATA/"
        "WAPOR-3/MAPSET/{mapset}/WAPOR-3.{mapset}.{code}.tif")
_SCALE = 0.1          # Int16 raw * scale = mm/day
_NODATA = -9999
_MAX_DEKADS = 40      # safety cap (~13 months)

# WaPOR v3 actual-ET (AETI) dekadal levels available via the open API.
# L3 (20 m) is only published for a few specific irrigation schemes and is not
# available for this region, so L1/L2 are offered (L2 = finest here).
LEVELS = {
    "L2": {"mapset": "L2-AETI-D", "resolution": "L2 (100 m)"},
    "L1": {"mapset": "L1-AETI-D", "resolution": "L1 (300 m)"},
}
DEFAULT_LEVEL = "L2"


def is_ready() -> bool:
    try:
        import rasterio  # noqa: F401
        return True
    except Exception:
        return False


def _dekads_in_range(start: date, end: date):
    """Yield (code, dekad_start, dekad_end) for every dekad overlapping [start, end]."""
    year, month = start.year, start.month
    while date(year, month, 1) <= end:
        dim = calendar.monthrange(year, month)[1]
        spans = [(1, 10), (11, 20), (21, dim)]
        for i, (a, b) in enumerate(spans, start=1):
            d_start = date(year, month, a)
            d_end = date(year, month, b)
            if d_end >= start and d_start <= end:
                yield f"{year}-{month:02d}-D{i}", d_start, d_end
        month += 1
        if month > 12:
            month, year = 1, year + 1


def _read_pixel(code: str, lat: float, lon: float, mapset: str = "L1-AETI-D"):
    """Return AETI mm/day for one dekad at a point, or None if missing/nodata."""
    import rasterio
    from rasterio.windows import Window
    url = _COG.format(mapset=mapset, code=code)
    try:
        with rasterio.open(url) as ds:
            row, col = ds.index(lon, lat)
            if not (0 <= row < ds.height and 0 <= col < ds.width):
                return None
            raw = ds.read(1, window=Window(col, row, 1, 1))
            v = float(raw[0, 0])
            if v == _NODATA:
                return None
            return v * _SCALE
    except Exception:
        return None  # raster not published yet, network hiccup, etc.


def _read_series(lat, lon, dekads, mapset, max_workers):
    results: dict[str, float | None] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = {pool.submit(_read_pixel, code, lat, lon, mapset): code
                for code, ds, de in dekads}
        for fut in as_completed(futs):
            results[futs[fut]] = fut.result()
    return results


def actual_et(lat: float, lon: float, start: date, end: date,
              level: str = DEFAULT_LEVEL, max_workers: int = 6) -> dict:
    """Seasonal actual ET (AETI) at a point over [start, end].

    `level` is "L2" (100 m, finest here) or "L1" (300 m). If the requested level
    has no valid pixel at the point (e.g. outside its coverage), it falls back to
    the coarser level automatically. Returns total_mm, per-dekad series, coverage
    and the level/resolution actually used.
    """
    if not is_ready():
        raise RuntimeError("rasterio/GDAL not installed — WaPOR reads unavailable")

    dekads = list(_dekads_in_range(start, end))[:_MAX_DEKADS]
    if not dekads:
        raise ValueError("Empty date range")

    order = [level] + [lv for lv in ("L2", "L1") if lv != level]
    used_level = level
    results: dict[str, float | None] = {}
    for lv in order:
        if lv not in LEVELS:
            continue
        results = _read_series(lat, lon, dekads, LEVELS[lv]["mapset"], max_workers)
        used_level = lv
        if any(v is not None for v in results.values()):
            break  # this level has data at the point

    series = []
    total = 0.0
    found = 0
    for code, ds, de in dekads:
        mm_day = results.get(code)
        window_days = (min(de, end) - max(ds, start)).days + 1
        if mm_day is None:
            series.append({"dekad": code, "start": ds.isoformat(),
                           "days": window_days, "mm_day": None, "mm": None})
            continue
        mm = round(mm_day * window_days, 2)
        total += mm
        found += 1
        series.append({"dekad": code, "start": ds.isoformat(),
                       "days": window_days, "mm_day": round(mm_day, 2), "mm": mm})

    return {
        "total_mm": round(total, 1),
        "dekads_found": found,
        "dekads_expected": len(dekads),
        "series": series,
        "level": used_level,
        "resolution": LEVELS[used_level]["resolution"] + " dekadal AETI",
    }
