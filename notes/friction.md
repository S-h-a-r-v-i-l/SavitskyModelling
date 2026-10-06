# `src/savitsky/friction.py`

**Summary.** Everything needed to get a friction coefficient and the
velocity it acts at. Public API: `FrictionLine` enum
(`SCHOENHERR` / `ITTC57`), `schoenherr_friction_coefficient(re)`,
`ittc57_friction_coefficient(re)`, `friction_coefficient(re, line,
roughness_allowance)` (the dispatcher, adds the roughness allowance),
`average_bottom_velocity_ratio(tau_deg, lam, beta_deg)` (V1/V),
`average_bottom_velocity(speed, ...)` (V1), and
`reynolds_number(v1, lam, beam, nu)`.

**Equation(s).** Mixed provenance -- important for the write-up:
- (23): `V1 = V*sqrt(1 - 2*pd/(rho*V^2))` -- Bernoulli between free
  stream and the mean bottom pressure.
- (24): `V1 = V*sqrt(1 - 0.0120*tau^1.1/(lambda^0.5*cos(tau)))`, the
  zero-deadrise closed form, obtained by substituting eq. (22)'s mean
  dynamic pressure into (23).
- Fig. 14 generalises this to deadrise with an `f(beta)` factor:
  `V1/V = sqrt(1 - (0.0120*tau^1.1/(lambda^0.5*cos(tau)))*f(beta))`.
- **Schoenherr and ITTC-57 are NOT Savitsky equations.** The paper cites
  Schoenherr as ref. [14] and reads Cf off a chart; it never writes the
  formula. Implemented here as the documented external standard
  `0.242/sqrt(Cf) = log10(Re*Cf)` (implicit, hence a Brent solve).
  ITTC-57 `Cf = 0.075/(log10(Re)-2)^2` is offered as the modern
  alternative. The ATTC roughness allowance (dCf = 0.0004 in the paper's
  examples) is a quoted table value with no formula, so it is a plain
  caller input defaulting to zero.

**Role in the model.** Supplies the two things [[drag]] needs for eq.
(19)/(25): the friction coefficient Cf and the velocity V1 it acts at.
Called once per trial trim inside the Batch 7 root-find, since V1 depends
on tau and lambda. Note `reynolds_number` uses the **mean wetted length
lambda*b** as its length scale and **V1, not V**, as its velocity -- both
easy to get wrong.

**The deadrise generalisation of V1/V -- a judgement call, documented.**
The paper prints eq. (24) for beta = 0 only and shows `f(beta)` on Fig. 14
without defining it. We implement `f(beta) = CLd_beta/CLd`, i.e. eq. (16)'s
deadrise correction applied to the *dynamic* lift component
`CLd = 0.0120*lambda^0.5*tau^1.1` of eq. (20). Justification:
1. The text says exactly this -- the deadrise V1 "is computed in an
   analogous manner using the lift coefficient for deadrise surfaces
   given by (16)" (p. 83).
2. It reduces to eq. (24) exactly at beta = 0.
3. It reproduces Fig. 14 at `lambda = 1.0`, where the curves are actually
   readable: computed 0.885 / 0.901 / 0.917 at `tau = 15` for
   beta = 10 / 20 / 30 against chart reads of ~0.89 / 0.90 / 0.915, with
   the correct trend direction (higher deadrise sits higher, because less
   lift means less bottom pressure means V1 nearer V).

Caveat recorded honestly: against Table 1's Vm row this runs about +0.3%
high, whereas dropping the deadrise correction entirely would land within
0.12%. We kept the deadrise version anyway, because Table 1's points sit
at the top of Fig. 14 (V1/V ~ 0.99) where the curves bunch and the whole
beta = 0 to beta = 10 spread is only 0.0014 in V1/V -- smaller than the
chart can be read to. The readable end of the chart is the better
evidence, and it favours the deadrise form.

**Status.** Implemented and validated (Batch 4). 43 tests in
`tests/test_friction.py`: Schoenherr satisfies its own implicit
definition across six decades of Re; Table 1's Cf row reproduced to
within 0.3% (Table 2's `.00177` exactly); row 9 (Cf + dCf) within 0.4%;
Re within 0.5%; Vm within 0.33%; Fig. 14 reads within 0.006.
