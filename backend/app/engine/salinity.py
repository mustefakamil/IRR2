"""Salinity / leaching-requirement engine (FAO-56 Chapter 5, Ayers & Westcot)."""
from __future__ import annotations


def leaching_requirement(ecw: float, ece: float) -> float:
    """LR (fraction) = ECw / (5*ECe - ECw). FAO-56 / Ayers & Westcot eq.

    ecw  = electrical conductivity of irrigation water (dS/m)
    ece  = tolerable soil-saturation-extract EC for the crop (dS/m)
    Requires 5*ECe > ECw (validation handled by caller).
    """
    denom = 5 * ece - ecw
    if denom <= 0:
        raise ValueError("Invalid leaching inputs: 5*ECe must exceed ECw")
    return ecw / denom
