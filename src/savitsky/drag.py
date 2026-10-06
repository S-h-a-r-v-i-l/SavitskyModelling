"""Planing drag: eq. (17)-(19) and (25)-(27) of Savitsky (1964).

Total drag has two parts, and at the shallow trims a planing boat runs at
they are of comparable size (the paper notes they are about equal at
tau = 4 deg for a flat bottom, p. 85):

* **Pressure drag**, eq. (17). The hydrodynamic force N acts normal to the
  bottom; with the bottom inclined at the trim angle, its component along
  the direction of travel is `Delta*tan(tau)`. Note this depends only on
  load and trim -- no speed, no wetted area, no friction line.
* **Friction drag**, eq. (19). Shear along the wetted bottom, which acts
  parallel to the keel and so is divided by cos(tau) to resolve it into
  the horizontal direction, eq. (18).

Wetted area convention: eq. (19) uses `lambda*b^2/cos(beta)` -- the
projected pressure area `lambda*b^2` divided by cos(beta) to get true
surface area on the inclined V-bottom. Savitsky explicitly recommends
using the pressure area alone, with no spray-area addition, at trims
below 4 deg (p. 83), and Tables 1 and 2 do so at every trim. We follow the
tables.

Units: SI throughout (N, kg/m^3, m/s, m). Angles in degrees, converted to
radians internally -- this module does use trig.
"""

import math


def pressure_drag(load: float, tau_deg: float) -> float:
    """Drag component from the pressure force on the inclined bottom.

    Eq. (17): Dp = Delta * tan(tau)

    Independent of speed and wetted area: for a given weight, trim alone
    fixes it. This is the term that makes high trim expensive.
    """
    return load * math.tan(math.radians(tau_deg))


def friction_drag(
    friction_coefficient: float,
    density: float,
    bottom_velocity: float,
    lam: float,
    beam: float,
    beta_deg: float,
) -> float:
    """Viscous shear drag along the wetted bottom, acting parallel to the keel.

    Eq. (19): Df = Cf * rho * V1**2 * (lambda*b**2) / (2*cos(beta))

    `friction_coefficient` should already include any roughness allowance
    (friction.friction_coefficient returns Cf + dCf). `bottom_velocity` is
    V1 from eq. (23)/(24), not the forward speed V.

    The cos(beta) divisor converts the projected pressure area lambda*b**2
    into actual wetted surface area on the V-bottom.
    """
    wetted_area = lam * beam**2 / math.cos(math.radians(beta_deg))
    return 0.5 * friction_coefficient * density * bottom_velocity**2 * wetted_area


def total_drag(load: float, tau_deg: float, friction_drag_force: float) -> float:
    """Total horizontal drag.

    Eq. (18): D = Delta*tan(tau) + Df/cos(tau)

    Substituting eq. (19) for Df gives the paper's combined eq. (25):
        D = Delta*tan(tau) + rho*V1**2*Cf*lambda*b**2 / (2*cos(beta)*cos(tau))

    The 1/cos(tau) resolves the keel-parallel friction force into the
    horizontal direction.
    """
    tau_rad = math.radians(tau_deg)
    return load * math.tan(tau_rad) + friction_drag_force / math.cos(tau_rad)


def drag_lift_ratio(
    load: float, tau_deg: float, friction_drag_force: float
) -> float:
    """Drag-lift ratio D/Delta.

    Eq. (26): D/Delta = tan(tau) + rho*V1**2*Cf*lambda*b**2/(2*Delta*cos(beta)*cos(tau))

    Eq. (27) is the same quantity rewritten in coefficient form,
    `tan(tau) + (V1/V)**2 * Cf * lambda / (CL*cos(tau)*cos(beta))`, which
    is algebraically identical once CL = 2*Delta/(rho*V**2*b**2) is
    substituted -- a test asserts that equivalence rather than duplicating
    the formula here.

    This is the inverse of lift-to-drag efficiency: a planing hull at its
    best trim runs around 0.12-0.18.
    """
    return total_drag(load, tau_deg, friction_drag_force) / load
