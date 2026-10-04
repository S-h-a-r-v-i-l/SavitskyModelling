# `src/savitsky/lift.py`

**Summary (planned — Batch 3, not yet implemented).** The empirical
planing-lift relations: zero-deadrise lift coefficient CL0 as a function of
trim τ, wetted length-beam ratio λ, and speed coefficient Cv; the deadrise
correction CLβ; and the inverse — given a target lift coefficient (= load
coefficient at equilibrium), bracketed root-find for the λ that produces
it.

**Equation(s).**
- (15): CL0 = τ^1.1·[0.0120·λ^0.5 + 0.0055·λ^2.5/Cv²]. Valid
  0.60≤Cv≤13.00, 2°≤τ≤15°, λ≤4 — violations set `OUT_OF_VALID_RANGE`.
- (16): CLβ = CL0 − 0.0065·β·CL0^0.60 (β in degrees).

**Role in the model.** Given the load coefficient CLβ = Δ/(0.5·ρ·V²·b²)
implied by the hull's weight and speed, `solve_lambda_from_CL` inverts
(15)+(16) to find λ at a trial trim τ — this is the inner loop both
`equilibrium_simple.py` (eq. 37) and `equilibrium_general.py` (eq. 35) call
at every trial τ during their outer trim root-find. CL0 is monotonic
increasing in λ for fixed τ, Cv, and CLβ is monotonic increasing in CL0, so
the λ-root is bracketable over (0, 4].

**Status.** Not yet implemented (Batch 3).
