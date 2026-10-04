# `src/savitsky/sweep.py`

**Summary (planned — Batch 8, not yet implemented).**
`solve_speed_sweep(...)`: calls `core.solve_single_point` once per speed
over an array of speeds for a fixed hull, returning a `list[PlaningResult]`
(resistance, trim, λ, wetted keel/chine lengths, and validity flags at
each speed).

**Equation(s).** None directly — no new physics, just iterates
`core.solve_single_point` and collects results.

**Role in the model.** The Phase-2 scope item: produces the resistance/
trim/λ-vs-speed curves used for the design sanity checks in `CLAUDE.md`'s
Verification section, and is the first place the `ResultFlag` machinery
(`DRY_CHINES`, `OUT_OF_VALID_RANGE`, `NO_SOLUTION`) gets exercised across a
realistic range rather than at a single hand-picked point.

**Status.** Not yet implemented (Batch 8).
