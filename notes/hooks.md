# `src/savitsky/hooks.py`

**Summary.** Typed stub interfaces only — no implementation, by design.
Documents three future extension points called out in the original scope
but explicitly deferred: `effective_deadrise(hull, wetted_region)` for
variable-deadrise hulls, `pre_planing_resistance(...)` for a hump-resistance
estimate below the planing speed range, and `DrivetrainModel`/
`BatteryModel`/`PropellerModel` Protocol classes for a later combined
drivetrain+battery+prop sweep.

**Equation(s).** None yet — these aren't in the paper's core planing
equations. `effective_deadrise` relates to material in eq. (6)-(7) (spray
edge/spray area, which involve the deadrise over the wetted region) but
isn't a direct implementation of those equations.

**Role in the model.** Not consumed by any other module yet. Exists so the
*interface shape* (function signatures, Protocol definitions) is decided
and documented ahead of time, even though nothing calls it until a future,
separate scope item.

**Status.** Interfaces only, added opportunistically as each relevant
batch lands; no implementation planned in Batches 1-11.
