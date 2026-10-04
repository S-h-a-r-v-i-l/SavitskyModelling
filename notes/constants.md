# `src/savitsky/constants.py`

**Summary.** Standard gravity `G` and a `WaterProperties(rho, nu)` frozen
dataclass with two presets, `FRESH_WATER` (~20°C) and `SALT_WATER`
(standard ITTC seawater, ~15°C). Savitsky's equations take rho/nu as given
inputs rather than prescribing them, so these are convenience defaults, not
paper-derived values — any caller can supply its own `WaterProperties`
instead.

**Equation(s).** n/a (external convenience values — standard textbook
water properties, not from the paper).

**Role in the model.** `WaterProperties` is threaded through
`friction.py` (Reynolds number, Schoenherr/ITTC-57) and ultimately
`core.solve_single_point` as part of the operating-point input. `G` is
used wherever the paper's speed coefficient `Cv = V/sqrt(g*b)` is computed
(`lift.py`, and anywhere `Cv` is derived from `V`).

**Status.** Implemented (Batch 1).
