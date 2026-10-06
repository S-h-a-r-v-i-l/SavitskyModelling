"""Simple-case trim equilibrium: eq. (37) of Savitsky (1964).

The simplest balance, and the one many small planing boats are close to:
thrust, viscous drag and the hydrodynamic normal force all pass through
the centre of gravity (a = c = f = epsilon = 0 in the general-case
notation). With no moment arms left, pitch equilibrium reduces to the
requirement that the resultant pressure force act *at* the CG:

    N = Delta/cos(tau)        and        lambda*Cp*b = LCG          (37)

Only the second is an equation in the unknown trim: lambda comes from the
lift relations at that trim ([[lift]]) and Cp from eq. (28)
([[center_of_pressure]]), so the whole thing collapses to a single
one-dimensional root-find in tau.

**The residual is strictly decreasing in tau**, so the root is unique and
bracketing is safe. Two competing effects both push the same way: raising
trim reduces the wetted length needed to carry the load (lambda falls),
and although that moves the centre of pressure forward as a *fraction*
of the wetted length (Cp rises toward 0.75), the product Cp*lambda still
falls. Differentiating eq. (28) confirms d(Cp*lambda)/d(lambda) stays
positive (minimum about 0.28) for every Cv, so lp is monotone in lambda
and lambda is monotone in tau. Hence no MULTIPLE_ROOTS case can arise
here -- that flag is for the general case of Batch 9, whose moment
equation has no such guarantee.
"""

import math

from scipy.optimize import brentq

from . import center_of_pressure, lift

# Upper end of the trim search. Far past the published 15 deg validity
# limit so that a hull balancing outside the fitted envelope still yields
# a number the caller can flag, rather than a failure.
TAU_SEARCH_MAX_DEG = 30.0


def minimum_feasible_trim(cl0: float, cv: float, lam_max: float = 10.0) -> float:
    """Lowest trim at which the required lambda is still within lam_max.

    Below this trim the hull would need more wetted length than
    `lift.solve_lambda_from_cl0` will search for, and that function raises.
    Since eq. (15) is simply proportional to tau**1.1, the boundary has a
    closed form -- no iteration needed:

        tau_min = [ CL0 / (0.0120*lam_max**0.5 + 0.0055*lam_max**2.5/Cv**2) ]**(1/1.1)

    Used to set the lower bracket so the residual is defined everywhere
    inside it.
    """
    denominator = 0.0120 * math.sqrt(lam_max) + 0.0055 * lam_max**2.5 / cv**2
    return (cl0 / denominator) ** (1.0 / 1.1)


def trim_residual(tau_deg: float, cl0: float, cv: float, beam: float, lcg: float) -> float:
    """Signed distance between the centre of pressure and the CG, in metres.

    Positive means the pressure force acts forward of the CG, which pitches
    the bow up and so drives trim up; negative means the reverse. Zero is
    eq. (37)'s equilibrium.
    """
    lam = lift.solve_lambda_from_cl0(cl0, tau_deg, cv)
    return center_of_pressure.center_of_pressure_distance(lam, cv, beam) - lcg


def solve_trim(cl0: float, cv: float, beam: float, lcg: float) -> float:
    """Equilibrium trim angle in degrees, eq. (37).

    Bracketed Brent search between `minimum_feasible_trim` and
    TAU_SEARCH_MAX_DEG. Raises ValueError if the residual does not change
    sign across that bracket, which is physically meaningful rather than a
    numerical failure:

    * residual still negative at the low end -- the CG is further forward
      than the centre of pressure can reach at any trim, so the bow cannot
      be held up;
    * residual still positive at the high end -- the CG is so far aft that
      the hull would have to trim past 30 degrees to balance.

    `core.solve_single_point` converts either into ResultFlag.NO_SOLUTION.
    """
    lower = minimum_feasible_trim(cl0, cv) * 1.0001  # stay inside the solvable side
    upper = TAU_SEARCH_MAX_DEG

    residual_lower = trim_residual(lower, cl0, cv, beam, lcg)
    residual_upper = trim_residual(upper, cl0, cv, beam, lcg)

    if residual_lower < 0.0:
        raise ValueError(
            f"LCG={lcg:g} m is forward of the furthest-forward centre of pressure "
            f"({lcg + residual_lower:g} m at tau={lower:g} deg); no trim balances this hull"
        )
    if residual_upper > 0.0:
        raise ValueError(
            f"LCG={lcg:g} m is aft of the centre of pressure even at "
            f"tau={upper:g} deg; no trim balances this hull"
        )

    return brentq(trim_residual, lower, upper, args=(cl0, cv, beam, lcg))
