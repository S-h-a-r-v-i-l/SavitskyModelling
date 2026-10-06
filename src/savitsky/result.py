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

    All physical fields default to None until computed; `converged` and
    `flags` are always meaningful. SI units throughout (N, m, m/s, W),
    angles in degrees.
    """

    converged: bool = False
    flags: ResultFlag = ResultFlag.NONE

    # Non-dimensional operating point, independent of the trim solve.
    cv: float | None = None  # speed coefficient, V/sqrt(g*b)
    cl_beta: float | None = None  # load coefficient, Delta/(0.5*rho*V^2*b^2)

    # Equilibrium trim, degrees (eq. 37 simple case / eq. 35 general case).
    tau_deg: float | None = None

    # Mean wetted length-beam ratio (eq. 5), wetted lengths (eq. 3, 4),
    # and the resulting transom draft.
    lam: float | None = None
    Lk: float | None = None
    Lc: float | None = None
    draft: float | None = None

    # Center of pressure (eq. 28).
    Cp: float | None = None
    lp: float | None = None

    # Friction (eq. 19/23/24) and drag components (eq. 17/25).
    V1: float | None = None
    Cf: float | None = None
    Df: float | None = None
    Dp: float | None = None
    D: float | None = None

    # Effective (towing) power, D * V, in watts. The paper's "EHP" is this
    # divided by 550 to get imperial horsepower.
    effective_power: float | None = None
