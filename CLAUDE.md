# SavitskyModelling

A from-scratch Python implementation of D. Savitsky's "Hydrodynamic Design
of Planing Hulls" (Marine Technology, Vol. 1, No. 1, Oct. 1964, pp. 71-95)
for a student electric boat (PEP27 Uncrewed Open division: ~45-60 kg hull +
27 kg/60 lb removable payload, 15-20 mph target, 2-mile race, ≤55.5V/500Ah).
Results must be defensible in the competition white paper, so **every
formula cites its Savitsky equation number** in a comment/docstring, or is
flagged as an external standard (Schoenherr friction, ITTC-57 — the paper
cites but doesn't restate these). `python-openplaning` (PyPI: `openplaning`,
class `PlaningBoat`) is used **only** as an independent test oracle in the
dev test suite — never copied from, never a source of implementation logic.

## Working agreement

- Implement **one batch per turn**, then stop for validation/sign-off before
  starting the next. Don't cascade into later batches even if the path
  looks obvious.
- After `/clear`: re-read this file, run `pytest -q` to see which batches'
  tests exist and pass, check the batch list below for the next unchecked
  item, and resume there.
- **After finishing a batch, write a short non-technical summary** of what
  it added: plain language, minimal jargon, the kind of thing a teammate
  or a competition judge could read. Say what it does, why it matters, and
  how we know it is right. Keep it short.
- Every module's purpose, paper-equation mapping, and role in the pipeline
  is documented in `notes/` (one file per `src/savitsky/*.py` module,
  `notes/README.md` is the index with the data-flow overview). Update the
  relevant `notes/*.md` as part of each batch's own changes, not as an
  afterthought.
- **`notes/caveats.md`** collects everything a competition reviewer could
  challenge: errors in the paper we deliberately do not reproduce,
  judgement calls where the paper is silent, the 1-3% chart-reading floor
  on agreement, and the method's validity limits for our hull. Add to it
  whenever a batch turns up something of that kind.
- **`notes/paper_reference.md` holds all worked-example data** (Tables 1
  and 2 in full, the derived ρ/ν the paper used, validity ranges, the PDF
  page map, and the known errors in the paper). Read it before starting a
  batch — it is designed so you do **not** need to re-read the PDF. Two
  things in it that will otherwise bite: the example runs in fresh water
  with ν = 1.00×10⁻⁵ ft²/s (our `FRESH_WATER` preset will not reproduce
  the paper's Re/Cf), and Table 1's printed λe = 3.29 is an arithmetic
  error for ≈3.42-3.475.

## Equation map

| Topic | Eq. # | Notes |
|---|---|---|
| Wave-rise, λ vs λ₁ | (1) | flat-plate wetted length |
| L₂ (chine/keel calm-water diff) | (2) | |
| Lk − Lc (deadrise wetted-length diff) | (3) | matches Fig. 6 |
| Lk = d/sinτ | (4) | |
| λ = (Lk+Lc)/2b | (5) | |
| Spray edge angle Φ, K, A, k₁ | (6) | future-hook material, not core path |
| Spray area As | (7) | future-hook only |
| CL (generic low-AR form) | (8)-(10) | derivation |
| Buoyant lift Lb | (11) | |
| **CL0 (zero-deadrise lift)** | **(15)** | `CL0 = τ^1.1 [0.0120λ^0.5 + 0.0055λ^2.5/Cv²]`, valid 0.60≤Cv≤13.00, 2°≤τ≤15°, λ≤4 |
| **CLβ (deadrise lift)** | **(16)** | `CLβ = CL0 − 0.0065·β·CL0^0.60` |
| Pressure drag Dp | (17) | `Δ tanτ` |
| Total drag (frictionless+friction) | (18) | |
| Friction drag Df | (19) | `Cf ρ V1² λb² / (2cosβ)` |
| V1 (avg bottom velocity), β=0 | (23),(24) | generalizes to β≠0 via CLβ |
| **Total hydrodynamic drag D** | **(25)** | `Δ tanτ + ρV1²Cfλb²/(2cosβcosτ)` |
| D/Δ ratio | (26),(27) | |
| **Center of pressure Cp = lp/(λb)** | **(28)** | `0.75 − 1/(5.21·Cv²/λ² + 2.39)` |
| **General-case equilibrium** | **(29)-(31)** | vertical force, horizontal force, moment about CG |
| Simplified equilibrium (ε=0) | (32),(35),(36) | thrust parallel to keel |
| Simplest case (all forces through CG) | (37) | `N = Δ/cosτ`, `λ·Cp·b = LCG` |
| Porpoising limits | Fig. 18 | τ vs √(CL/2), curves for β=0°,10°,20° |

Schoenherr/ITTC-57 friction lines and ATTC roughness allowance ΔCf are
external standards, not Savitsky equations — exposed as explicit, documented
inputs rather than hardcoded unsourced formulas.

## Package layout

```
src/savitsky/
    __init__.py
    constants.py           # g, fresh/salt water (rho, nu) defaults
    geometry.py             # eq (1)-(5): wetted-length relations, Lk, Lc, L2, d
    lift.py                  # eq (15),(16): CL0(tau,lambda,Cv), CLbeta; solve_lambda_from_CL
    friction.py              # Schoenherr (implicit, brentq), ITTC-57, roughness, V1/V (eq 23/24)
    drag.py                   # eq (17)-(19),(25)-(27): Dp, Df, D, D/Delta
    center_of_pressure.py     # eq (28): Cp, lp
    equilibrium_simple.py      # eq (37): solve tau via lp(tau) == LCG (brentq)
    equilibrium_general.py     # eq (29)-(31)/(35): general case, thrust line + friction lever a
    porpoising.py               # Fig. 18 digitized curves, stability check
    result.py                    # PlaningResult dataclass + ResultFlag enum
    core.py                       # solve_single_point(...) -> PlaningResult
    sweep.py                       # solve_speed_sweep(...) -> list[PlaningResult]
    hooks.py                        # future-extension stub interfaces only

tests/
    test_scaffolding.py              # Batch 1 smoke tests
    test_paper_worked_example.py      # Table 1 (general case) + Table 2 (simple case) reproduction
    test_against_openplaning.py        # grid vs openplaning.PlaningBoat, dev-only dependency
    test_trends.py                      # monotonic trend checks
    test_solver_robustness.py            # dry-chine / out-of-range / no-solution flags
```

All public functions in `geometry.py`/`lift.py`/`friction.py`/`drag.py`/
`center_of_pressure.py` take/return plain floats (no hidden state) so
`core.solve_single_point` stays a pure function — vectorizable later for
sweeping thousands of hull variants without a redesign.

## Conventions

- SI at every public function boundary (m, N, rad internally for trig, kg,
  m/s, Pa, m²/s). `tau_deg`/`tau_rad`, `beta_deg`/`beta_rad` kept explicit
  wherever both appear — Savitsky's empirical fits take degrees, trig needs
  radians.
- `WaterProperties(rho, nu)` dataclass; fresh-water default, salt-water
  preset available (`src/savitsky/constants.py`).
- Friction line selectable: Schoenherr (implicit, solved via
  `scipy.optimize.brentq`) or ITTC-57 (explicit). Optional roughness
  allowance ΔCf (default 0.0).
- All 1-D solves use bracketed `scipy.optimize.brentq` — no unbracketed
  Newton iteration anywhere.
- `PlaningResult` never raises on a bad physical case — it returns
  `ResultFlag` bits (`NO_SOLUTION`, `MULTIPLE_ROOTS`, `DRY_CHINES`,
  `OUT_OF_VALID_RANGE`) plus whatever partial numbers were computable.

## Batch plan

- [x] **Batch 1 — scaffolding.** `.gitignore`, `pyproject.toml`, package
      skeleton (all modules as stubs), `constants.py`, `result.py`.
      *Validated:* `pip install -e .` succeeds, package imports, smoke
      tests pass. Committed `eca6677`.
- [x] **Batch 2 — geometry (eq. 1-5).** `geometry.py`: λ↔λ₁ wave-rise
      relation, Lk−Lc, Lk, Lc, L2, d. *Validated:* 30 tests in
      `tests/test_geometry.py` — Fig. 3/Fig. 6 chart reads agree to better
      than 0.005 beams, Table 1's Lk/Lc/d reproduced to
      −0.10%/+0.49%/+0.05% (the Lc gap is the paper's own hand-arithmetic
      slop: its stated inputs give 36.28 ft at full precision).
- [x] **Batch 3 — lift (eq. 15-16).** `lift.py`:
      `zero_deadrise_lift_coefficient`, `deadrise_lift_coefficient`,
      `solve_cl0_from_cl_beta`, `solve_lambda_from_cl0` (bracketed
      root-finds), plus the published validity constants. *Validated:* 50
      tests in `tests/test_lift.py` — Table 1's `CL0/τ^1.1` rows
      (.0397/.0254/.0185) matched to <0.2%; λ vs Fig. 10 reads
      +0.6%/+0.4%/−3.0% at τ=2/3/4°, with the −3.0% explained (Fig. 10
      only draws Cv=3.0 and 4.0; the example needs 3.18, and the paper's
      1.86 falls inside our [1.768, 1.937] bracket — asserted by test).
      Note solve functions raise `ValueError`; Batch 7 converts to
      `NO_SOLUTION`.
- [x] **Batch 4 — friction (Schoenherr/ITTC-57, V1/V).** `friction.py`:
      implicit Schoenherr (brentq), explicit ITTC-57, roughness allowance,
      V1/V + Reynolds number. *Validated:* 43 tests in
      `tests/test_friction.py` — Table 1's Cf reproduced to <0.3%, row 9
      (Cf+ΔCf) to 0.4%, Re to 0.5%, Vm to 0.33%, and Fig. 14 reads to
      0.006. **Judgement call recorded:** the paper prints eq. (24) for
      β=0 only and leaves Fig. 14's f(β) undefined; we apply eq. (16) to
      the dynamic lift term per the text on p. 83, which matches the
      readable end of Fig. 14 (λ=1) and the correct trend direction. See
      `notes/friction.md`. Remember Re uses λ·b and V1, not b and V.
- [x] **Batch 5 — drag (eq. 17-19, 25-27).** `drag.py`: Dp, Df, D, D/Δ.
      *Validated:* 24 tests in `tests/test_drag.py` — Table 1's Df matched
      to <0.36%, Dp to <0.2%, D to <0.28%; Table 2 near exact (Df 6669 vs
      6670 lb, D 9010 vs 9010 lb). **Found: the paper mixes two water
      densities.** Its Df rows imply ρ≈2.00 slug/ft³ (seawater) while its
      CLβ line implies 1.94 (fresh) — 3% apart, so no single ρ reproduces
      both printed quantities. Tests use 2.00 for drag; ρ stays a caller
      input. See `notes/drag.md` and `notes/paper_reference.md`.
- [x] **Batch 6 — center of pressure (eq. 28).** `center_of_pressure.py`:
      Cp, lp. *Validated:* 12 tests in `tests/test_center_of_pressure.py`
      — both asymptotic limits exact (Cv→∞ gives 0.75, Cv→0 gives 0.332,
      matching the paper's prose that dynamic lift acts at 75% and buoyant
      at 33% of wetted length); Table 2's implied Cp=0.600 reproduced as
      0.6033; Table 1 row 17 within 1.4% (Fig. 17 chart reads). No Fig. 17
      chart-read tests by design — that figure is just a plot of eq. (28).
- [ ] **Batch 7 — Phase 1 assembly.** `equilibrium_simple.py` (eq. 37,
      bracketed root-find τ s.t. `Cp(Cv,λ(τ))·λ(τ)·b == LCG`),
      `core.solve_single_point` wiring batches 2-6 for one hull/speed.
      *Validate:* full reproduction of Table 2 (Δ=60,000 lb, LCG=29 ft,
      b=14 ft, β=10°, V=40 kn → τ≈2.23°, D≈9010 lb, EHP≈1100), ~1-2% tol.
- [ ] **Batch 8 — Phase 2: speed sweep.** `sweep.solve_speed_sweep` wrapping
      batch 7 over an array of speeds. No new physics. *Validate:* sweep
      for the Table 2 hull, eyeball monotonic trends; solver-robustness
      flags (dry chines, out-of-range, no-solution) exercised across range.
- [ ] **Batch 9 — Phase 3: general-case equilibrium.**
      `equilibrium_general.py` (eq. 29-31/35, thrust line ε/f, friction
      lever a); extends `core.solve_single_point` (simple case stays
      available as ε=f=a=c=0). *Validate:* full reproduction of Table 1
      (a=1.39 ft, f=0.50 ft, ε=4° → τe≈2.3°, D≈9095 lb, EHP≈1115).
- [ ] **Batch 10 — cross-validation suite.** `test_against_openplaning.py`
      (grid speed×deadrise×LCG, report >3% disagreements, no auto-"fixing")
      and `test_trends.py` (trim↓ w/ speed, drag↑ w/ deadrise, trim↑ as LCG
      moves aft). *Validate:* review disagreement report together.
- [ ] **Batch 11 — Phase 4: porpoising.** Digitize/fit Fig. 18 — **ask
      first** how to do this (manual tie-points + interpolation vs.
      digitized curve-fit vs. other) before writing any code.

Future hooks (`hooks.py`: `effective_deadrise`, `pre_planing_resistance`,
`DrivetrainModel`/`BatteryModel`/`PropellerModel` Protocols) get added
opportunistically when a batch naturally exposes the extension point — not
a batch of their own.

## Verification

- `pip install -e ".[dev]"` then `pytest -q`.
- Manual sanity check once Batch 8 lands: print a speed sweep for a rough
  PEP27-scale hull (b≈0.5 m, β≈15-20°, Δ≈(45-60 kg + 27 kg)·9.81 N) across
  5-10 m/s and eyeball trim/drag curves before trusting them for design
  decisions.
