# `src/savitsky/equilibrium_simple.py`

**Summary.** Finds the trim angle a hull actually settles at, for the
simple case where thrust, viscous drag and the hydrodynamic normal force
all pass through the CG. Public functions: `solve_trim(cl0, cv, beam,
lcg)`, plus `trim_residual(...)` and `minimum_feasible_trim(...)` which it
uses and which are independently testable.

**Equation(s).**
- (37): `N = Delta/cos(tau)` and `lambda*Cp*b = LCG`. Only the second is an
  equation in the unknown trim; it says the resultant pressure force must
  act *at* the CG, since with every moment arm zero there is nothing else
  to balance a pitching moment.

**Role in the model.** Called by `core.solve_single_point`. Everything
else in the library computes quantities *at a given trim*; this is the
module that works out what the trim is. lambda comes from [[lift]] at each
trial trim, Cp from [[center_of_pressure]], so the whole balance collapses
to a 1-D root-find in tau.

**Why the root is unique.** The residual `lp(tau) - LCG` is **strictly
decreasing** in tau, so a single bracketed Brent search is provably safe.
Raising trim reduces the wetted length needed to carry the load (lambda
falls), and although that moves the centre of pressure forward as a
*fraction* of wetted length (Cp rises toward 0.75), the product
`Cp*lambda` still falls: differentiating eq. (28) gives
`d(Cp*lambda)/d(lambda) = 0.75 - (15.63*u + 2.39*u^2)/(5.21 + 2.39*u)^2`
with `u = lambda^2/Cv^2`, which stays positive (minimum about 0.28) for
all u. **No MULTIPLE_ROOTS case can arise here** -- that flag exists for
Batch 9, whose moment equation carries no such guarantee.

**Bracketing.** The lower end is `minimum_feasible_trim`, the closed-form
trim at which the required lambda equals the lift module's search ceiling;
below it `lift.solve_lambda_from_cl0` has no root and would raise, so the
residual would be undefined. Since eq. (15) is simply proportional to
`tau^1.1`, that boundary inverts directly with no iteration. The upper end
is 30 deg, well past the published 15 deg limit, so a hull balancing
outside the fitted envelope still returns a flaggable number.

**Failure modes are physical, not numerical.** `solve_trim` raises
ValueError when the residual does not change sign, and both cases mean
something real: the CG is forward of anywhere the centre of pressure can
reach (the bow cannot be held up), or so far aft that the hull would have
to trim past 30 deg. `core.solve_single_point` converts either into
`ResultFlag.NO_SOLUTION`.

**Status.** Implemented and validated (Batch 7). 11 tests in
`tests/test_equilibrium_simple.py`, plus the end-to-end reproduction in
`tests/test_core.py`. Monotonicity of the residual is asserted directly,
as is the eq. (37) condition itself (lp == LCG at the converged trim) and
the trend that moving the CG aft raises trim.
