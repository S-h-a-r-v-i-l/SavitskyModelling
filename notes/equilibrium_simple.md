# `src/savitsky/equilibrium_simple.py`

**Summary (planned — Batch 7, not yet implemented).** Solves for the
equilibrium trim angle τ in the simplest case, where thrust, friction drag,
and the hydrodynamic normal force N are all assumed to pass through the
CG (a=f=c=ε=0 in the paper's general-case notation). Bracketed root-find
(`scipy.optimize.brentq`) over τ in the valid trim range (paper's example
brackets between 2° and 3°, but the search range should cover the full
paper-valid window, flagging `OUT_OF_VALID_RANGE` outside it).

**Equation(s).**
- (37): N = Δ/cosτ, and the equilibrium condition λ·Cp·b = LCG. Combined
  with (15)/(16) (λ from CLβ via `lift.py`) and (28) (Cp via
  `center_of_pressure.py`), the root-find variable is τ and the residual
  function is `Cp(Cv, λ(τ))·λ(τ)·b − LCG`.

**Role in the model.** This is the Phase-1/Batch-7 core solve. Given a
hull (b, β, LCG, Δ) and a speed V, it's the function that produces the
converged τ, from which `lift.py`, `friction.py`, `drag.py`, and
`center_of_pressure.py` are re-evaluated once more to populate the rest of
`PlaningResult`. Called by `core.solve_single_point` whenever the
general-case thrust-line parameters (ε, f, a, c) aren't supplied.

**Status.** Not yet implemented (Batch 7). Validation target: paper's
Table 2 worked example (Δ=60,000 lb, LCG=29 ft, b=14 ft, β=10°, V=40 kn →
τ≈2.23°, D≈9010 lb, EHP≈1100).
