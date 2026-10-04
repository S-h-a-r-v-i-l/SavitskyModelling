# `src/savitsky/drag.py`

**Summary (planned — Batch 5, not yet implemented).** Combines pressure
drag (component of the normal force N along the direction of travel) and
friction drag (from `friction.py`) into total hydrodynamic drag, plus the
drag-lift ratio D/Δ.

**Equation(s).**
- (17): Dp = Δ·tanτ.
- (18): D = Δ·tanτ + Df/cosτ (frictionless-fluid form, restated with
  friction added).
- (19): Df = Cf·ρ·V1²·(λb²)/(2cosβ).
- (25): D = Δ·tanτ + ρ·V1²·Cf·λb²/(2cosβ·cosτ) — the combined,
  final-form total drag.
- (26), (27): D/Δ = tanτ + ρV1²Cfλb²/(2Δ·cosβ·cosτ), rearranged using
  CL in place of Δ/(ρV²b²).

**Role in the model.** `D` is the quantity reported in `PlaningResult.D`
and used for `EHP = D·V`. Also the quantity `equilibrium_general.py`
balances horizontally (eq. 30) against thrust. Depends on `friction.py`'s
Cf/V1 and (implicitly, through τ) `lift.py`'s λ.

**Status.** Not yet implemented (Batch 5).
