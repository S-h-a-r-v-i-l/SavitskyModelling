# notes/

One file per module in `src/savitsky/`, each with a **Summary**, the
Savitsky (1964) **equation(s)** it implements, and its **role in the
model**. Kept up to date as part of each batch's own changes (see
`CLAUDE.md` batch list for build status) — if a module is still a stub,
its note says so explicitly rather than describing unwritten behavior.

## Data flow

```
geometry.py  ─┐
lift.py       ├─ physics primitives: pure functions of (tau, beta, lambda, Cv, ...)
friction.py   │  no equilibrium-solving, no state
drag.py       │
center_of_pressure.py ─┘
        │
        ▼
equilibrium_simple.py   (Batch 7)   — eq. 37: all forces through CG.
equilibrium_general.py  (Batch 9)   — eq. 29-31/35: thrust line + friction lever.
  both root-find the trim angle tau using the primitives above, then
  read off lambda, Cp, Df, D, etc. at the converged tau.
        │
        ▼
core.solve_single_point   — one hull, one speed -> PlaningResult.
  picks simple vs. general case based on which inputs are given
  (ε=f=a=c=0 falls back to the simple case).
        │
        ▼
sweep.solve_speed_sweep   (Batch 8) — core.solve_single_point over an
  array of speeds -> list[PlaningResult]. No new physics.

porpoising.py (Batch 11) — a separate, post-hoc stability check: given a
  converged (tau, CL) from core/sweep, compare against Savitsky's Fig. 18
  limit curves. Does not feed back into the equilibrium solve.

hooks.py — unimplemented extension points (effective deadrise for
  variable-deadrise hulls, pre-planing resistance, drivetrain/battery/
  propeller coupling) referenced by no other module yet.

result.py / constants.py — shared types (PlaningResult, ResultFlag,
  WaterProperties) used across the whole pipeline, not physics themselves.
```

## Index

- [`paper_reference.md`](paper_reference.md) — **start here when validating
  a batch.** All worked-example data (Tables 1 and 2 in full), the ρ/ν the
  paper actually used, validity ranges, PDF page map, and the known errors
  in the paper. Written so batches can be validated without re-reading the
  PDF.
- [`__init__.md`](__init__.md) — package root
- [`constants.md`](constants.md) — water properties, gravity
- [`result.md`](result.md) — `PlaningResult`, `ResultFlag`
- [`geometry.md`](geometry.md) — eq. (1)-(5)
- [`lift.md`](lift.md) — eq. (15)-(16)
- [`friction.md`](friction.md) — Schoenherr/ITTC-57, eq. (23)-(24)
- [`drag.md`](drag.md) — eq. (17)-(19), (25)-(27)
- [`center_of_pressure.md`](center_of_pressure.md) — eq. (28)
- [`equilibrium_simple.md`](equilibrium_simple.md) — eq. (37)
- [`equilibrium_general.md`](equilibrium_general.md) — eq. (29)-(31), (35)
- [`porpoising.md`](porpoising.md) — Fig. 18
- [`core.md`](core.md) — single-point entry
- [`sweep.md`](sweep.md) — speed sweep
- [`hooks.md`](hooks.md) — future extension stubs
