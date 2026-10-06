# `src/savitsky/center_of_pressure.py`

**Summary.** Where along the wetted bottom the resultant hydrodynamic
force acts. Public functions: `center_of_pressure_ratio(lam, cv)` (Cp, a
fraction of the mean wetted length) and
`center_of_pressure_distance(lam, cv, beam)` (lp, metres forward of the
transom).

**Equation(s).**
- (28): `Cp = lp/(lambda*b) = 0.75 - 1/(5.21*Cv^2/lambda^2 + 2.39)`

**Role in the model.** This is what closes the equilibrium loop. The hull
balances when the hydrodynamic force lines up with the centre of gravity,
so the simple case (eq. 37, Batch 7) root-finds the trim at which
`lp == LCG`. In the general case (Batch 9) lp instead sets the moment arm
`c = LCG - lp` in eq. (31). Depends only on Cv and the lambda that
[[lift]] returns; trim and deadrise enter only indirectly, which is why the
paper gets away with a single family of curves in Fig. 17.

**Why the constants are what they are.** Eq. (28) interpolates between the
two lift components, which act at different places (p. 85): the dynamic
part at **75%** of the mean wetted length forward of the transom, the
buoyant part at **33%**. The formula collapses to exactly those values in
the limits -- `Cv -> inf` gives 0.75, `Cv -> 0` gives
`0.75 - 1/2.39 = 0.332` -- so the two leading constants are not free
parameters but the physical endpoints. Tests assert both limits, which is
stronger evidence than any chart read, since the percentages come from the
paper's prose rather than from the formula itself.

**No chart-read tests here, deliberately.** Fig. 17 is simply a plot of
eq. (28) with the equation printed on it, so reading points off it would
test nothing new. The numerical checks come from Table 2's internal
cross-check instead (it fixes lp/b = LCG/b = 2.07 at lambda = 3.45, which
implies Cp = 0.600 with no chart involved) and from Table 1 row 17, which
*is* a Fig. 17 read and so is given a looser tolerance.

**Status.** Implemented and validated (Batch 6). 12 tests in
`tests/test_center_of_pressure.py`: both asymptotic limits exact; Table 2's
implied Cp = 0.600 reproduced as 0.6033 (+0.5%), and its LCG recovered to
within 1% by `center_of_pressure_distance`; Table 1 row 17 within 1.4%
(-1.39% / +0.28% / -0.97%, Fig. 17 chart reads). Monotonic trends checked
in both Cv and lambda.
