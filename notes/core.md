# `src/savitsky/core.py`

**Summary (planned — assembled in Batch 7, extended in Batch 9; not yet
implemented).** `solve_single_point(...)`: the single public entry point
for "solve this one hull, at this one speed, in this one water." Wires
together `geometry.py`, `lift.py`, `friction.py`, `drag.py`,
`center_of_pressure.py`, and whichever of `equilibrium_simple.py` /
`equilibrium_general.py` applies (based on whether thrust-line/lever-arm
parameters are supplied), and packages the result into a `PlaningResult`.

**Equation(s).** None directly — pure orchestration. Every number in its
output traces back to the equation cited in the module that computed it
(see those modules' notes).

**Role in the model.** The one function everything else calls: Batch 8's
`sweep.py` calls it once per speed; Batch 10's cross-validation tests call
it per (speed, deadrise, LCG) grid point; a future bulk hull-variant sweep
(mentioned in the original scope as a design requirement) would call it in
a vectorized/parallel loop. Designed as a pure function over plain floats
(no hidden state) specifically so that kind of sweep doesn't require a
redesign later.

**Status.** Not yet implemented (Batch 7 for the simple-case path, Batch 9
for the general-case path).
