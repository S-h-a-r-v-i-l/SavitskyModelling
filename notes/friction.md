# `src/savitsky/friction.py`

**Summary (planned — Batch 4, not yet implemented).** Frictional
resistance coefficient Cf via a selectable friction line — Schoenherr
(what Savitsky used; implicit in Cf, so solved numerically with
`scipy.optimize.brentq`) or ITTC-57 (explicit closed form) — plus an
optional roughness allowance ΔCf, and the average-bottom-velocity ratio
V1/V that corrects free-stream velocity down to the actual velocity over
the planing bottom.

**Equation(s).**
- (23): V1 = V·(1 − 2·pd/(ρV²))^0.5 (Bernoulli, general).
- (24): V1 = V·(1 − 0.0120·τ^1.1/(λ^0.5·cosτ))^0.5 for β=0; generalizes to
  β≠0 using CLβ in place of the β=0 dynamic-lift term (paper's Fig. 14).
- Schoenherr and ITTC-57 themselves are **not** Savitsky equations — they
  are standard external friction lines the paper cites (ref. [14]) but
  doesn't restate; implemented as documented external formulas, not
  invented. Likewise the ATTC roughness allowance ΔCf is exposed as a
  plain optional parameter (paper's worked example quotes ΔCf=0.0004 as a
  table value, not a derivable formula).

**Role in the model.** Produces Cf and V1, both required by `drag.py`'s
Df (eq. 19/25). Called once per trial trim τ inside the equilibrium
root-find (Reynolds number depends on V1, which depends on τ through λ via
`lift.py`).

**Status.** Not yet implemented (Batch 4).
