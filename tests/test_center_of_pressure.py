"""Batch 6: centre of pressure, eq. (28) of Savitsky (1964).

The strongest evidence here is structural rather than numerical. Fig. 17
is just a plot of eq. (28) with the equation printed on it, so reading
points off it would test nothing the formula does not state. Instead:

1. **Asymptotic limits against the paper's prose.** The text (p. 85) says
   the dynamic lift acts at 75% of the mean wetted length forward of the
   transom and the buoyant lift at 33%. Eq. (28) must collapse to exactly
   those two numbers at high and vanishing speed -- an independent check,
   since those percentages come from the text, not from the formula.
2. **Table 2's internal cross-check.** That table never reads Cp off a
   chart; it fixes lp/b = LCG/b = 2.07 and lambda = 3.45, which implies
   Cp = 0.600. Eq. (28) must reproduce that.
3. **Table 1 row 17**, which *is* a Fig. 17 chart read, so it gets a
   looser tolerance (observed -1.4% / +0.3% / -1.0%).
"""

import pytest

from savitsky import center_of_pressure as cop

CV_EXAMPLE = 3.18
BEAM_EXAMPLE = 14.0 * 0.3048


class TestAsymptoticLimits:
    """Eq. (28) against the physical statements it was built from."""

    def test_approaches_dynamic_centre_at_high_speed(self):
        # p. 85: dynamic lift acts at 75% of mean wetted length.
        assert cop.center_of_pressure_ratio(3.0, 1e9) == pytest.approx(0.75)

    def test_approaches_buoyant_centre_at_vanishing_speed(self):
        # p. 85: buoyant lift acts at 33% forward of the transom.
        # 0.75 - 1/2.39 = 0.3316, i.e. the paper's "33 percent".
        assert cop.center_of_pressure_ratio(3.0, 1e-9) == pytest.approx(0.33, abs=0.005)

    def test_stays_between_the_two_limits(self):
        for lam in (0.5, 1.0, 2.5, 4.0):
            for cv in (0.6, 1.0, 3.18, 8.0, 13.0):
                assert 0.33 <= cop.center_of_pressure_ratio(lam, cv) <= 0.75

    def test_moves_forward_as_speed_rises(self):
        # More of the lift becomes dynamic, so the resultant shifts from
        # the buoyant 33% toward the dynamic 75%.
        values = [cop.center_of_pressure_ratio(3.0, cv) for cv in (1.0, 2.0, 4.0, 8.0)]
        assert values == sorted(values)

    def test_moves_aft_as_wetted_length_grows(self):
        # Longer wetted length at fixed speed means relatively more buoyant
        # lift, pulling the centre of pressure back toward 33%.
        values = [cop.center_of_pressure_ratio(lam, 3.18) for lam in (1.0, 2.0, 3.0, 4.0)]
        assert values == sorted(values, reverse=True)


class TestAgainstWorkedExamples:
    def test_matches_table2_implied_value(self):
        # Table 2 fixes lp/b = LCG/b = 2.07 at lambda = 3.45, so its own
        # numbers imply Cp = 2.07/3.45 = 0.600 with no chart involved.
        implied = 2.07 / 3.45
        assert cop.center_of_pressure_ratio(3.45, CV_EXAMPLE) == pytest.approx(
            implied, rel=0.01
        )

    @pytest.mark.parametrize(
        "lam, cp_from_fig17", [(3.85, 0.59), (2.60, 0.65), (1.86, 0.70)]
    )
    def test_against_table1_row17(self, lam, cp_from_fig17):
        # Fig. 17 chart reads; observed deviations -1.4% / +0.3% / -1.0%.
        assert cop.center_of_pressure_ratio(lam, CV_EXAMPLE) == pytest.approx(
            cp_from_fig17, rel=0.015
        )


class TestCenterOfPressureDistance:
    def test_is_ratio_times_mean_wetted_length(self):
        lam, cv, beam = 3.0, 3.18, 0.5
        assert cop.center_of_pressure_distance(lam, cv, beam) == pytest.approx(
            cop.center_of_pressure_ratio(lam, cv) * lam * beam
        )

    def test_reproduces_table2_lcg(self):
        # The whole point of the simple case: at equilibrium lp equals the
        # LCG. Table 2's converged lambda = 3.45 should put lp at 29 ft.
        lp = cop.center_of_pressure_distance(3.45, CV_EXAMPLE, BEAM_EXAMPLE)
        assert lp / 0.3048 == pytest.approx(29.0, rel=0.01)

    def test_scales_with_beam(self):
        single = cop.center_of_pressure_distance(3.0, 3.18, 0.5)
        assert cop.center_of_pressure_distance(3.0, 3.18, 1.0) == pytest.approx(
            2.0 * single
        )
