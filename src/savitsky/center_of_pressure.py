"""Centre of pressure: eq. (28) of Savitsky (1964).

Where along the wetted bottom the resultant hydrodynamic force N acts.
This is what closes the equilibrium loop: the hull balances when that
force lines up with the centre of gravity.

Eq. (28) blends the two contributions to lift, which act at different
places (p. 85):

* the **dynamic** part acts at 75% of the mean wetted length forward of
  the transom,
* the **buoyant** part at 33% forward of the transom.

The formula interpolates between them on Cv/lambda, and it collapses to
exactly those two values in the limits -- at high speed the dynamic part
dominates and Cp -> 0.75; as speed vanishes Cp -> 0.75 - 1/2.39 = 0.332.
Tests assert both limits.

No trig and no angles here: Cp depends only on the speed coefficient and
the wetted length-beam ratio. Trim enters only indirectly, through the
lambda that [[lift]] returns at that trim.
"""


def center_of_pressure_ratio(lam: float, cv: float) -> float:
    """Centre of pressure as a fraction of the mean wetted length.

    Eq. (28): Cp = lp/(lambda*b) = 0.75 - 1/(5.21*Cv**2/lambda**2 + 2.39)

    Measured forward of the transom. Ranges from 0.332 (all buoyant lift,
    vanishing speed) to 0.75 (all dynamic lift, high speed). Essentially
    independent of trim and deadrise, which is why the paper gets away
    with a single curve family.
    """
    return 0.75 - 1.0 / (5.21 * cv**2 / lam**2 + 2.39)


def center_of_pressure_distance(lam: float, cv: float, beam: float) -> float:
    """Distance of the centre of pressure forward of the transom, lp (m).

    lp = Cp * lambda * b, i.e. eq. (28) rearranged. This is the quantity
    the simple-case equilibrium (eq. 37) sets equal to the LCG.
    """
    return center_of_pressure_ratio(lam, cv) * lam * beam
