"""Multi-source climate aggregation.

Exposes a registry of providers and helpers to fetch from several sources,
run quality control, and merge them into one authoritative daily series.
"""
from __future__ import annotations

from datetime import date

from .base import WeatherProvider, PARAMS
from .providers import NasaPower, Era5, OpenMeteo, NoaaCdo, Wapor, ClimateNormals
from .merge import merge_records, summarise
from .provision import provision_season, climate_normals

# Registry (order = preference). Validation-role providers are excluded from merge.
REGISTRY: list[WeatherProvider] = [
    NasaPower(), Era5(), NoaaCdo(), OpenMeteo(), ClimateNormals(), Wapor(),
]
_BY_KEY = {p.key: p for p in REGISTRY}

# Legacy single-source map (used by the /fetch endpoint)
PROVIDERS = {p.key: p for p in REGISTRY if p.role == "driver"}


def list_providers() -> list[dict]:
    return [p.info() for p in REGISTRY]


def driver_providers(only_available: bool = True) -> list[WeatherProvider]:
    return [p for p in REGISTRY if p.role == "driver"
            and (p.is_available() if only_available else True)]


def fetch_single(source: str, lat: float, lon: float, start: date, end: date) -> list[dict]:
    prov = _BY_KEY.get(source)
    if not prov:
        raise KeyError(source)
    return _round_records(prov.fetch(lat, lon, start, end))


def _round_records(recs: list[dict]) -> list[dict]:
    out = []
    for r in recs:
        rr = {"date": r["date"]}
        for p in PARAMS:
            v = r.get(p)
            rr[p] = round(v, 2) if isinstance(v, (int, float)) else v
        out.append(rr)
    return out


def fetch_and_merge(lat: float, lon: float, start: date, end: date,
                    sources: list[str] | None = None) -> dict:
    """Fetch from all (or selected) available driver providers, QC + merge.

    Returns {merged, provenance, report, weights}. Providers that error out are
    recorded in the report and skipped — the merge proceeds with the rest.
    """
    providers = driver_providers(only_available=True)
    if sources:
        providers = [p for p in providers if p.key in sources]
    if not providers:
        raise ValueError("No climate providers available")

    by_provider: dict[str, list[dict]] = {}
    errors: dict[str, str] = {}
    weights: dict[str, float] = {}
    for p in providers:
        try:
            recs = p.fetch(lat, lon, start, end)
            if recs:
                by_provider[p.key] = recs
                weights[p.key] = p.weight
            else:
                errors[p.key] = "no data returned"
        except Exception as e:  # network / provider / range errors
            errors[p.key] = str(e)[:200]

    if not by_provider:
        raise ValueError("All climate sources failed: " +
                         "; ".join(f"{k}: {v}" for k, v in errors.items()))

    merged, provenance = merge_records(by_provider, weights)
    report = summarise(by_provider, provenance, errors)
    return {"merged": merged, "provenance": provenance, "report": report,
            "weights": weights}
