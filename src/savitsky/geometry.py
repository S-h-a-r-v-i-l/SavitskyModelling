"""Wetted-length geometry: eq. (1)-(5) of Savitsky (1964).

Two distinct tracks live in this module and they are NOT interchangeable:

* Eq. (1) is the *flat-plate* wave-rise relation, converting the calm-water
  (level-water-surface) length-beam ratio lambda_1 into the running mean
  wetted length-beam ratio lambda. Provided for reference; the deadrise
  computational path below does not use it.
* Eq. (2)-(5) are the *deadrise* relations the solver actually runs on.
  There, wave rise is accounted for transversely by Wagner's pi/2 factor,
  which is exactly why eq. (3) is a factor 2/pi smaller than the
  level-water value of eq. (2). The paper reports no appreciable water
  pile-up along the keel up to roughly tau = 15 deg, so the wetted keel
  length is taken as the plain calm-water value d/sin(tau), eq. (4).

A consequence worth knowing when defending results: setting beta = 0 in
eq. (5) gives lambda = lambda_1, i.e. no wave rise, which disagrees with
eq. (1)'s lambda = lambda_1 + 0.30 for a flat plate. That is a known
limitation of the deadrise formulation, not a transcription error here.

Units: lengths SI (m); angles passed in degrees (Savitsky's empirical fits
are stated in degrees) and converted to radians internally.
"""

import math


def lambda_from_lambda1(lambda1: float) -> float:
    """Running mean wetted length-beam ratio from the calm-water one.

    Eq. (1): lambda = 1.60*lambda_1 - 0.30*lambda_1**2   (0 <= lambda_1 <= 1)
             lambda = lambda_1 + 0.30                    (1 <= lambda_1 <= 4)

    Flat planing surfaces only. Published domain is lambda_1 <= 4; the
    domain is documented, not enforced -- validity flagging belongs to the
    caller (see savitsky.result.ResultFlag.OUT_OF_VALID_RANGE).
    """
    if lambda1 <= 1.0:
        return 1.60 * lambda1 - 0.30 * lambda1**2
    return lambda1 + 0.30


def lambda1_from_lambda(lam: float) -> float:
    """Calm-water length-beam ratio from the running one: inverse of eq. (1).

    Below lambda = 1.30 (the value of eq. (1) at lambda_1 = 1) this inverts
    the quadratic branch, taking the root that lands in [0, 1].
    """
    if lam <= 1.30:
        # 0.30*l1**2 - 1.60*l1 + lam = 0, negative root is the one on [0, 1].
        return (1.60 - math.sqrt(2.56 - 1.2 * lam)) / 0.60
    return lam - 0.30


def level_water_keel_chine_difference(
    beam: float, tau_deg: float, beta_deg: float
) -> float:
    """Keel/chine wetted-length difference at the calm-water intersection, L2.

    Eq. (2): L2 = (b/2) * tan(beta)/tan(tau)

    This is the level-water value, i.e. before the wave-rise correction;
    the load-carrying geometry uses eq. (3) instead.
    """
    tau_rad = math.radians(tau_deg)
    beta_rad = math.radians(beta_deg)
    return 0.5 * beam * math.tan(beta_rad) / math.tan(tau_rad)


def keel_chine_difference(beam: float, tau_deg: float, beta_deg: float) -> float:
    """Actual wetted keel minus wetted chine length, Lk - Lc.

    Eq. (3): Lk - Lc = (b/pi) * tan(beta)/tan(tau)

    A factor 2/pi smaller than the level-water value of eq. (2), which is
    Wagner's pi/2 wave-rise factor applied to the wetted width.
    """
    tau_rad = math.radians(tau_deg)
    beta_rad = math.radians(beta_deg)
    return beam * math.tan(beta_rad) / (math.pi * math.tan(tau_rad))


def keel_length_from_draft(draft: float, tau_deg: float) -> float:
    """Wetted keel length from transom draft.

    Eq. (4): Lk = d / sin(tau)
    """
    return draft / math.sin(math.radians(tau_deg))


def draft_from_keel_length(keel_length: float, tau_deg: float) -> float:
    """Transom draft from wetted keel length: eq. (4) rearranged."""
    return keel_length * math.sin(math.radians(tau_deg))


def mean_wetted_length_ratio(
    keel_length: float, chine_length: float, beam: float
) -> float:
    """Mean wetted length-beam ratio lambda from the two wetted lengths.

    Eq. (5): lambda = (Lk + Lc) / (2b)
    """
    return (keel_length + chine_length) / (2.0 * beam)


def mean_wetted_length_ratio_from_draft(
    draft: float, beam: float, tau_deg: float, beta_deg: float
) -> float:
    """Mean wetted length-beam ratio lambda from transom draft.

    Eq. (5) in its as-published form:
        lambda = [ d/sin(tau) - (b/2pi) * tan(beta)/tan(tau) ] / b
    """
    tau_rad = math.radians(tau_deg)
    beta_rad = math.radians(beta_deg)
    keel_length = draft / math.sin(tau_rad)
    half_difference = beam * math.tan(beta_rad) / (2.0 * math.pi * math.tan(tau_rad))
    return (keel_length - half_difference) / beam


def wetted_lengths(
    lam: float, beam: float, tau_deg: float, beta_deg: float
) -> tuple[float, float]:
    """Wetted keel and chine lengths (Lk, Lc) from lambda.

    Inverts eq. (5) using the eq. (3) difference:
        Lk = lambda*b + (b/2pi) * tan(beta)/tan(tau)
        Lc = lambda*b - (b/2pi) * tan(beta)/tan(tau)

    A non-positive Lc means the chines are dry and the prismatic planing
    assumptions behind eq. (15)/(16) no longer hold. The raw value is
    returned unclamped; flagging that case is the caller's job (see
    savitsky.result.ResultFlag.DRY_CHINES).
    """
    half_difference = 0.5 * keel_chine_difference(beam, tau_deg, beta_deg)
    mean_length = lam * beam
    return mean_length + half_difference, mean_length - half_difference
