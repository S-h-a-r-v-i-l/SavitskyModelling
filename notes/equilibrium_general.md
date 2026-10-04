# `src/savitsky/equilibrium_general.py`

**Summary (planned — Batch 9, not yet implemented).** Solves for the
equilibrium trim angle τ in the general case, where the propeller thrust
line has an arbitrary inclination ε and offset f from the CG, and the
friction-drag force acts along a lever arm `a` from the CG (not through
it). Bracketed root-find over τ, evaluating the combined force/moment
residual (eq. 35) at each trial τ via `lift.py`/`friction.py`/`drag.py`/
`center_of_pressure.py`, same inner-loop structure as
`equilibrium_simple.py` but with the extra thrust-line/lever-arm terms.

**Equation(s).**
- (29): vertical equilibrium — Δ = N·cosτ + T·sin(τ+ε) − Df·sinτ.
- (30): horizontal equilibrium — T·cos(τ+ε) = Df·cosτ + N·sinτ.
- (31): moment equilibrium about CG — N·c + Df·a − T·f = 0.
- (35): the three combined into a single residual in τ (eliminating N via
  (29)+(30)), the actual root-find target.
- (32), (36): special cases (ε=0: thrust parallel to keel) that the general
  solver reduces to automatically when ε=0 is passed, without needing a
  separate code path.

**Role in the model.** The Batch 9 extension of `core.solve_single_point`:
when ε, f, a, c are supplied (not all zero), this module is used instead
of `equilibrium_simple.py`. Setting ε=f=a=c=0 must reproduce
`equilibrium_simple.py`'s result exactly (eq. 37 is the a=f=c=ε=0
specialization of eq. 35) — a useful consistency check in its own right.

**Status.** Not yet implemented (Batch 9). Validation target: paper's
Table 1 worked example (same Δ/LCG/b/β/V as Table 2, plus a=1.39 ft,
f=0.50 ft, ε=4° → τe≈2.3°, D≈9095 lb, EHP≈1115).
