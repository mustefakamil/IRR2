"""Soil water storage engine (FAO-56 Chapter 8)."""
from __future__ import annotations


def total_available_water(theta_fc: float, theta_wp: float, root_depth_m: float) -> float:
    """TAW (mm) = 1000 * (theta_FC - theta_WP) * Zr. FAO-56 eq. 82.

    theta values are volumetric fractions (0-1); root depth in metres.
    """
    return 1000 * (theta_fc - theta_wp) * root_depth_m


def adjusted_depletion_fraction(p_table: float, etc: float,
                                lower: float = 0.1, upper: float = 0.8) -> float:
    """p adjusted for ET rate: p = p_table + 0.04*(5 - ETc). FAO-56 eq. (table 22 note).

    Bounded to the recommended [0.1, 0.8] range.
    """
    p_adj = p_table + 0.04 * (5 - etc)
    return max(lower, min(upper, p_adj))


def readily_available_water(p: float, taw: float) -> float:
    """RAW (mm) = p * TAW. FAO-56 eq. 83."""
    return p * taw
