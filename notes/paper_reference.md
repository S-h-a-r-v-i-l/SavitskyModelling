# Paper reference data — Savitsky (1964)

Consolidated reference so later batches can be validated **without
re-reading the PDF**. Everything here is either (a) transcribed directly
from the paper and marked PRINTED, or (b) derived by us from the paper's
own numbers and marked DERIVED with the supporting evidence. Nothing here
is a guess; if something isn't known it says so.

Source: D. Savitsky, "Hydrodynamic Design of Planing Hulls," *Marine
Technology*, Vol. 1, No. 1, Oct. 1964, pp. 71-95. Local copy:
`refs/Hydrodynamic Design of Planing Hulls - Savitsky 1964.pdf`
(25 pages, **no OCR text layer** — `pdftotext` returns nothing; render
pages to images with `pymupdf` to read them).

## PDF page map

Journal page = PDF page + 70. Useful targets:

| Content | PDF page |
|---|---|
| Nomenclature | 1 |
| Fig. 3 (wave rise, eq. 1) | 3 |
| Fig. 6 (Lk−Lc vs trim), eq. (2) | 5-6 |
| Eq. (3), (4), (5) | 7 |
| Eq. (6), (7), K factor | 8 |
| **Eq. (8)-(15)**, Fig. 9 | 9 |
| Fig. 10 (CL0/τ^1.1 vs λ) + τ^1.1 inset table | 10 |
| Fig. 11 (CLβ vs CL0) | 11 |
| **Eq. (16)**, Fig. 12 | 12 |
| **Eq. (17)-(25)**, Fig. 13 | 13 |
| Eq. (26), (27) | 14 |
| Fig. 14 (V1/V), **eq. (28)** | 15 |
| Fig. 15 | 16 |
| Fig. 16 | 17 |
| **Eq. (29)-(31)** + force/moment sketch | 18 |
| **Table 1** (general case worked example) | 19 |
| **Table 2** (simple case worked example), eq. (32) | 20 |
| Fig. 17 (Cp), **eq. (33)-(37)** | 21 |
| **Fig. 18** (porpoising limits) | 22 |
| Fig. 19 (Koelbel nomogram) | 23 |

Render recipe:

```python
import pymupdf
doc = pymupdf.open("refs/Hydrodynamic Design of Planing Hulls - Savitsky 1964.pdf")
doc[18].get_pixmap(matrix=pymupdf.Matrix(220/72, 220/72)).save("page_19.png")  # 0-indexed
```

## Worked example — shared inputs (Tables 1 and 2)

PRINTED. Both tables use the same hull and speed; they differ only in
whether the thrust line and friction lever are offset from the CG.

| Quantity | Value (imperial, as printed) | SI |
|---|---|---|
| Δ (weight) | 60,000 lb | 266,893 N |
| LCG (from transom, along keel) | 29.0 ft | 8.8392 m |
| VCG (above keel, normal to keel) | 2.0 ft | 0.6096 m |
| b (beam, average) | 14 ft | 4.2672 m |
| β (deadrise, average) | 10° | — |
| V | 40 knots = 67.5 ft/s | 20.574 m/s |
| Cv = V/√(gb) | 3.18 | same (dimensionless) |
| CLβ = Δ/(½ρV²b²) | 0.069 | same (dimensionless) |

Table 1 only (general case): `a = 1.39 ft`, `f = 0.50 ft`, `ε = 4°`.
Table 2 only (simple case): `a = c = f = ε = 0`.

Conversion used in tests: `FT = 0.3048`, `lbf = 4.448222 N`,
`1 knot = 1.68781 ft/s` (the paper rounds to 1.69), `g = 32.2 ft/s²`
(the paper's value; SI standard 9.80665 differs by 0.07%).

## Water properties used by the worked example

**DERIVED** — the paper never states ρ or ν explicitly, but both follow
from its own numbers. This matters: using our `FRESH_WATER` preset
instead will *not* reproduce the paper's Re or Cf.

**ρ = 1.94 slug/ft³ = 999.8 kg/m³ (fresh water).** Evidence: the printed
CLβ line reads `60,000 / 0.97 × 67.5² × 14² = 0.069`, so ½ρ = 0.97
slug/ft³ ⟹ ρ = 1.94. Recomputing gives CLβ = 0.06927, consistent with
the printed 0.069.

**ν = 1.00×10⁻⁵ ft²/s = 9.29×10⁻⁷ m²/s.** Evidence: inverting
`Re = Vm·λ·b/ν` on all four printed Re values independently:

| Case | Vm (fps) | λ | Re printed | ν implied (ft²/s) |
|---|---|---|---|---|
| T1 τ=2° | 67.0 | 3.85 | 3.61×10⁸ | 1.000×10⁻⁵ |
| T1 τ=3° | 66.6 | 2.60 | 2.42×10⁸ | 1.002×10⁻⁵ |
| T1 τ=4° | 66.2 | 1.86 | 1.73×10⁸ | 0.996×10⁻⁵ |
| T2 τ=2.23° | 66.9 | 3.45 | 3.22×10⁸ | 1.004×10⁻⁵ |

All four agree within 0.4%, so this is a solid inference. Note
`Re = Vm·λ·b/ν` uses the **mean wetted length λb**, not the beam alone.

> **Warning for Batch 4.** Our `constants.FRESH_WATER` preset has
> ν = 1.004×10⁻⁶ m²/s (= 1.081×10⁻⁵ ft²/s, water at ~20 °C). That yields
> Re = 3.34×10⁸ for the T1 τ=2° case versus the paper's 3.61×10⁸ — 7.4%
> low, which shifts Cf by roughly 1%. Paper-reproduction tests must pass
> the paper's ν explicitly rather than relying on the preset.

Roughness allowance: **ΔCf = 0.0004**, PRINTED, sourced in the table as
"ATTC Standard Roughness". A quoted table value, not a formula.

## Table 2 — simple case, all forces through CG (PDF p. 20)

PRINTED. This is the Batch 7 validation target.

| Row | Quantity | Source | Value |
|---|---|---|---|
| 1 | CL0 | Fig. 11 | .085 |
| 2 | lp/b | LCG/b | 2.07 |
| 3 | λ | Fig. 19 | 3.45 |
| 4 | CL0/τ^1.1 | Fig. 19 | .035 |
| 5 | τ^1.1 | (1)/(4) | 2.42 |
| 6 | **τ** | — | **2.23°** |
| 7 | tanτ | — | .039 |
| 8 | Δ tanτ | — | 2,340 |
| 9 | λb² | (3)·b² | 675 |
| 10 | Vm | Fig. 14 | 66.9 |
| 11 | Re | Vm·λ·b/ν | 3.22×10⁸ |
| 12 | Cf | Schoenherr | .00177 |
| 13 | ΔCf | ATTC Std Roughness | .0004 |
| 14 | Cf + ΔCf | (12)+(13) | .00217 |
| 15 | Df | ρVm²λb²(Cf+ΔCf)/(2cosβ) | 6,670 |
| 16 | Df/cosτ | — | 6,670 |
| 17 | **D** | (8)+(16) | **9,010** |
| 18 | **EHP** | D·V/550 | **1,100** |
| 19 | √(CLβ/2) | — | .186 |
| 20 | τ porpoising | Fig. 18 | ≤4.5° → **stable** |

Row 17's source cell is printed as "(8) + (17)", a typo for (8)+(16);
2,340 + 6,670 = 9,010 confirms the intent.

## Table 1 — general case (PDF p. 19)

PRINTED. Three trial trims; eq. (35) residual (row 30) is interpolated
to zero. This is the Batch 9 validation target.

| Row | Quantity | Source | τ=2° | τ=3° | τ=4° |
|---|---|---|---|---|---|
| 1 | τ^1.1 | inset table | 2.14 | 3.35 | 4.59 |
| 2 | CL0 | Fig. 11 | .085 | .085 | .085 |
| 3 | CL0/τ^1.1 | (2)/(1) | .0397 | .0254 | .0185 |
| 4 | λ | Fig. 10 | 3.85 | 2.60 | 1.86 |
| 5 | Vm | Fig. 14 | 67.0 | 66.6 | 66.2 |
| 6 | Re | Vm·λ·b/ν | 3.61×10⁸ | 2.42×10⁸ | 1.73×10⁸ |
| 7 | Cf | Schoenherr | .00174 | .00184 | .00192 |
| 8 | ΔCf | ATTC Std Roughness | .0004 | .0004 | .0004 |
| 9 | Cf+ΔCf | (7)+(8) | .00214 | .00224 | .00232 |
| 10 | Df | ρVm²λb²(Cf+ΔCf)/(2cosβ) | 7,340 | 5,160 | 3,760 |
| 11 | tanτ | — | .0349 | .0524 | .0698 |
| 12 | sinτ | — | .0349 | .0524 | .0698 |
| 13 | cosτ | — | .9994 | .9986 | .9976 |
| 14 | Δ tanτ | — | 2,094 | 3,144 | 4,188 |
| 15 | Df/cosτ | (10)/cosτ | 7,340 | 5,160 | 3,760 |
| 16 | D | (14)+(15) | 9,434 | 8,304 | 7,948 |
| 17 | Cp | Fig. 17 | .59 | .65 | .70 |
| 18 | Cp·λ·b | — | 31.6 | 23.5 | 18.2 |
| 19 | c | LCG − (18) | −2.6 | 5.5 | 10.8 |
| 20 | (b/4)tanβ | — | .616 | .616 | .616 |
| 21 | a | VCG − (20) | 1.39 | 1.39 | 1.39 |
| 22 | sin(τ+ε) | — | .1045 | .1219 | .1392 |
| 23 | 1 − sinτ·sin(τ+ε) | 1 − (12)(22) | .9964 | .9964 | .9903 |
| 24 | (23)·(c/cosτ) | — | −2.59 | 5.46 | 10.70 |
| 25 | f·sinτ | — | .0174 | .0262 | .0349 |
| 26 | (24) − (25) | — | −2.6 | 5.53 | 10.73 |
| 27 | Δ·(26) | — | −156,500 | 332,000 | 645,000 |
| 28 | (a − f) | (21) − f | .89 | .89 | .89 |
| 29 | Df(a − f) | (10)(28) | 6,540 | 4,600 | 3,350 |
| 30 | **(27)+(29)** | **eq. (35)** | **−149,960** | **336,600** | **648,350** |

Results printed alongside the table:

- τe = 2° + 149,960/(149,960 + 336,600) ≈ **2.3°** (linear interpolation
  on the eq. 35 residual between τ=2° and τ=3°)
- D = 9,434 − (9,434 − 8,304)(3/10) = **9,095 lb** (printed as "9424" in
  the first term, a typo for 9,434)
- EHP = D·V/550 = 9,095 × 67.5/550 = **1,115 hp**
- λe = **3.29** — *see known errors below*
- Lk = λe·b + (b tanβ)/(2π tanτ) = **55.9 ft**
- Lc = λe·b − (b tanβ)/(2π tanτ) = **36.1 ft**
- d = Lk·sinτe = **2.24 ft**
- √(CLβ/2) = √(0.0345) = **0.186**; Fig. 18 gives porpoising above
  τ ≈ 4.5°, so the boat is **stable**

Note row 21: `a = VCG − (b/4)tanβ`, i.e. the friction lever arm is
measured from the CG down to the line of action of Df, which the paper
places midway between keel and chine (hence b/4, not b/2).

## Known errors and discrepancies in the paper

Recorded so later batches don't "fix" our code to chase a bad number.

1. **Table 1's λe is wrong (affects Batch 9).** The paper prints
   `λe = 3.85 − (3.85 − 2.60)(3/10) = 3.29`, but that arithmetic gives
   **3.475**. We verified that the two endpoint λ values (3.85 at τ=2°,
   2.60 at τ=3°) *are* consistent with eq. (15) at CL0 = .085, Cv = 3.18,
   so the error is in the interpolation step alone. Solving eq. (15)
   directly at τ = 2.3° gives λ ≈ **3.42** (λ-vs-τ is nonlinear, so the
   direct solve differs from linear interpolation's 3.475 too). The paper
   then carries 3.29 downstream consistently (`Lk = 46 + …`, and
   46/14 = 3.286). **Expect our Batch 9 solver to land near λ ≈ 3.42 and
   produce Lk/Lc about 4% off Table 1's printed values. That is the
   paper's error, not ours.**

2. **The tables mix two water densities (seen in Batch 5).** Inverting
   eq. (19) on all four printed Df values backs out
   rho = 1.994 / 2.007 / 1.998 / 2.000 slug/ft^3 (Table 1's three trim
   columns, then Table 2) -- i.e. the drag rows were computed with
   **rho = 2.00 slug/ft^3**, a rounded seawater value. But the CLbeta
   line at the head of the same tables reads
   `60,000 / 0.97 x 67.5^2 x 14^2`, and 0.97 is rho/2 for **fresh**
   water, rho = 1.94. The two differ by 3%. Using 1.94 in eq. (19)
   undershoots the paper's own printed Df by about 3% at every trim.
   **Consequence for Batches 7 and 9:** a single self-consistent density
   cannot reproduce both the printed CLbeta and the printed Df. Decide
   which to match and say so; our drag tests use 2.00 slug/ft^3 because
   that is what the drag rows were actually computed with. Our library
   takes density as an input, so neither value is baked in.

3. **Table 1's Lc is ~0.5% off its own inputs (seen in Batch 2).**
   Carrying the paper's stated λe = 3.29, b = 14 ft, β = 10°, τe = 2.3°
   at full precision gives Lc = 36.28 ft, but 36.1 ft is printed. Lk
   (−0.10%) and d (+0.05%) match closely, so this is isolated hand
   arithmetic, not a formula difference.

4. **Typos (harmless, intent unambiguous):** Table 1's drag line prints
   "9424" for 9,434; Table 2 row 17's source prints "(8) + (17)" for
   (8)+(16).

5. **Eq. (1) vs eq. (5) disagree at β = 0** (seen in Batch 2). Eq. (5)
   gives λ = λ₁ (no wave rise) for a flat plate, while eq. (1) gives
   λ = λ₁ + 0.30. Known limitation of the deadrise formulation; the two
   are separate tracks and eq. (1) is not used in the solver path.

## Cross-checks that don't need the PDF

- **τ^1.1 inset table** (Fig. 10, PDF p. 10) is simply τ^1.1 evaluated at
  integer trims: 2→2.14, 3→3.35, 4→4.59, 5→5.87, 6→7.18, 7→8.50, 8→9.85,
  9→11.21, 10→12.59, 11→13.98, 12→15.39, 13→16.80, 14→18.23, 15→19.67.
  Verified against `tau**1.1` — no lookup needed, use the power directly.
- **Eq. (16) self-check:** CL0 = .085, β = 10° gives
  CLβ = .085 − 0.0065(10)(.085^0.60) = 0.0702, versus the example's
  CLβ = 0.069 (1.7% apart, consistent with CL0 = .085 having been read
  off Fig. 11 by eye).

## Validity ranges (PRINTED)

- Eq. (15)/(16) lift: **0.60 ≤ Cv ≤ 13.00, 2° ≤ τ ≤ 15°, λ ≤ 4**.
- Eq. (1) wave rise: trim 2° to 24°, λ ≤ 4.0, 0.60 ≤ Cv ≤ 25.00.
- Eq. (3) applies for all deadrise/trim combinations when Cv > 2.0; it
  begins to break down at Cv ≈ 1.0 when the spray-root angle
  γ = arctan(tanτ / (2 tanβ)) falls below about 17°.
- Savitsky's own guidance: the computational procedures are carried out
  "with the restriction that Cv ≥ 1.0".
