"""Effective rainfall engine (spec section 13).

Four methods are supported. USDA-SCS and FAO formulas are monthly relations;
applied per-day they give a conservative daily estimate.
"""
from __future__ import annotations


def effective_rainfall(rainfall_mm: float, method: str = "usda_scs",
                       fixed_fraction: float = 0.8,
                       manual_value: float | None = None) -> float:
    """Return effective rainfall Pe (mm), never below 0 or above rainfall."""
    if rainfall_mm <= 0 and method != "manual":
        return 0.0
    method = method.lower()

    if method == "manual":
        return max(0.0, manual_value if manual_value is not None else 0.0)

    if method == "fixed":
        pe = fixed_fraction * rainfall_mm

    elif method == "fao":
        # FAO method (dependable rainfall)
        if rainfall_mm <= 75:
            pe = 0.6 * rainfall_mm - 10
        else:
            pe = 0.8 * rainfall_mm - 25

    else:  # usda_scs (default)
        if rainfall_mm <= 250:
            pe = rainfall_mm * (125 - 0.2 * rainfall_mm) / 125
        else:
            pe = 125 + 0.1 * rainfall_mm

    return max(0.0, min(pe, rainfall_mm))
