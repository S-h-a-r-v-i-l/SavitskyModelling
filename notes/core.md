# `src/savitsky/core.py`

**Summary.** `solve_single_point(...)`: the library's main entry point.
Takes a hull (load, beam, LCG, deadrise), a speed, and water properties;
returns a fully populated `PlaningResult`. Keyword-only arguments, because
there are many same-typed floats and positional order would be easy to get
wrong.

**Equation(s).** None of its own -- pure orchestration. Every number it
returns traces to the module that computed it: [[geometry]], [[lift]],
[[friction]], [[drag]], [[center_of_pressure]], [[equilibrium_simple]].

**Order of operations** (mirrors the paper's Table 2 procedure):
1. Non-dimensionalise: `Cv = V/sqrt(g*b)` and
   `CLbeta = Delta/(0.5*rho*V^2*b^2)`.
2. Invert eq. (16) **once** for CL0. It depends on neither trim nor wetted
   length, which is why Table 1 carries a single CL0 across all three of
   its trim columns -- doing it inside the trim loop would be wasted work.
3. Root-find the trim where the centre of pressure sits over the CG
   (eq. 37).
4. Evaluate wetted lengths, bottom velocity, Reynolds number, friction
   coefficient and drag at that converged trim.

**This is the only module that catches exceptions.** The primitives raise
loudly when a root does not exist; `solve_single_point` translates that
into `ResultFlag.NO_SOLUTION` so callers sweeping thousands of hull
variants never need try/except. A test sweeps 96 combinations of speed,
deadrise and LCG asserting nothing escapes.

**Two try blocks, deliberately.** The trim solve and the downstream
evaluation are wrapped separately so that a trim found far outside the
fitted envelope is still *reported* even when the physics then breaks down
on it. This was a real bug caught in Batch 7: a CG almost at the transom
drives trim to 24 deg with lambda = 0.05, where eq. (24)'s radicand goes
negative; the first version let that ValueError escape, violating the
never-raise contract. Now that case returns `tau_deg = 24.3` with
`NO_SOLUTION | OUT_OF_VALID_RANGE | DRY_CHINES` and `D = None`.

**Validity flags constrain outputs, not inputs.** The published limits
(0.60 <= Cv <= 13, 2 <= tau <= 15 deg, lambda <= 4) are on quantities the
solve produces, so they can only be checked afterwards -- which is exactly
why the result carries flags rather than the constructor validating.

**Status.** Implemented for the simple case (Batch 7); the general-case
input path (thrust line, friction lever) arrives in Batch 9. 24 tests in
`tests/test_core.py`.

Validation: full reproduction of Table 2 from raw inputs, with nothing
read off a chart -- trim 2.216 deg vs the paper's 2.23 (-0.6%),
lambda 3.426 vs 3.45 (-0.7%), friction drag 6653 vs 6670 lb (-0.3%),
total drag 8980 vs 9010 lb (-0.3%), effective power 1102 vs 1100 hp
(+0.2%). That run uses rho = 2.00 slug/ft^3; a companion test shows the
1.94 the same table implies elsewhere reproduces CLbeta = 0.069 exactly
while missing the drag by about 2%, which is caveat A2 in action.
