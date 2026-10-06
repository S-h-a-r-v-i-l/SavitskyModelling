"""Batch 7: simple-case trim equilibrium, eq. (37) of Savitsky (1964)."""

import pytest

from savitsky import center_of_pressure, equilibrium_simple, lift

FT = 0.3048

# Paper's worked example, reduced to what the trim solve needs.
CV_EXAMPLE = 3.18
BEAM_EXAMPLE = 14.0 * FT
LCG_EXAMPLE = 29.0 * FT
CL0_EXAMPLE = lift.solve_cl0_from_cl_beta(0.069, 10.0)


class TestMinimumFeasibleTrim:
    @pytest.mark.parametrize("cv", [1.0, 3.18, 8.0])
    def test_is_the_trim_at_which_lambda_hits_the_search_ceiling(self, cv):
        # Below this trim lift.solve_lambda_from_cl0 has no root to find.
        tau = equilibrium_simple.minimum_feasible_trim(CL0_EXAMPLE, cv, lam_max=10.0)
        assert lift.solve_lambda_from_cl0(
            CL0_EXAMPLE, tau, cv, lam_max=10.0
        ) == pytest.approx(10.0, rel=1e-6)

    def test_rises_with_load(self):
        # A more heavily loaded hull needs more trim before its required
        # wetted length comes back inside the search range.
        light = equilibrium_simple.minimum_feasible_trim(0.02, 3.18)
        heavy = equilibrium_simple.minimum_feasible_trim(0.10, 3.18)
        assert heavy > light


class TestTrimResidual:
    def test_is_strictly_decreasing_in_trim(self):
        # The guarantee that makes the root unique: see module docstring.
        values = [
            equilibrium_simple.trim_residual(
                tau, CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, LCG_EXAMPLE
            )
            for tau in (1.0, 2.0, 3.0, 5.0, 8.0, 12.0)
        ]
        assert values == sorted(values, reverse=True)

    def test_is_zero_at_the_solved_trim(self):
        tau = equilibrium_simple.solve_trim(
            CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, LCG_EXAMPLE
        )
        assert equilibrium_simple.trim_residual(
            tau, CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, LCG_EXAMPLE
        ) == pytest.approx(0.0, abs=1e-9)

    def test_sign_means_bow_up_or_down(self):
        # Positive residual = pressure force forward of the CG = bow-up.
        tau = equilibrium_simple.solve_trim(
            CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, LCG_EXAMPLE
        )
        below = equilibrium_simple.trim_residual(
            tau - 0.5, CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, LCG_EXAMPLE
        )
        above = equilibrium_simple.trim_residual(
            tau + 0.5, CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, LCG_EXAMPLE
        )
        assert below > 0.0 > above


class TestSolveTrim:
    def test_puts_the_centre_of_pressure_over_the_cg(self):
        # This is eq. (37) itself: lambda*Cp*b == LCG.
        tau = equilibrium_simple.solve_trim(
            CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, LCG_EXAMPLE
        )
        lam = lift.solve_lambda_from_cl0(CL0_EXAMPLE, tau, CV_EXAMPLE)
        lp = center_of_pressure.center_of_pressure_distance(lam, CV_EXAMPLE, BEAM_EXAMPLE)
        assert lp == pytest.approx(LCG_EXAMPLE)

    def test_reproduces_the_paper_example_trim(self):
        # Table 2 reads tau = 2.23 deg off the Fig. 19 nomogram.
        tau = equilibrium_simple.solve_trim(
            CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, LCG_EXAMPLE
        )
        assert tau == pytest.approx(2.23, rel=0.03)

    def test_moving_the_cg_aft_raises_trim(self):
        # One of the project's stated trend requirements, and the standard
        # trick for trimming a planing boat.
        trims = [
            equilibrium_simple.solve_trim(
                CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, lcg * FT
            )
            for lcg in (32.0, 29.0, 26.0, 23.0)
        ]
        assert trims == sorted(trims)

    def test_raises_when_cg_is_too_far_forward(self):
        with pytest.raises(ValueError, match="forward of the furthest-forward"):
            equilibrium_simple.solve_trim(
                CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, 100.0 * FT
            )

    def test_raises_when_cg_is_too_far_aft(self):
        with pytest.raises(ValueError, match="aft of the centre of pressure"):
            equilibrium_simple.solve_trim(
                CL0_EXAMPLE, CV_EXAMPLE, BEAM_EXAMPLE, 0.01 * FT
            )
