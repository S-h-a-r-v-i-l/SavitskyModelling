# `src/savitsky/drag.py`

**Summary.** Turns the ingredients from [[friction]] and [[lift]] into
actual forces. Public functions: `pressure_drag(load, tau_deg)` (eq. 17),
`friction_drag(cf, rho, v1, lam, beam, beta_deg)` (eq. 19),
`total_drag(load, tau_deg, friction_drag_force)` (eq. 18/25), and
`drag_lift_ratio(...)` (eq. 26/27).

**Equation(s).**
- (17): `Dp = Delta*tan(tau)`. Pressure component -- the hydrodynamic
  normal force resolved along the direction of travel. Depends only on
  load and trim: no speed, no area, no friction line.
- (18): `D = Delta*tan(tau) + Df/cos(tau)`. The `1/cos(tau)` resolves the
  keel-parallel shear force into the horizontal.
- (19): `Df = Cf*rho*V1^2*(lambda*b^2)/(2*cos(beta))`.
- (25): (17) and (19) combined into one expression.
- (26): `D/Delta`, and (27) the same thing in coefficient form,
  `tan(tau) + (V1/V)^2*Cf*lambda/(CL*cos(tau)*cos(beta))`. We implement
  (26) and assert (27)'s equivalence in a test rather than duplicating
  the formula -- that test also pins the wetted-area convention, since a
  wrong area breaks the identity.

**Role in the model.** The end of the force chain for a given trial trim:
[[lift]] gives lambda, [[friction]] gives Cf and V1, this module turns
them into Df and D. `total_drag` is what gets reported as
`PlaningResult.D` and what Batch 9's horizontal-equilibrium equation (30)
balances against thrust. Effective power is just `D * V` and is left to
Batch 7 rather than duplicated here.

**Wetted-area convention.** Eq. (19) uses `lambda*b^2/cos(beta)`: the
projected pressure area divided by cos(beta) to get true surface area on
the inclined V-bottom. Savitsky recommends the pressure area alone with
**no spray-area addition** below 4 deg trim (p. 83), noting the spray
sheet there is thinner than previously assumed; Tables 1 and 2 use it at
every trim. We follow the tables. Adding spray area is a future refinement,
not a correction.

**The density inconsistency (found in this batch -- affects Batches 7/9).**
Inverting eq. (19) on all four printed Df values backs out
rho = 1.994 / 2.007 / 1.998 / 2.000 slug/ft^3, so the drag rows were
computed with **rho = 2.00** (rounded seawater). But the CLbeta line at
the head of the same tables, `60,000/0.97 x 67.5^2 x 14^2`, implies
rho/2 = 0.97, i.e. **rho = 1.94** (fresh water). The paper mixes the two,
a 3% difference; using 1.94 in eq. (19) undershoots its own printed Df by
about 3% at every trim. No single density reproduces both printed
quantities. Our tests use 2.00 for the drag comparisons because that is
what those rows were computed with; nothing in the library hardcodes
either, since density is a caller input. Recorded in
`notes/paper_reference.md` under known discrepancies.

**Status.** Implemented and validated (Batch 5). 24 tests in
`tests/test_drag.py`. With rho = 2.00 slug/ft^3: Table 1's Df row matches
to within 0.36% (+0.28 / -0.36 / +0.10%), row 14 (Dp) to within 0.2%, row
16 (D) to within 0.28%; Table 2 is near exact (Df 6669 vs 6670 lb, D 9010
vs 9010 lb). Structural tests cover the V1^2 and wetted-length scalings,
the 1/cos(beta) area factor, the eq. (25) combined form, and the
eq. (26)/(27) identity.
