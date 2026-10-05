"""Planing lift: eq. (15)-(16) of Savitsky (1964).

The two empirical lift relations, plus the inversions the solver needs.

A trap worth stating plainly: **neither equation contains a trig
function**. Eq. (15) raises the trim angle in *degrees* to the power 1.1,
and eq. (16) multiplies the deadrise angle in *degrees* by a constant.
Converting either to radians here would be wrong. Radians are only needed
in the geometry, drag, and equilibrium modules, which do use trig.

Symbols (paper -> code):
    CL0     zero-deadrise (flat-plate) lift coefficient  -> cl0
    CLbeta  deadrise lift coefficient                    -> cl_beta
    lambda  mean wetted length-beam ratio                -> lam
    Cv      speed coefficient V/sqrt(g*b)                -> cv
    tau     trim angle, degrees                          -> tau_deg
    beta    deadrise angle, degrees                      -> beta_deg

Both lift coefficients are referred to the same quantity,
CL = load / (0.5 * rho * V**2 * b**2), so at equilibrium CLbeta is fixed
by the hull weight and speed alone.
"""

import math

from scipy.optimize import brentq

# Validity ranges stated with eq. (15), p. 79. Exported so the solver can
# raise OUT_OF_VALID_RANGE rather than re-hardcoding them.
CV_MIN = 0.60
CV_MAX = 13.00
TAU_MIN_DEG = 2.0
TAU_MAX_DEG = 15.0
LAMBDA_MAX = 4.0


def zero_deadrise_lift_coefficient(tau_deg: float, lam: float, cv: float) -> float:
    """Lift coefficient of a flat (zero-deadrise) planing surface.

    Eq. (15): CL0 = tau**1.1 * [ 0.0120*lambda**0.5 + 0.0055*lambda**2.5 / Cv**2 ]

    The first term is the dynamic contribution, the second the buoyant one;
    the buoyant term dies off as 1/Cv**2, which is why above Cv ~ 10 the
    paper reduces this to CL0 = 0.0120*lambda**0.5*tau**1.1 (p. 80).

    tau_deg is in DEGREES and is used as a plain power, not through any
    trig function. Published validity: 0.60 <= Cv <= 13.00,
    2 deg <= tau <= 15 deg, lambda <= 4. Documented, not enforced --
    flagging is the caller's job.
    """
    dynamic = 0.0120 * math.sqrt(lam)
    buoyant = 0.0055 * lam**2.5 / cv**2
    return tau_deg**1.1 * (dynamic + buoyant)


def deadrise_lift_coefficient(cl0: float, beta_deg: float) -> float:
    """Lift coefficient of a deadrise surface at the same tau, lambda, Cv.

    Eq. (16): CLbeta = CL0 - 0.0065 * beta * CL0**0.60

    Deadrise sweeps the stagnation line aft, reducing the stagnation
    pressure and so the lift, hence CLbeta < CL0 for beta > 0.
    beta_deg is in DEGREES, used directly as a multiplier.
    """
    return cl0 - 0.0065 * beta_deg * cl0**0.60


def _turning_point_cl0(beta_deg: float) -> float:
    """CL0 at which eq. (16) stops decreasing and starts increasing.

    d(CLbeta)/d(CL0) = 1 - 0.0039*beta*CL0**-0.4, which vanishes at
    CL0 = (0.0039*beta)**2.5. Below this point eq. (16) runs backwards
    (CLbeta falls as CL0 rises), so inverting it is only single-valued on
    the branch above. For beta = 10 deg the turning point is CL0 = 3e-4,
    far below any realistic planing loading.
    """
    return (0.0039 * beta_deg) ** 2.5


def solve_cl0_from_cl_beta(
    cl_beta: float, beta_deg: float, cl0_max: float = 1.0
) -> float:
    """Invert eq. (16): recover the flat-plate CL0 behind a deadrise CLbeta.

    This is the first step of the paper's own procedure -- Table 1 row 2
    reads CL0 off Fig. 11 once and reuses it at every trial trim, because
    eq. (16) depends on neither tau nor lambda.

    Solved with a bracketed Brent search on the increasing branch of
    eq. (16) (see _turning_point_cl0), so the root is unique.

    Raises ValueError if no root exists in [turning point, cl0_max]; the
    caller (core.solve_single_point) turns that into ResultFlag.NO_SOLUTION
    rather than letting it escape.
    """
    if beta_deg == 0.0:
        return cl_beta  # eq. (16) degenerates to CLbeta = CL0

    lower = _turning_point_cl0(beta_deg)
    residual_lower = deadrise_lift_coefficient(lower, beta_deg) - cl_beta
    residual_upper = deadrise_lift_coefficient(cl0_max, beta_deg) - cl_beta

    if residual_lower > 0.0:
        raise ValueError(
            f"CLbeta={cl_beta:g} is below the minimum eq. (16) can produce "
            f"at beta={beta_deg:g} deg "
            f"({deadrise_lift_coefficient(lower, beta_deg):g})"
        )
    if residual_upper < 0.0:
        raise ValueError(
            f"CLbeta={cl_beta:g} needs CL0 above cl0_max={cl0_max:g} "
            f"at beta={beta_deg:g} deg"
        )
    return brentq(
        lambda cl0: deadrise_lift_coefficient(cl0, beta_deg) - cl_beta,
        lower,
        cl0_max,
    )


def solve_lambda_from_cl0(
    cl0: float, tau_deg: float, cv: float, lam_max: float = 10.0
) -> float:
    """Invert eq. (15) for the mean wetted length-beam ratio lambda.

    Eq. (15) is strictly increasing in lambda for lambda > 0 -- its
    derivative 0.0060*lambda**-0.5 + 0.01375*lambda**1.5/Cv**2 is
    positive -- and is zero at lambda = 0, so [0, lam_max] brackets
    exactly one root and there is no multiple-root case to worry about.

    lam_max defaults to 10, well past eq. (15)'s published lambda <= 4
    validity limit, deliberately: a hull needing lambda > 4 should come
    back with a usable number the caller can flag OUT_OF_VALID_RANGE,
    rather than a hard failure that would punch a discontinuity in the
    trim residual the Batch 7 solver is root-finding across.

    Raises ValueError if cl0 is non-positive or exceeds what lam_max can
    deliver; core.solve_single_point converts that to NO_SOLUTION.
    """
    if cl0 <= 0.0:
        raise ValueError(f"cl0 must be positive, got {cl0:g}")

    cl0_at_max = zero_deadrise_lift_coefficient(tau_deg, lam_max, cv)
    if cl0 > cl0_at_max:
        raise ValueError(
            f"CL0={cl0:g} exceeds the maximum {cl0_at_max:g} reachable at "
            f"lambda={lam_max:g}, tau={tau_deg:g} deg, Cv={cv:g}"
        )
    return brentq(
        lambda lam: zero_deadrise_lift_coefficient(tau_deg, lam, cv) - cl0,
        0.0,
        lam_max,
    )
