# Caveats

Everything found so far that a reader of the competition write-up could
reasonably challenge us on: errors in the source paper, places where we had
to make a judgement because the paper is silent, how precisely our numbers
can be expected to agree with it, and where the method stops applying.

Collected while implementing Batches 1-5. Each entry says what it is, how
we know, and what we did about it. Updated as later batches land.

---

## A. Errors in the paper

These are places where Savitsky's printed numbers are wrong. We do **not**
reproduce them, and no code was tuned to match them.

### A1. Table 1's equilibrium wetted length is wrong (~5%)

The paper prints `λe = 3.85 − (3.85 − 2.60)(3/10) = 3.29`. That arithmetic
gives **3.475**, not 3.29. Solving eq. (15) directly at the equilibrium
trim gives **≈3.42** (λ-vs-τ is nonlinear, so the direct solve differs from
linear interpolation too).

We verified the two endpoint values the interpolation starts from (λ = 3.85
at τ = 2°, 2.60 at τ = 3°) *are* consistent with eq. (15), so the error is
isolated to the interpolation step. The paper then carries 3.29 downstream
consistently — its `Lk = 46 + …` implies 46/14 = 3.286.

**Impact:** Batch 9's wetted lengths will come out roughly 4% off Table 1's
printed Lk and Lc. That is the paper's error, not ours.
**Found in:** Batch 2.

### A2. The tables mix two water densities (3%)

Inverting eq. (19) on all four printed friction-drag values (Table 1's
three trim columns plus Table 2) backs out ρ = 1.994, 2.007, 1.998 and
2.000 slug/ft³ — the drag rows were computed with **ρ = 2.00 slug/ft³**, a
rounded seawater value.

But the CLβ line at the head of those same tables reads
`60,000 / 0.97 × 67.5² × 14²`, and 0.97 is ρ/2 for **fresh water**,
ρ = 1.94. The two differ by 3%. Using 1.94 in eq. (19) undershoots the
paper's own printed drag by about 3% at every trim.

**Impact:** no single self-consistent density reproduces both the printed
lift coefficient and the printed drag. When reporting agreement with the
paper we must say which we matched. Our library takes density as an input,
so neither value is hardcoded.
**Found in:** Batch 5.

### A3. Table 1 row 23 has a copied cell (0.3%)

At τ = 3°, row 23 (`1 − sinτ·sin(τ+ε)`) prints **.9964**, but
1 − 0.0524 × 0.1219 = **.9936**. The printed value is the τ = 2° column's
entry copied across.

**Impact:** negligible. Propagating the correction changes the paper's
equilibrium trim from 2.308° to 2.312°.
**Found in:** Batch 5 audit.

### A4. Hand-arithmetic slop, roughly 0.5-1%, scattered through Table 1

Several cells don't quite follow from their own stated inputs:
- Table 1's wetted chine length prints **36.1 ft**; its own λe, b, β and τe
  at full precision give **36.28 ft** (+0.49%). The keel length (−0.10%)
  and draft (+0.05%) match closely, so this cell is isolated.
- Rows 24 and 26 drift by about 1% from the rows they are computed from
  (e.g. at τ = 3°, row 26 prints 5.53 where its inputs give 5.446).

**Impact:** sets a floor on how exactly anyone can reproduce the paper.
Agreement better than ~1% on these quantities is not meaningful.
**Found in:** Batches 2 and 5.

### A5. Harmless typos

- Table 1's drag line prints "9424" in the first term where 9434 is meant.
- Table 2 row 17's source column prints "(8) + (17)" where "(8) + (16)" is
  meant; 2,340 + 6,670 = 9,010 confirms the intent.

**Impact:** none, intent unambiguous in both cases.

---

## B. Places the paper is silent, where we had to choose

These are judgement calls. Each is defensible, but each is *ours*, and a
reviewer is entitled to ask about them.

### B1. The friction line itself is not in the paper

Savitsky cites Schoenherr (ref. [14]) for the friction coefficient and
reads values off a chart; he never writes the formula down. We supplied the
standard ATTC 1947 form, `0.242/√Cf = log₁₀(Re·Cf)`, solved numerically
because it is implicit in Cf. ITTC-57 is also implemented as a selectable
alternative, but note that choosing it will **not** reproduce Savitsky's
tables.

**Evidence it is the right line:** fed the paper's own Reynolds numbers, it
returns the paper's own Cf values to better than 0.3%.
**Found in:** Batch 4.

### B2. The roughness allowance is a lookup, not a formula

The worked examples add ΔCf = 0.0004, sourced only as "ATTC Standard
Roughness". There is no formula in the paper and none is derivable from it.
We expose it as a plain caller input defaulting to zero (smooth), rather
than inventing a correlation.

**Impact:** for our own boat we must choose this value deliberately and
justify it, rather than inheriting 0.0004 unthinkingly — a small
3D-printed or composite hull is not a 1964 ship hull.
**Found in:** Batch 4.

### B3. The deadrise correction to bottom velocity is undefined

Eq. (24) gives the mean bottom velocity for a **flat** bottom only. Fig. 14
shows the V-bottom version as a factor `f(β)` applied to that correction —
but never defines `f(β)` anywhere in the paper.

We apply eq. (16)'s deadrise correction to the dynamic lift term, which is
what the text on p. 83 describes ("computed in an analogous manner using
the lift coefficient for deadrise surfaces given by (16)"). It reduces to
eq. (24) exactly at β = 0, and reproduces Fig. 14 where that chart is
actually readable — computed 0.885 / 0.901 / 0.917 at τ = 15°, λ = 1 for
β = 10 / 20 / 30° against chart reads of ~0.89 / 0.90 / 0.915, with the
correct trend direction.

**Honest caveat:** against Table 1's bottom-velocity row this runs ~0.3%
high, whereas dropping the deadrise correction entirely lands within 0.12%.
We kept the deadrise version because Table 1's points sit where Fig. 14's
curves bunch together near 0.99 and cannot be read that finely, while the
readable end of the chart favours our choice.
**Found in:** Batch 4.

### B4. The example's water properties are never stated

Neither ρ nor ν appears anywhere in the paper. We derived them from its own
numbers: ν = 1.0×10⁻⁵ ft²/s (inverting `Re = V₁·λ·b/ν` on all four printed
Reynolds numbers gives 1.000, 1.002, 0.996 and 1.004 ×10⁻⁵ — agreement
within 0.4%), and ρ as discussed in A2.

**Impact:** our library's `FRESH_WATER` preset (ν = 1.004×10⁻⁶ m²/s, water
at 20 °C) is *not* what the paper used; it gives Re = 3.34×10⁸ against the
paper's 3.61×10⁸. Paper-reproduction tests pass the paper's ν explicitly.
**Found in:** reference-building, confirmed Batch 4.

### B5. Wetted-area convention excludes spray

Eq. (19) uses the pressure area λb²/cos β. Savitsky recommends exactly this,
with no spray-area addition, below 4° trim (p. 83), noting the spray sheet
is thinner than earlier work assumed; above 4° he points to refs [9] and
[17] for adding it. Tables 1 and 2 use the pressure area at every trim and
we follow the tables.

**Impact:** at trims above ~4° our friction drag is a mild underestimate.
Adding spray area is a future refinement, not a correction.
**Found in:** Batch 5.

---

## C. Why agreement is ~1-3%, not exact

Much of the paper's own procedure is **reading values off charts by eye**,
so there is an irreducible floor on reproducibility that has nothing to do
with either implementation being wrong.

- Table 1's λ values come from Fig. 10. The example needs Cv = 3.18, but
  Fig. 10 only draws curves at Cv = 3.0 and Cv = 4.0 — the author had to
  interpolate between them visually. Our computed λ brackets his reads at
  every trim (e.g. at τ = 4°, ours gives 1.768 at Cv = 3.0 and 1.937 at
  Cv = 4.0, and he read 1.86). Deviations: +0.6%, +0.4%, −3.0%.
- The lift coefficient CL0 = .085 is a Fig. 11 read; computing it from the
  stated CLβ gives 0.0837, a 1.6% difference.
- Table 2's λ = 3.45 comes off the Fig. 19 nomogram; we compute 3.52
  (+2.1%).

**Rule of thumb for the write-up:** quantities the paper computes
arithmetically (`CL0/τ^1.1`, drag sums) we match to better than 0.5%.
Quantities it reads off charts we match to 1-3%, and that is the expected
result, not a defect.

---

## D. Where the method does not apply — relevant to our boat

Savitsky's equations carry explicit validity limits. For a 0.5 m beam hull,
`Cv = V/√(g·b) = V/2.21`:

| Speed | Cv | Status |
|---|---|---|
| 5 mph | 1.01 | at the absolute floor of the method |
| 10 mph | 2.02 | valid range, but likely still pre-planing |
| 15 mph | 3.03 | valid, planing |
| 20 mph | 4.04 | valid, planing |

Published limits for the lift equation: **0.60 ≤ Cv ≤ 13.00**,
**2° ≤ τ ≤ 15°**, **λ ≤ 4**. Savitsky additionally restricts the
computational procedure to **Cv ≥ 1.0**.

Two consequences worth stating explicitly in the write-up:

1. **Below roughly 9 mph our boat is not planing**, so these equations do
   not describe it. Planing inception is around `Cv/√λ ≈ 1` (for τ ≥ 4°),
   which for λ ≈ 3 puts it at ~8.6 mph. The hump region below that — where
   resistance peaks and the bow rises — is outside the model entirely. That
   is the `pre_planing_resistance` future hook, and it matters because the
   boat has to get *through* the hump before it reaches its design speed.
2. **The trim and λ limits are outputs, not inputs**, so they can only be
   checked after solving. The code flags `OUT_OF_VALID_RANGE` rather than
   silently returning a number from outside the fitted envelope.

### D1. Prismatic-hull assumption

The whole method assumes **constant deadrise, constant beam, constant trim**
over the wetted length. A real hull with warped sections or varying beam has
to be reduced to an equivalent prismatic one (the paper uses "average"
values for b and β in its example without saying how they were averaged).
Choosing those averages for our hull is a modelling decision we will have to
make and defend.

### D2. Flat-plate and V-bottom wave rise disagree

Setting β = 0 in the V-bottom wetted-length relation (eq. 5) gives no wave
rise at all, contradicting the flat-plate relation (eq. 1), which adds 0.30
beams. The two are separate tracks in the paper and the solver uses only the
V-bottom one. A known limitation of the formulation, not a transcription
error.
**Found in:** Batch 2.

### D3. The deadrise lift correction misbehaves at very light loading

Eq. (16) is not monotonic near zero — its slope vanishes at
`CL0 = (0.0039·β)^2.5`, below which it runs backwards and inverting it is
ambiguous. Irrelevant at β = 10° (turning point CL0 = 3×10⁻⁴), but the
threshold grows with deadrise, so a high-deadrise hull at very light loading
could reach it. Our inverse brackets above the turning point so the root
stays unique.
**Found in:** Batch 3.
