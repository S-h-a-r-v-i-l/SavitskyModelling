"""Structured result type for a single-point planing solve.

Design intent (see plan): a solve never raises on a physically awkward
case -- it returns a PlaningResult with `flags` set and whatever partial
numbers were computable, so a caller sweeping many hull variants can
filter afterwards instead of wrapping every call in try/except.
"""

from dataclasses import dataclass
from enum import Flag, auto


class ResultFlag(Flag):
    """Bit flags describing issues found while solving one hull/speed point."""

    NONE = 0
    NO_SOLUTION = auto()
    MULTIPLE_ROOTS = auto()
    DRY_CHINES = auto()
    OUT_OF_VALID_RANGE = auto()


@dataclass
class PlaningResult:
    """Result of solving the planing equilibrium for one hull at one speed.

    All fields default to None until the batch that computes them lands;
    `converged` and `flags` are always meaningful.
    """

    converged: bool = False
    flags: ResultFlag = ResultFlag.NONE

    # Equilibrium trim, degrees (eq. 37 simple case / eq. 35 general case).
    tau_deg: float | None = None

    # Mean wetted length-beam ratio (eq. 5) and wetted lengths (eq. 3, 4).
    lam: float | None = None
    Lk: float | None = None
    Lc: float | None = None

    # Center of pressure (eq. 28).
    Cp: float | None = None
    lp: float | None = None

    # Friction (eq. 19/25) and total drag (eq. 25).
    V1: float | None = None
    Cf: float | None = None
    Df: float | None = None
    Dp: float | None = None
    D: float | None = None

    # Effective horsepower, D * V.
    EHP: float | None = None
