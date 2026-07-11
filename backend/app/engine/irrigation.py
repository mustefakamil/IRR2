"""Irrigation depth, volume and runtime engine (spec sections 16-20)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


def gross_depth(net_depth_mm: float, efficiency_pct: float,
                leaching_fraction: float = 0.0) -> float:
    """Gross irrigation depth (mm) = Dn / Ea, adjusted for leaching.

    Dg = Dn / ((1 - LR) * Ea).  With LR=0 this reduces to Dn/Ea (spec section 17).
    """
    ea = efficiency_pct / 100
    if ea <= 0:
        raise ValueError("Irrigation efficiency must be > 0")
    return net_depth_mm / ((1 - leaching_fraction) * ea)


def water_volume_m3(depth_mm: float, area_m2: float) -> float:
    """Water volume (m3) = depth(mm) * area(m2) / 1000. Spec section 19."""
    return depth_mm * area_m2 / 1000


@dataclass
class DripSystem:
    n_emitters: int
    emitter_flow_lph: float          # litres per hour per emitter

    @property
    def system_flow_lph(self) -> float:
        return self.n_emitters * self.emitter_flow_lph


def runtime_hours(volume_m3: float, system_flow_lph: float) -> Optional[float]:
    """Runtime (hours) = required volume (L) / system flow (L/h). Spec section 20."""
    if system_flow_lph <= 0:
        return None
    volume_litres = volume_m3 * 1000
    return volume_litres / system_flow_lph
