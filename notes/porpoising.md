# `src/savitsky/porpoising.py`

**Summary (planned — Batch 11, not yet implemented; implementation
approach to be discussed with the user before coding, per standing
instruction).** Checks a converged operating point for porpoising
(dynamic pitch/heave instability) by comparing its trim angle against
Savitsky's empirically-derived critical-trim limit curves.

**Equation(s).** Fig. 18 — trim angle (deg) vs. √(CL/2), with separate
limit curves for β=0°, 10°, 20° deadrise. Not a closed-form equation in the
paper; the curves are empirical/graphical, digitized from the paper's own
Fig. 18. The digitization/fitting method (manual tie-points +
interpolation, a digitized point-cloud + curve fit, or similar) is an open
decision — ask the user before implementing, as previously agreed.

**Role in the model.** A post-hoc stability check, not part of the
equilibrium solve itself: given a converged `PlaningResult` (τ, and the
load coefficient CL used to get there), compares τ against the Fig. 18
limit curve at the hull's β (interpolating between the 0°/10°/20° curves
for intermediate deadrise) and reports stable/unstable. Does not feed back
into `equilibrium_simple.py`/`equilibrium_general.py`.

**Status.** Not yet implemented (Batch 11).
