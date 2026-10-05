"""Batch 3: planing lift, eq. (15)-(16) of Savitsky (1964).

Validation strategy, strongest evidence first:

1. **Table 1 row 3 (CL0/tau^1.1) is pure arithmetic** -- the paper divides
   row 2 by row 1 with no chart involved -- so our eq. (15) inputs must
   match it to printed precision. This is the sharpest check available.
2. **Algebraic properties** stated in the text: eq. (16) degenerates at
   beta = 0, eq. (15) is monotonic in lambda, and above Cv ~ 10 the
   buoyant term becomes negligible (p. 80).
3. **Chart reads** (Table 1 row 4 lambda from Fig. 10, CL0 from Fig. 11,
   Table 2 lambda from the Fig. 19 nomogram) are the *weakest* evidence,
   because the example's Cv = 3.18 falls between Fig. 10's drawn Cv = 3.0
   and Cv = 4.0 curves and had to be interpolated by eye. Those get loose
   tolerances, plus a bracketing test that is independent of how well the
   original author eyeballed that interpolation.

Measured deviations from the paper's chart reads: lambda +0.6% / +0.4% /
-3.0% at tau = 2/3/4 deg, Table 2 lambda +2.1%, eq. (16) CLbeta +1.7%.
"""

import pytest

from savitsky import lift

# Worked-example planing coefficients shared by Tables 1 and 2 (p. 89-90).
# See notes/paper_reference.md.
CL0_EXAMPLE = 0.085  # Table 1 row 2 / Table 2 row 1, read off Fig. 11
CV_EXAMPLE = 3.18
BETA_EXAMPLE_DEG = 10.0
CL_BETA_EXAMPLE = 0.069


class TestZeroDeadriseLiftCoefficient:
    """Eq. (15)."""

    @pytest.mark.parametrize(
        "tau_deg, printed_ratio", [(2.0, 0.0397), (3.0, 0.0254), (4.0, 0.0185)]
    )
    def test_cl0_over_tau_power_matches_table1_row3(self, tau_deg, printed_ratio):
        # Row 3 = row 2 / row 1, no chart reading, so this pins the tau**1.1
        # factor in eq. (15) to the paper's own arithmetic.
        assert CL0_EXAMPLE / tau_deg**1.1 == pytest.approx(printed_ratio, rel=0.005)

    def test_tau_power_matches_fig10_inset_table(self):
        # Fig. 10's inset tabulates tau**1.1; spot-check three entries.
        assert 2.0**1.1 == pytest.approx(2.14, abs=0.005)
        assert 10.0**1.1 == pytest.approx(12.59, abs=0.005)
        assert 15.0**1.1 == pytest.approx(19.67, abs=0.005)

    def test_is_strictly_increasing_in_lambda(self):
        values = [
            lift.zero_deadrise_lift_coefficient(4.0, lam, 3.18)
            for lam in (0.5, 1.0, 2.0, 3.0, 4.0)
        ]
        assert values == sorted(values)
        assert len(set(values)) == len(values)

    def test_is_strictly_increasing_in_trim(self):
        values = [
            lift.zero_deadrise_lift_coefficient(tau, 2.5, 3.18)
            for tau in (2.0, 4.0, 8.0, 15.0)
        ]
        assert values == sorted(values)

    def test_vanishes_at_zero_wetted_length(self):
        assert lift.zero_deadrise_lift_coefficient(4.0, 0.0, 3.18) == 0.0

    def test_approaches_dynamic_term_only_at_high_cv(self):
        # p. 80: for Cv > 10 the flat-plate lift coefficient reduces to
        # CL = 0.0120 * lambda**0.5 * tau**1.1.
        tau_deg, lam = 5.0, 2.0
        dynamic_only = 0.0120 * lam**0.5 * tau_deg**1.1
        at_cv_10 = lift.zero_deadrise_lift_coefficient(tau_deg, lam, 10.0)
        assert at_cv_10 == pytest.approx(dynamic_only, rel=0.02)
        # and the residual buoyant share keeps shrinking as Cv grows
        at_cv_50 = lift.zero_deadrise_lift_coefficient(tau_deg, lam, 50.0)
        assert abs(at_cv_50 - dynamic_only) < abs(at_cv_10 - dynamic_only)

    def test_buoyant_term_scales_as_inverse_cv_squared(self):
        tau_deg, lam = 5.0, 2.0
        dynamic_only = 0.0120 * lam**0.5 * tau_deg**1.1
        buoyant_at_2 = (
            lift.zero_deadrise_lift_coefficient(tau_deg, lam, 2.0) - dynamic_only
        )
        buoyant_at_4 = (
            lift.zero_deadrise_lift_coefficient(tau_deg, lam, 4.0) - dynamic_only
        )
        assert buoyant_at_2 / buoyant_at_4 == pytest.approx(4.0)


class TestDeadriseLiftCoefficient:
    """Eq. (16)."""

    def test_degenerates_to_cl0_at_zero_deadrise(self):
        assert lift.deadrise_lift_coefficient(0.085, 0.0) == 0.085

    def test_deadrise_reduces_lift(self):
        # Deadrise sweeps the stagnation line aft, cutting stagnation
        # pressure, so CLbeta < CL0 for any beta > 0.
        assert lift.deadrise_lift_coefficient(0.085, 10.0) < 0.085

    def test_decreases_monotonically_with_deadrise(self):
        values = [
            lift.deadrise_lift_coefficient(0.085, beta)
            for beta in (0.0, 10.0, 20.0, 30.0)
        ]
        assert values == sorted(values, reverse=True)

    def test_matches_worked_example(self):
        # CL0 = .085 (Fig. 11 read) and beta = 10 deg give the example's
        # CLbeta = 0.069. The 1.7% gap is the chart read, not the formula.
        assert lift.deadrise_lift_coefficient(
            CL0_EXAMPLE, BETA_EXAMPLE_DEG
        ) == pytest.approx(CL_BETA_EXAMPLE, rel=0.02)


class TestSolveCl0FromClBeta:
    """Inverse of eq. (16)."""

    def test_round_trips(self):
        cl0 = lift.solve_cl0_from_cl_beta(0.069, 10.0)
        assert lift.deadrise_lift_coefficient(cl0, 10.0) == pytest.approx(0.069)

    @pytest.mark.parametrize("beta_deg", [0.0, 5.0, 10.0, 20.0, 30.0])
    def test_round_trips_across_deadrise(self, beta_deg):
        cl0 = lift.solve_cl0_from_cl_beta(0.05, beta_deg)
        assert lift.deadrise_lift_coefficient(cl0, beta_deg) == pytest.approx(0.05)

    def test_identity_at_zero_deadrise(self):
        assert lift.solve_cl0_from_cl_beta(0.069, 0.0) == 0.069

    def test_recovers_the_example_cl0(self):
        # The paper read CL0 = .085 off Fig. 11 for CLbeta = 0.069, beta = 10.
        assert lift.solve_cl0_from_cl_beta(
            CL_BETA_EXAMPLE, BETA_EXAMPLE_DEG
        ) == pytest.approx(CL0_EXAMPLE, rel=0.02)

    def test_raises_when_target_unreachable(self):
        with pytest.raises(ValueError, match="above cl0_max"):
            lift.solve_cl0_from_cl_beta(5.0, 10.0)


class TestSolveLambdaFromCl0:
    """Inverse of eq. (15)."""

    def test_round_trips(self):
        lam = lift.solve_lambda_from_cl0(0.085, 3.0, 3.18)
        assert lift.zero_deadrise_lift_coefficient(3.0, lam, 3.18) == pytest.approx(
            0.085
        )

    @pytest.mark.parametrize("tau_deg", [2.0, 4.0, 8.0, 15.0])
    @pytest.mark.parametrize("cv", [1.0, 3.18, 8.0, 13.0])
    def test_round_trips_across_the_valid_envelope(self, tau_deg, cv):
        target = lift.zero_deadrise_lift_coefficient(tau_deg, 2.5, cv)
        assert lift.solve_lambda_from_cl0(target, tau_deg, cv) == pytest.approx(2.5)

    @pytest.mark.parametrize(
        "tau_deg, lambda_from_fig10", [(2.0, 3.85), (3.0, 2.60), (4.0, 1.86)]
    )
    def test_against_table1_row4(self, tau_deg, lambda_from_fig10):
        # Loose tolerance: these are Fig. 10 reads at Cv = 3.18, which sits
        # between the chart's drawn Cv = 3.0 and 4.0 curves.
        assert lift.solve_lambda_from_cl0(
            CL0_EXAMPLE, tau_deg, CV_EXAMPLE
        ) == pytest.approx(lambda_from_fig10, rel=0.04)

    @pytest.mark.parametrize(
        "tau_deg, lambda_from_fig10", [(2.0, 3.85), (3.0, 2.60), (4.0, 1.86)]
    )
    def test_paper_reads_lie_between_the_drawn_cv_curves(
        self, tau_deg, lambda_from_fig10
    ):
        # Independent of how well the original author interpolated by eye:
        # whatever he read at Cv = 3.18 must fall between the Cv = 3.0 and
        # Cv = 4.0 curves that Fig. 10 actually draws.
        at_cv_3 = lift.solve_lambda_from_cl0(CL0_EXAMPLE, tau_deg, 3.0)
        at_cv_4 = lift.solve_lambda_from_cl0(CL0_EXAMPLE, tau_deg, 4.0)
        assert at_cv_3 <= lambda_from_fig10 <= at_cv_4

    def test_against_table2_nomogram_read(self):
        # Table 2 reads lambda = 3.45 off the Fig. 19 nomogram at tau = 2.23.
        assert lift.solve_lambda_from_cl0(
            CL0_EXAMPLE, 2.23, CV_EXAMPLE
        ) == pytest.approx(3.45, rel=0.03)

    def test_lambda_falls_as_trim_rises_at_fixed_load(self):
        # Carrying a fixed load: more trim means less wetted length needed.
        values = [
            lift.solve_lambda_from_cl0(CL0_EXAMPLE, tau, CV_EXAMPLE)
            for tau in (2.0, 3.0, 4.0, 6.0)
        ]
        assert values == sorted(values, reverse=True)

    def test_searches_past_the_validity_limit(self):
        # lam_max deliberately exceeds the published lambda <= 4 so the
        # caller gets a flaggable number instead of a hard failure. A hull
        # this heavily loaded (CL0 = .085) at low trim and Cv = 5 has too
        # weak a buoyant term to carry the load within lambda <= 4, so the
        # honest answer is a number above the limit, not an exception.
        lam = lift.solve_lambda_from_cl0(0.085, 2.0, 5.0)
        assert lam > lift.LAMBDA_MAX

    def test_raises_on_non_positive_cl0(self):
        with pytest.raises(ValueError, match="must be positive"):
            lift.solve_lambda_from_cl0(0.0, 4.0, 3.18)

    def test_raises_when_target_unreachable(self):
        with pytest.raises(ValueError, match="exceeds the maximum"):
            lift.solve_lambda_from_cl0(10.0, 2.0, 3.18)
