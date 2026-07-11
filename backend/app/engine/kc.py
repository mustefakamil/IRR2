"""Crop coefficient (Kc) and growth-stage engine (FAO-56 Chapter 6).

Kc follows the classic four-stage curve:
  * initial      -> Kc = Kc_ini            (constant)
  * development  -> Kc_ini -> Kc_mid        (linear interpolation)
  * mid-season   -> Kc = Kc_mid            (constant)
  * late season  -> Kc_mid -> Kc_end        (linear interpolation)

Root depth grows linearly from a minimum at planting to the maximum by the end
of the development stage, then stays constant (FAO-56 practice).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


STAGE_INITIAL = "initial"
STAGE_DEVELOPMENT = "development"
STAGE_MID = "mid"
STAGE_LATE = "late"
STAGE_END = "end"


@dataclass
class CropStageParams:
    l_ini: int          # length of initial stage (days)
    l_dev: int          # development
    l_mid: int          # mid-season
    l_late: int         # late season
    kc_ini: float
    kc_mid: float
    kc_end: float
    zr_min: float       # minimum (planting) root depth (m)
    zr_max: float       # maximum root depth (m)
    depletion_fraction: float  # p (table value)
    height: float = 1.0        # crop height (m)

    @property
    def season_length(self) -> int:
        return self.l_ini + self.l_dev + self.l_mid + self.l_late


@dataclass
class DailyCropState:
    stage: str
    kc: Optional[float]
    root_depth: Optional[float]


def stage_for_day(dap: int, p: CropStageParams) -> str:
    """Growth stage for a given day-after-planting (1-based)."""
    if dap <= p.l_ini:
        return STAGE_INITIAL
    if dap <= p.l_ini + p.l_dev:
        return STAGE_DEVELOPMENT
    if dap <= p.l_ini + p.l_dev + p.l_mid:
        return STAGE_MID
    if dap <= p.season_length:
        return STAGE_LATE
    return STAGE_END


def kc_for_day(dap: int, p: CropStageParams) -> Optional[float]:
    """Daily Kc with linear interpolation over development and late stages."""
    stage = stage_for_day(dap, p)
    if stage == STAGE_INITIAL:
        return p.kc_ini
    if stage == STAGE_DEVELOPMENT:
        frac = (dap - p.l_ini) / p.l_dev if p.l_dev else 1.0
        return p.kc_ini + frac * (p.kc_mid - p.kc_ini)
    if stage == STAGE_MID:
        return p.kc_mid
    if stage == STAGE_LATE:
        days_into_late = dap - (p.l_ini + p.l_dev + p.l_mid)
        frac = days_into_late / p.l_late if p.l_late else 1.0
        return p.kc_mid + frac * (p.kc_end - p.kc_mid)
    return None


def root_depth_for_day(dap: int, p: CropStageParams) -> Optional[float]:
    """Daily root depth (m). Grows linearly to Zr_max by end of development."""
    if stage_for_day(dap, p) == STAGE_END:
        return None
    grow_days = p.l_ini + p.l_dev
    if dap >= grow_days or grow_days == 0:
        return p.zr_max
    frac = dap / grow_days
    return p.zr_min + frac * (p.zr_max - p.zr_min)


def crop_state_for_day(dap: int, p: CropStageParams) -> DailyCropState:
    return DailyCropState(
        stage=stage_for_day(dap, p),
        kc=kc_for_day(dap, p),
        root_depth=root_depth_for_day(dap, p),
    )
