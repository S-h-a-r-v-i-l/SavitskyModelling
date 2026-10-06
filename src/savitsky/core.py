"""Single entry point: solve one hull at one speed.

`solve_single_point` wires together the five physics modules and returns a
fully populated `PlaningResult`. It is the only place in the library that
catches exceptions: the primitives raise loudly when a root does not exist,
and this function translates that into `ResultFlag.NO_SOLUTION` so a caller
sweeping thousands of hull variants never has to wrap calls in try/except.

Order of operations mirrors the paper's own procedure (Table 2):

1. Non-dimensionalise: Cv from speed and beam, CLbeta from load and speed.
2. Invert eq. (16) **once** for CL0 -- it depends on neither trim nor
   wetted length, which is why Table 1 carries a single CL0 across all
   three of its trim columns.
3. Root-find the trim at which the centre of pressure sits over the CG,
   eq. (37).
4. Evaluate everything else at that converged trim.

Keyword-only arguments throughout: there are a lot of same-typed floats
here and positional order would be easy to get wrong.
"""

import math

from .constants import FRESH_WATER, G, WaterProperties
from . import center_of_pressure, drag, equilibrium_simple, friction, geometry, lift
from .result import PlaningResult, ResultFlag


def solve_single_point(
    *,
    load: float,
    beam: float,
    lcg: float,
    deadrise_deg: float,
    speed: float,
    water: WaterProperties = FRESH_WATER,
    friction_line: friction.FrictionLine = friction.FrictionLine.SCHOENHERR,
    roughness_allowance: float = 0.0,
    gravity: float = G,
) -> PlaningResult:
    """Solve the planing equilibrium for one hull at one speed.

    Args:
        load: Weight carried by the water, newtons (mass * g).
        beam: Hull beam, metres.
        lcg: Longitudinal centre of gravity forward of the transom,
            measured along the keel, metres.
        deadrise_deg: Deadrise angle, degrees.
        speed: Forward speed, metres per second.
        water: Density and kinematic viscosity.
        friction_line: Schoenherr (what Savitsky used) or ITTC-57.
        roughness_allowance: dCf added to the smooth-surface Cf. The
            paper's examples use 0.0004 ("ATTC Standard Roughness");
            defaults to 0.0, i.e. hydraulically smooth.
        gravity: Acceleration due to gravity, m/s^2.

    Returns:
        A PlaningResult. Check `converged` and `flags` before trusting the
        numbers -- this function does not raise on unsolvable or
        out-of-envelope cases.
    """
    cv = speed / math.sqrt(gravity * beam)
    cl_beta = load / (0.5 * water.rho * speed**2 * beam**2)
    result = PlaningResult(cv=cv, cl_beta=cl_beta)

    try:
        cl0 = lift.solve_cl0_from_cl_beta(cl_beta, deadrise_deg)
        tau_deg = equilibrium_simple.solve_trim(cl0, cv, beam, lcg)
        lam = lift.solve_lambda_from_cl0(cl0, tau_deg, cv)
    except ValueError:
        result.flags |= ResultFlag.NO_SOLUTION
        return result

    # Record the balance point and its validity before evaluating the rest,
    # so that a trim found far outside the fitted envelope still reports
    # what it found even if the downstream physics then breaks down.
    keel_length, chine_length = geometry.wetted_lengths(
        lam, beam, tau_deg, deadrise_deg
    )
    result.tau_deg = tau_deg
    result.lam = lam
    result.Lk = keel_length
    result.Lc = chine_length
    result.draft = geometry.draft_from_keel_length(keel_length, tau_deg)
    result.Cp = center_of_pressure.center_of_pressure_ratio(lam, cv)
    result.lp = center_of_pressure.center_of_pressure_distance(lam, cv, beam)
    result.flags |= _validity_flags(tau_deg, lam, cv, chine_length)

    try:
        bottom_velocity = friction.average_bottom_velocity(
            speed, tau_deg, lam, deadrise_deg
        )
        reynolds = friction.reynolds_number(bottom_velocity, lam, beam, water.nu)
        friction_coefficient = friction.friction_coefficient(
            reynolds, line=friction_line, roughness_allowance=roughness_allowance
        )
        friction_force = drag.friction_drag(
            friction_coefficient, water.rho, bottom_velocity, lam, beam, deadrise_deg
        )
    except ValueError:
        # Eq. (24) can go imaginary at extreme trim with a tiny wetted
        # length. The trim is still reported above; the drag is not
        # computable, so this is not a converged answer.
        result.flags |= ResultFlag.NO_SOLUTION
        return result

    total = drag.total_drag(load, tau_deg, friction_force)
    result.converged = True
    result.V1 = bottom_velocity
    result.Cf = friction_coefficient
    result.Df = friction_force
    result.Dp = drag.pressure_drag(load, tau_deg)
    result.D = total
    result.effective_power = total * speed
    return result


def _validity_flags(
    tau_deg: float, lam: float, cv: float, chine_length: float
) -> ResultFlag:
    """Flag a converged solution that sits outside the method's envelope.

    The published limits on eq. (15) are 0.60 <= Cv <= 13.00,
    2 <= tau <= 15 deg and lambda <= 4. They constrain *outputs*, so they
    can only be checked after solving -- which is exactly why the result
    carries flags rather than the inputs being validated up front.

    A non-positive chine length means the chines never get wet, and the
    prismatic planing assumptions behind eq. (15)/(16) no longer hold.
    """
    flags = ResultFlag.NONE
    if not lift.TAU_MIN_DEG <= tau_deg <= lift.TAU_MAX_DEG:
        flags |= ResultFlag.OUT_OF_VALID_RANGE
    if lam > lift.LAMBDA_MAX:
        flags |= ResultFlag.OUT_OF_VALID_RANGE
    if not lift.CV_MIN <= cv <= lift.CV_MAX:
        flags |= ResultFlag.OUT_OF_VALID_RANGE
    if chine_length <= 0.0:
        flags |= ResultFlag.DRY_CHINES
    return flags
