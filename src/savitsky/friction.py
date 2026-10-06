"""Frictional resistance inputs: friction lines and average bottom velocity.

Two different provenances live here, and the distinction matters for the
write-up:

* **Average bottom velocity V1** is Savitsky's, eq. (23)-(24) plus Fig. 14.
* **The friction lines themselves are NOT in the paper.** Savitsky cites
  Schoenherr (ref. [14]) for Cf but never restates the formula, and the
  roughness allowance is quoted in his worked example as a bare table
  value ("ATTC Standard Roughness", dCf = 0.0004) with no formula at all.
  Both are therefore implemented here as documented external standards,
  with the roughness allowance exposed as a plain caller-supplied number
  rather than an invented correlation.

Units: SI at the boundary (m, m/s, m^2/s). Angles in degrees; unlike
lift.py, this module *does* use trig (cos tau), so degrees are converted
to radians internally.
"""

import math
from enum import Enum

from scipy.optimize import brentq


class FrictionLine(Enum):
    """Which turbulent friction line to use for Cf."""

    SCHOENHERR = "schoenherr"
    ITTC57 = "ittc57"


def schoenherr_friction_coefficient(reynolds: float) -> float:
    """Schoenherr (ATTC 1947) turbulent friction coefficient.

    External standard, not from Savitsky -- the paper cites it as ref. [14]
    and reads values off a chart. Defined implicitly by

        0.242 / sqrt(Cf) = log10(Re * Cf)

    which has no closed-form solution, hence the bracketed Brent search.
    The residual is strictly decreasing in Cf (the left side falls, the
    right side rises), so the root in [1e-5, 1e-1] is unique.
    """
    if reynolds <= 0.0:
        raise ValueError(f"Reynolds number must be positive, got {reynolds:g}")

    def residual(cf: float) -> float:
        return 0.242 / math.sqrt(cf) - math.log10(reynolds * cf)

    return brentq(residual, 1e-5, 1e-1)


def ittc57_friction_coefficient(reynolds: float) -> float:
    """ITTC-57 model-ship correlation line.

    External standard, not from Savitsky; offered as the modern
    alternative to Schoenherr. Explicit, so no iteration needed:

        Cf = 0.075 / (log10(Re) - 2)**2
    """
    if reynolds <= 0.0:
        raise ValueError(f"Reynolds number must be positive, got {reynolds:g}")
    return 0.075 / (math.log10(reynolds) - 2.0) ** 2


def friction_coefficient(
    reynolds: float,
    line: FrictionLine = FrictionLine.SCHOENHERR,
    roughness_allowance: float = 0.0,
) -> float:
    """Total friction coefficient Cf + dCf for the selected friction line.

    Mirrors rows 7-9 of the paper's Table 1: a smooth-surface Cf, plus a
    flat roughness allowance added on top. Savitsky's worked examples use
    dCf = 0.0004, quoted as "ATTC Standard Roughness"; it is a lookup
    value in the paper, not a formula, so it stays a caller input here and
    defaults to zero (smooth).

    Schoenherr is the default because it is what Savitsky used -- choosing
    ITTC-57 will not reproduce his tables exactly.
    """
    if line is FrictionLine.SCHOENHERR:
        smooth = schoenherr_friction_coefficient(reynolds)
    else:
        smooth = ittc57_friction_coefficient(reynolds)
    return smooth + roughness_allowance


def _dynamic_lift_coefficient(tau_deg: float, lam: float, beta_deg: float) -> float:
    """Dynamic (non-buoyant) part of the lift coefficient, corrected for deadrise.

    Eq. (20) gives the zero-deadrise dynamic component
    CLd = 0.0120 * lambda**0.5 * tau**1.1. For a deadrise surface the paper
    says the average bottom velocity "is computed in an analogous manner
    using the lift coefficient for deadrise surfaces given by (16)"
    (p. 83), so eq. (16)'s correction is applied to that dynamic component.
    This is the f(beta) factor printed on Fig. 14.
    """
    flat = 0.0120 * math.sqrt(lam) * tau_deg**1.1
    return flat - 0.0065 * beta_deg * flat**0.60


def average_bottom_velocity_ratio(
    tau_deg: float, lam: float, beta_deg: float = 0.0
) -> float:
    """Ratio V1/V of mean velocity over the planing bottom to forward speed.

    Eq. (24) for zero deadrise:
        V1/V = sqrt( 1 - 0.0120*tau**1.1 / (lambda**0.5 * cos(tau)) )

    and the Fig. 14 generalisation, which multiplies that correction by
    f(beta) = CLd_beta / CLd (see _dynamic_lift_coefficient):
        V1/V = sqrt( 1 - CLd_beta / (lambda * cos(tau)) )

    V1 < V because the bottom pressure exceeds free-stream pressure;
    deadrise reduces the lift, hence the pressure, hence pushes V1 back up
    toward V -- which is why Fig. 14's higher-deadrise panels sit higher.

    Raises ValueError if the radicand goes negative, which only happens at
    physically absurd combinations (very high trim with a tiny wetted
    length) where the model has broken down anyway.
    """
    tau_rad = math.radians(tau_deg)
    radicand = 1.0 - _dynamic_lift_coefficient(tau_deg, lam, beta_deg) / (
        lam * math.cos(tau_rad)
    )
    if radicand < 0.0:
        raise ValueError(
            f"eq. (24) radicand is negative ({radicand:g}) at tau={tau_deg:g} deg, "
            f"lambda={lam:g}, beta={beta_deg:g} deg"
        )
    return math.sqrt(radicand)


def average_bottom_velocity(
    speed: float, tau_deg: float, lam: float, beta_deg: float = 0.0
) -> float:
    """Mean velocity over the planing bottom, V1 (m/s). Eq. (23)/(24)."""
    return speed * average_bottom_velocity_ratio(tau_deg, lam, beta_deg)


def reynolds_number(
    bottom_velocity: float, lam: float, beam: float, kinematic_viscosity: float
) -> float:
    """Reynolds number on the mean wetted length.

    Re = V1 * lambda * b / nu, as defined on p. 84. Note the length scale
    is the mean wetted length (lambda*b), not the beam, and the velocity
    is the bottom velocity V1, not the forward speed V.
    """
    return bottom_velocity * lam * beam / kinematic_viscosity
