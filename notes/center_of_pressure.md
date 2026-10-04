# `src/savitsky/center_of_pressure.py`

**Summary (planned — Batch 6, not yet implemented).** The longitudinal
position of the resultant hydrodynamic normal force N, as a fraction Cp of
the mean wetted length λb forward of the transom, and the corresponding
absolute distance lp = Cp·λb.

**Equation(s).**
- (28): Cp = lp/(λb) = 0.75 − 1/(5.21·Cv²/λ² + 2.39).

**Role in the model.** This is the equation that closes the equilibrium
loop in the simple case: `equilibrium_simple.py` (eq. 37) root-finds the
trim τ such that lp(τ) = Cp(Cv, λ(τ))·λ(τ)·b equals the given LCG. In the
general case (`equilibrium_general.py`), Cp/lp feed into the moment
equation (31) via the lever arm `c` between N and the CG. Depends only on
Cv (from the operating point) and λ (from `lift.py`'s λ-solve at the trial
τ) — no dependency on friction/drag.

**Status.** Not yet implemented (Batch 6).
