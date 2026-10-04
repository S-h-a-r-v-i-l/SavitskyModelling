# `src/savitsky/result.py`

**Summary.** `ResultFlag` (a `Flag` enum: `NO_SOLUTION`, `MULTIPLE_ROOTS`,
`DRY_CHINES`, `OUT_OF_VALID_RANGE`, combinable via `|`) and `PlaningResult`,
a dataclass holding every quantity the solve can produce (`tau_deg`, `lam`,
`Lk`, `Lc`, `Cp`, `lp`, `V1`, `Cf`, `Df`, `Dp`, `D`, `EHP`), all
`Optional[float] = None` until the batch that computes them lands, plus
`converged: bool` and `flags: ResultFlag`.

**Equation(s).** n/a — a container type, not a formula. Its fields are
named after the quantities defined by eq. (5) (`lam`), (3)/(4) (`Lk`,
`Lc`), (28) (`Cp`, `lp`), (19)/(23) (`V1`, `Cf`, `Df`), (17)/(25) (`Dp`,
`D`), and the equilibrium trim `tau_deg` from eq. (35)/(37).

**Role in the model.** The single return type for `core.solve_single_point`
and (wrapped in a list) `sweep.solve_speed_sweep`. Central to the
never-raise design: a bad physical case (dry chines, speed/trim/lambda
outside the paper's validity windows, a bracket with no sign change) sets
the relevant flag and returns whatever partial numbers were computable,
instead of throwing — so a caller sweeping thousands of hull variants can
filter on `flags` afterward rather than wrapping every call in try/except.

**Status.** Implemented (Batch 1); fields get populated as later batches
(3-9) land, no structural changes expected.
