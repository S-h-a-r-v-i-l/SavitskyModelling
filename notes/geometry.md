# `src/savitsky/geometry.py`

**Summary.** Converts between the mean wetted length-beam ratio lambda, the
hull's actual wetted keel/chine lengths, and the transom draft; plus the
flat-plate wave-rise relation. Public functions:
`lambda_from_lambda1` / `lambda1_from_lambda` (eq. 1 and its inverse),
`level_water_keel_chine_difference` (eq. 2), `keel_chine_difference`
(eq. 3), `keel_length_from_draft` / `draft_from_keel_length` (eq. 4),
`mean_wetted_length_ratio` and `mean_wetted_length_ratio_from_draft`
(eq. 5), and `wetted_lengths` (eq. 5 inverted, returning `(Lk, Lc)`).

**Equation(s).**
- (1): lambda = 1.60*lambda_1 - 0.30*lambda_1^2 (0 <= lambda_1 <= 1);
  lambda = lambda_1 + 0.30 (1 <= lambda_1 <= 4). Flat-plate wave rise.
- (2): L2 = (b/2) * tan(beta)/tan(tau) -- level-water keel/chine difference.
- (3): Lk - Lc = (b/pi) * tan(beta)/tan(tau) -- actual difference, a factor
  2/pi smaller than (2) because of Wagner's pi/2 wave-rise factor.
- (4): Lk = d / sin(tau).
- (5): lambda = [d/sin(tau) - (b/2pi)*tan(beta)/tan(tau)] / b = (Lk+Lc)/(2b).

**Role in the model.** Pure geometry, no lift or drag physics. The solver
path (Batches 7/9) calls `wetted_lengths` to turn the lambda found at each
trial trim angle into Lk and Lc -- needed for the `DRY_CHINES` check
(Lc <= 0) and reported in the final `PlaningResult`. `draft_from_keel_length`
supplies the running draft d.

**Gotchas worth defending in the write-up.**
- Eq. (1) and eq. (2)-(5) are separate tracks. Eq. (1) is flat-plate only
  and is *not* used by the deadrise computational path. Setting beta = 0 in
  eq. (5) yields lambda = lambda_1 (no wave rise), which disagrees with
  eq. (1)'s lambda = lambda_1 + 0.30 -- a known limitation of the deadrise
  formulation, not a transcription error.
- `wetted_lengths` returns Lc unclamped, so a negative value is possible and
  means dry chines; flagging that is the caller's job, keeping this module
  a set of pure float functions.

**Status.** Implemented and validated (Batch 2). 30 tests in
`tests/test_geometry.py`: eq. (3) = (2/pi) * eq. (2) identity, eq. (1)
branch continuity at lambda_1 = 1, Fig. 3 and Fig. 6 chart reads (agree to
better than 0.005 beams), round-trips, and Table 1's Lk/Lc/d
(55.9 ft / 36.1 ft / 2.24 ft reproduced to -0.10% / +0.49% / +0.05%).
