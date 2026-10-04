# `src/savitsky/geometry.py`

**Summary (planned — Batch 2, not yet implemented).** Converts between the
mean wetted length-beam ratio λ and the hull's actual wetted keel/chine
lengths, and the flat-plate wave-rise relation. Functions: λ↔λ₁ (wave rise),
`Lk_minus_Lc(tau, beta, b)`, `Lk(d, tau)`, `L2(tau, beta, b)`,
`lam(Lk, Lc, b)` (and the inverse: wetted lengths from λ, τ, β, b).

**Equation(s).**
- (1): λ = 1.60λ₁ − 0.30λ₁² (0≤λ₁≤1), λ = λ₁ + 0.30 (1≤λ₁≤4) — flat-plate
  wave rise.
- (2): L2 = (b/2)·tanβ/tanτ.
- (3): Lk − Lc = (b/π)·tanβ/tanτ.
- (4): Lk = d/sinτ.
- (5): λ = (Lk + Lc)/(2b).

**Role in the model.** Pure geometric relations with no lift/drag physics.
Consumed by `equilibrium_simple.py`/`equilibrium_general.py` to turn a
trial trim angle τ (during the trim root-find) into the wetted lengths Lk,
Lc needed for the `DRY_CHINES` check (Lc≤0) and reported in the final
`PlaningResult`.

**Status.** Not yet implemented (Batch 2).
