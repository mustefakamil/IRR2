"""Quality control + multi-source merge.

For every date and parameter, values from the available providers are:
  1. range-checked (physically plausible),
  2. outlier-rejected against the median when >=3 sources agree-ish,
  3. combined with a weight = provider reliability,
producing a merged series plus provenance (which sources contributed and the
spread between them).
"""
from __future__ import annotations

import statistics

from .base import PARAMS, RANGES, ABS_TOL


def qc_ok(param: str, value) -> bool:
    if value is None:
        return False
    lo, hi = RANGES[param]
    return lo <= value <= hi


def merge_records(by_provider: dict[str, list[dict]],
                  weights: dict[str, float]) -> tuple[list[dict], list[dict]]:
    """Return (merged_records, provenance)."""
    # index[date][param] = [(provider, value), ...]
    index: dict[str, dict[str, list[tuple[str, float]]]] = {}
    for prov, recs in by_provider.items():
        for rec in recs:
            d = rec["date"]
            for p in PARAMS:
                v = rec.get(p)
                if qc_ok(p, v):
                    index.setdefault(d, {}).setdefault(p, []).append((prov, float(v)))

    merged: list[dict] = []
    provenance: list[dict] = []
    for d in sorted(index):
        rec = {"date": d}
        info: dict[str, dict] = {}
        for p in PARAMS:
            cands = index[d].get(p, [])
            if not cands:
                rec[p] = None
                continue
            vals = [v for _, v in cands]
            if len(vals) == 1:
                rec[p] = round(vals[0], 2)
                info[p] = {"n": 1, "sources": [cands[0][0]], "spread": 0.0}
                continue
            med = statistics.median(vals)
            surv = cands
            if len(vals) >= 3:
                sd = statistics.pstdev(vals)
                tol = max(ABS_TOL[p], 2 * sd)
                filtered = [(pr, v) for pr, v in cands if abs(v - med) <= tol]
                if filtered:
                    surv = filtered
            num = sum(weights.get(pr, 1.0) * v for pr, v in surv)
            den = sum(weights.get(pr, 1.0) for pr, v in surv)
            svals = [v for _, v in surv]
            rec[p] = round(num / den, 2)
            info[p] = {"n": len(surv), "sources": [pr for pr, _ in surv],
                       "spread": round(max(svals) - min(svals), 2)}
        # keep Tmax >= Tmin after merging
        if rec.get("tmax") is not None and rec.get("tmin") is not None \
                and rec["tmax"] < rec["tmin"]:
            rec["tmax"], rec["tmin"] = rec["tmin"], rec["tmax"]
        merged.append(rec)
        provenance.append({"date": d, "params": info})
    return merged, provenance


def summarise(by_provider: dict[str, list[dict]], provenance: list[dict],
              errors: dict[str, str]) -> dict:
    """Human-friendly report of source contributions and agreement."""
    sources = []
    for prov, recs in by_provider.items():
        sources.append({"key": prov, "days": len(recs), "status": "ok"})
    for prov, msg in errors.items():
        sources.append({"key": prov, "days": 0, "status": "error", "error": msg})

    # per-parameter average number of sources and average spread
    param_stats: dict[str, dict] = {}
    for p in PARAMS:
        ns, spreads = [], []
        for day in provenance:
            if p in day["params"]:
                ns.append(day["params"][p]["n"])
                spreads.append(day["params"][p]["spread"])
        if ns:
            param_stats[p] = {
                "avg_sources": round(sum(ns) / len(ns), 2),
                "avg_spread": round(sum(spreads) / len(spreads), 2),
            }
    return {"sources": sources, "parameters": param_stats}
