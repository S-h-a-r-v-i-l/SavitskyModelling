"""Batch 2: wetted-length geometry, eq. (1)-(5) of Savitsky (1964).

Validation sources, in decreasing order of strength:
  * algebraic identities the paper states explicitly (eq. 3 = 2/pi * eq. 2,
    continuity of eq. 1's two branches),
  * points read off Fig. 3 and Fig. 6 of the paper (reading precision is
    about +/- 0.05 beams, which sets the tolerance on those tests),
  * the worked example in Table 1 (imperial; converted to SI here only --
    the library itself is SI throughout).
"""

import math

import pytest

from savitsky import geometry

FT = 0.3048  # Imperial -> SI. Confined to tests, per project convention.


class TestWaveRise:
    """Eq. (1), flat planing surfaces."""

    def test_quadratic_branch_matches_published_coefficients(self):
        # lambda = 1.60*0.5 - 0.30*0.25
        assert geometry.lambda_from_lambda1(0.5) == pytest.approx(0.725)

    def test_branches_agree_at_the_junction(self):
        # Both branches of eq. (1) are stated as valid at lambda_1 = 1.
        quadratic = 1.60 * 1.0 - 0.30 * 1.0**2
        linear = 1.0 + 0.30
        assert quadratic == pytest.approx(linear)
        assert geometry.lambda_from_lambda1(1.0) == pytest.approx(1.30)

    @pytest.mark.parametrize("lambda1, lam_from_fig3", [(2.0, 2.30), (3.0, 3.30)])
    def test_linear_branch_against_fig3(self, lambda1, lam_from_fig3):
        # Fig. 3: above lambda_1 = 1 the fitted curve sits a constant 0.30
        # beams to the right of the lambda_1 = lambda diagonal.
        assert geometry.lambda_from_lambda1(lambda1) == pytest.approx(
            lam_from_fig3, abs=0.05
        )

    @pytest.mark.parametrize("lambda1", [0.0, 0.25, 0.5, 0.75, 1.0, 2.0, 3.5, 4.0])
    def test_inverse_round_trips(self, lambda1):
        lam = geometry.lambda_from_lambda1(lambda1)
        assert geometry.lambda1_from_lambda(lam) == pytest.approx(lambda1, abs=1e-12)


class TestKeelChineDifference:
    """Eq. (2) and (3)."""

    @pytest.mark.parametrize("tau_deg, beta_deg", [(4.0, 10.0), (8.0, 20.0)])
    def test_eq3_is_two_over_pi_times_eq2(self, tau_deg, beta_deg):
        # The paper states eq. (3) is 2/pi times the level-water value,
        # that ratio being Wagner's pi/2 wave-rise factor.
        beam = 1.0
        level_water = geometry.level_water_keel_chine_difference(
            beam, tau_deg, beta_deg
        )
        actual = geometry.keel_chine_difference(beam, tau_deg, beta_deg)
        assert actual / level_water == pytest.approx(2.0 / math.pi)

    @pytest.mark.parametrize(
        "tau_deg, beta_deg, beams_from_fig6",
        [
            (8.0, 40.0, 1.90),
            (8.0, 20.0, 0.82),
            (8.0, 10.0, 0.40),
            (20.0, 40.0, 0.73),
        ],
    )
    def test_against_fig6(self, tau_deg, beta_deg, beams_from_fig6):
        # Fig. 6 plots (Lk - Lc) in beams against trim, one curve per
        # deadrise. Values read off the chart; tolerance is chart-reading
        # precision, not solver precision.
        beam = 1.0
        assert geometry.keel_chine_difference(
            beam, tau_deg, beta_deg
        ) == pytest.approx(beams_from_fig6, abs=0.05)

    def test_scales_linearly_with_beam(self):
        single = geometry.keel_chine_difference(1.0, 5.0, 15.0)
        assert geometry.keel_chine_difference(4.0, 5.0, 15.0) == pytest.approx(
            4.0 * single
        )

    def test_vanishes_for_zero_deadrise(self):
        # A flat plate wets keel and chine at the same station.
        assert geometry.keel_chine_difference(2.0, 5.0, 0.0) == pytest.approx(0.0)


class TestKeelLengthAndDraft:
    """Eq. (4)."""

    def test_round_trips(self):
        keel_length = geometry.keel_length_from_draft(0.5, 4.0)
        assert geometry.draft_from_keel_length(keel_length, 4.0) == pytest.approx(0.5)

    def test_matches_published_form(self):
        # Lk = d / sin(tau)
        assert geometry.keel_length_from_draft(0.5, 4.0) == pytest.approx(
            0.5 / math.sin(math.radians(4.0))
        )


class TestMeanWettedLengthRatio:
    """Eq. (5)."""

    def test_wetted_lengths_round_trip_through_lambda(self):
        lam, beam, tau_deg, beta_deg = 2.5, 0.5, 5.0, 18.0
        keel_length, chine_length = geometry.wetted_lengths(
            lam, beam, tau_deg, beta_deg
        )
        assert geometry.mean_wetted_length_ratio(
            keel_length, chine_length, beam
        ) == pytest.approx(lam)

    def test_wetted_lengths_differ_by_eq3(self):
        beam, tau_deg, beta_deg = 0.5, 5.0, 18.0
        keel_length, chine_length = geometry.wetted_lengths(
            2.5, beam, tau_deg, beta_deg
        )
        assert keel_length - chine_length == pytest.approx(
            geometry.keel_chine_difference(beam, tau_deg, beta_deg)
        )

    def test_published_draft_form_matches_composition(self):
        # Eq. (5) written directly in terms of draft must agree with going
        # the long way round: draft -> Lk (eq. 4) -> Lc (eq. 3) -> lambda.
        draft, beam, tau_deg, beta_deg = 0.4, 0.5, 6.0, 15.0
        direct = geometry.mean_wetted_length_ratio_from_draft(
            draft, beam, tau_deg, beta_deg
        )
        keel_length = geometry.keel_length_from_draft(draft, tau_deg)
        chine_length = keel_length - geometry.keel_chine_difference(
            beam, tau_deg, beta_deg
        )
        composed = geometry.mean_wetted_length_ratio(keel_length, chine_length, beam)
        assert direct == pytest.approx(composed)

    def test_negative_chine_length_is_returned_unclamped(self):
        # Dry chines: lambda*b smaller than half the eq. (3) difference.
        # geometry reports the raw value; flagging is the caller's job.
        _, chine_length = geometry.wetted_lengths(0.05, 1.0, 2.0, 30.0)
        assert chine_length < 0.0


class TestPaperTable1Geometry:
    """Worked example, Table 1 (general case), p. 89.

    Given there: lambda_e = 3.29, b = 14 ft, beta = 10 deg, tau_e = 2.3 deg.
    Published results: Lk = 55.9 ft, Lc = 36.1 ft, d = 2.24 ft.

    Tolerance is 1%: the paper's hand arithmetic carries roughly half a
    percent of slop here (its own Lc works out to 36.2-36.3 ft when the
    stated inputs are carried at full precision).
    """

    LAMBDA_E = 3.29
    BEAM = 14.0 * FT
    BETA_DEG = 10.0
    TAU_E_DEG = 2.3

    def test_wetted_keel_length(self):
        keel_length, _ = geometry.wetted_lengths(
            self.LAMBDA_E, self.BEAM, self.TAU_E_DEG, self.BETA_DEG
        )
        assert keel_length == pytest.approx(55.9 * FT, rel=0.01)

    def test_wetted_chine_length(self):
        _, chine_length = geometry.wetted_lengths(
            self.LAMBDA_E, self.BEAM, self.TAU_E_DEG, self.BETA_DEG
        )
        assert chine_length == pytest.approx(36.1 * FT, rel=0.01)

    def test_transom_draft(self):
        keel_length, _ = geometry.wetted_lengths(
            self.LAMBDA_E, self.BEAM, self.TAU_E_DEG, self.BETA_DEG
        )
        draft = geometry.draft_from_keel_length(keel_length, self.TAU_E_DEG)
        assert draft == pytest.approx(2.24 * FT, rel=0.01)

    def test_lambda_recovered_from_published_lengths(self):
        # Closing the loop the other way: the paper's own Lk and Lc must
        # reproduce its lambda_e through eq. (5).
        lam = geometry.mean_wetted_length_ratio(55.9 * FT, 36.1 * FT, self.BEAM)
        assert lam == pytest.approx(self.LAMBDA_E, rel=0.01)
