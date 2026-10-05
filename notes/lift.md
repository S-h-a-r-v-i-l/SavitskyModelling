# `src/savitsky/lift.py`

**Summary.** The two empirical planing-lift relations and the inversions
the solver needs. Public functions:
`zero_deadrise_lift_coefficient(tau_deg, lam, cv)` (eq. 15),
`deadrise_lift_coefficient(cl0, beta_deg)` (eq. 16),
`solve_cl0_from_cl_beta(cl_beta, beta_deg)` (eq. 16 inverted), and
`solve_lambda_from_cl0(cl0, tau_deg, cv)` (eq. 15 inverted). Also exports
the published validity constants `CV_MIN/CV_MAX` (0.60/13.00),
`TAU_MIN_DEG/TAU_MAX_DEG` (2/15) and `LAMBDA_MAX` (4) so later batches
flag `OUT_OF_VALID_RANGE` without re-hardcoding them.

**Equation(s).**
- (15): `CL0 = tau^1.1 * [0.0120*lambda^0.5 + 0.0055*lambda^2.5/Cv^2]`.
  First term dynamic, second buoyant; the buoyant term dies as 1/Cv^2.
- (16): `CLbeta = CL0 - 0.0065*beta*CL0^0.60`. Deadrise sweeps the
  stagnation line aft, cutting stagnation pressure and hence lift.

**Role in the model.** The hinge of the whole solve. At equilibrium the
load coefficient `CLbeta = Delta/(0.5*rho*V^2*b^2)` is fixed by weight and
speed, so the chain is: `CLbeta` --eq.(16) inverted--> `CL0` --eq.(15)
inverted--> `lambda`, and `lambda` then feeds wetted lengths
([[geometry]]), wetted area for friction drag ([[drag]]), and centre of
pressure ([[center_of_pressure]]). Mirroring the paper's own procedure,
`solve_cl0_from_cl_beta` is called **once** per operating point (eq. 16
depends on neither tau nor lambda -- Table 1 row 2 is constant across all
three trim columns), while `solve_lambda_from_cl0` is called once per
trial trim inside the Batch 7 root-find.

**Gotchas worth defending in the write-up.**
- **No trig anywhere in this module.** Eq. (15) raises tau in *degrees* to
  the 1.1 power and eq. (16) multiplies beta in *degrees* by a constant.
  Converting either to radians would be wrong.
- Eq. (15) is strictly increasing in lambda (derivative
  `0.0060*lambda^-0.5 + 0.01375*lambda^1.5/Cv^2 > 0`) and zero at
  lambda = 0, so `[0, lam_max]` brackets exactly one root -- no
  multiple-root case here.
- `lam_max` defaults to **10**, past the published lambda <= 4, on
  purpose: a hull needing lambda > 4 should return a flaggable number
  rather than a hard failure that would punch a discontinuity into the
  trim residual Batch 7 root-finds across.
- Eq. (16) is **not monotonic near zero**. Its derivative vanishes at
  `CL0 = (0.0039*beta)^2.5`, below which it runs backwards. The inverse
  brackets from that turning point upward so the root is unique. For
  beta = 10 deg the turning point is CL0 = 3e-4, far below any realistic
  loading, but the guard matters for high deadrise and light loading.
- The solve functions **raise ValueError** when no root exists. That is
  deliberate: these are pure float primitives, and
  `core.solve_single_point` (Batch 7) catches and converts to
  `ResultFlag.NO_SOLUTION`. Returning NaN would propagate silently.

**Status.** Implemented and validated (Batch 3). 50 tests in
`tests/test_lift.py`.

Validation notes: Table 1 row 3 (`CL0/tau^1.1` = .0397/.0254/.0185) is
pure arithmetic in the paper, no chart involved, and we match it to
better than 0.2% -- the sharpest available confirmation of eq. (15)'s
form. The remaining comparisons are against *chart reads* and so are
looser: lambda vs Table 1 row 4 (Fig. 10) is +0.6%/+0.4%/-3.0% at
tau = 2/3/4 deg, Table 2's nomogram lambda is +2.1%, and eq. (16) against
the example CLbeta is +1.7%. The -3.0% outlier is explained: Fig. 10 only
draws curves at Cv = 3.0 and 4.0 while the example needs Cv = 3.18, and
the paper's read of 1.86 falls inside our computed bracket
[1.768, 1.937]. A dedicated test asserts that bracketing for all three
trims, which is independent of how well the original author eyeballed the
interpolation.
