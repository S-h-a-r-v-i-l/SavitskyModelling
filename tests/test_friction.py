"""Batch 4: friction lines and average bottom velocity.

Provenance matters here. V1 (eq. 23/24 + Fig. 14) is Savitsky's; the
Schoenherr and ITTC-57 friction lines are external standards the paper
cites but never restates, so they are validated differently:

* **Schoenherr** is checked against its own defining implicit equation
  (the residual must vanish), and then against Table 1's Cf row, which is
  the real evidence that we picked the right friction line and the right
  Reynolds number definition.
* **V1/V** is checked against Fig. 14 at lambda = 1.0, where the curves
  are well separated and genuinely readable. The Table 1 Vm row sits at
  the top of the chart (V1/V ~ 0.99) where the curves bunch together and
  reading precision is poor, so it gets a looser tolerance.

All imperial-to-SI conversion is confined to this file, and the paper's
own water properties are used (fresh water, nu = 1.0e-5 ft^2/s) rather
than the library's FRESH_WATER preset -- see notes/paper_reference.md.
"""

import math

import pytest

from savitsky import friction

FT = 0.3048
NU_PAPER = 1.0e-5 * FT * FT  # derived from Table 1's own Re values
V_EXAMPLE = 67.5 * FT
BEAM_EXAMPLE = 14.0 * FT
BETA_EXAMPLE_DEG = 10.0
ROUGHNESS_ATTC = 0.0004  # "ATTC Standard Roughness", quoted in Tables 1-2

# Table 1 rows 4-9, per trim column: (tau, lambda, Vm fps, Re, Cf, Cf+dCf)
TABLE1 = [
    (2.0, 3.85, 67.0, 3.61e8, 0.00174, 0.00214),
    (3.0, 2.60, 66.6, 2.42e8, 0.00184, 0.00224),
    (4.0, 1.86, 66.2, 1.73e8, 0.00192, 0.00232),
]


class TestSchoenherr:
    @pytest.mark.parametrize("reynolds", [1e5, 1e6, 1e7, 1e8, 3.61e8, 1e9])
    def test_satisfies_its_defining_equation(self, reynolds):
        # 0.242/sqrt(Cf) = log10(Re*Cf), the implicit definition itself.
        cf = friction.schoenherr_friction_coefficient(reynolds)
        assert 0.242 / math.sqrt(cf) == pytest.approx(math.log10(reynolds * cf))

    @pytest.mark.parametrize("tau_deg, lam, vm, reynolds, cf, cf_total", TABLE1)
    def test_against_table1_cf(self, tau_deg, lam, vm, reynolds, cf, cf_total):
        # Fed the paper's own Re, Schoenherr must return the paper's own Cf.
        assert friction.schoenherr_friction_coefficient(reynolds) == pytest.approx(
            cf, rel=0.005
        )

    def test_against_table2_cf(self):
        assert friction.schoenherr_friction_coefficient(3.22e8) == pytest.approx(
            0.00177, rel=0.005
        )

    def test_decreases_with_reynolds_number(self):
        values = [
            friction.schoenherr_friction_coefficient(re)
            for re in (1e6, 1e7, 1e8, 1e9)
        ]
        assert values == sorted(values, reverse=True)

    def test_raises_on_non_positive_reynolds(self):
        with pytest.raises(ValueError, match="must be positive"):
            friction.schoenherr_friction_coefficient(0.0)


class TestIttc57:
    @pytest.mark.parametrize("reynolds", [1e6, 1e8, 1e9])
    def test_matches_the_published_formula(self, reynolds):
        expected = 0.075 / (math.log10(reynolds) - 2.0) ** 2
        assert friction.ittc57_friction_coefficient(reynolds) == pytest.approx(expected)

    def test_decreases_with_reynolds_number(self):
        values = [friction.ittc57_friction_coefficient(re) for re in (1e6, 1e8, 1e9)]
        assert values == sorted(values, reverse=True)

    def test_is_close_to_schoenherr_at_full_scale(self):
        # The two lines are within a couple of percent at ship-scale Re;
        # they diverge more at model scale. This guards against a gross
        # error in either, without pretending they are interchangeable.
        reynolds = 3.61e8
        schoenherr = friction.schoenherr_friction_coefficient(reynolds)
        ittc = friction.ittc57_friction_coefficient(reynolds)
        assert ittc == pytest.approx(schoenherr, rel=0.03)

    def test_raises_on_non_positive_reynolds(self):
        with pytest.raises(ValueError, match="must be positive"):
            friction.ittc57_friction_coefficient(-1.0)


class TestFrictionCoefficient:
    def test_defaults_to_schoenherr(self):
        assert friction.friction_coefficient(1e8) == (
            friction.schoenherr_friction_coefficient(1e8)
        )

    def test_selects_ittc57(self):
        assert friction.friction_coefficient(
            1e8, line=friction.FrictionLine.ITTC57
        ) == friction.ittc57_friction_coefficient(1e8)

    def test_roughness_allowance_adds_linearly(self):
        smooth = friction.friction_coefficient(1e8)
        rough = friction.friction_coefficient(1e8, roughness_allowance=0.0004)
        assert rough - smooth == pytest.approx(0.0004)

    def test_defaults_to_smooth(self):
        assert friction.friction_coefficient(1e8) == pytest.approx(
            friction.friction_coefficient(1e8, roughness_allowance=0.0)
        )

    @pytest.mark.parametrize("tau_deg, lam, vm, reynolds, cf, cf_total", TABLE1)
    def test_against_table1_row9(self, tau_deg, lam, vm, reynolds, cf, cf_total):
        # Row 9 = row 7 + row 8, i.e. Schoenherr plus the ATTC allowance.
        assert friction.friction_coefficient(
            reynolds, roughness_allowance=ROUGHNESS_ATTC
        ) == pytest.approx(cf_total, rel=0.005)


class TestAverageBottomVelocity:
    def test_zero_deadrise_matches_eq24_exactly(self):
        tau_deg, lam = 6.0, 2.0
        expected = math.sqrt(
            1.0
            - 0.0120
            * tau_deg**1.1
            / (math.sqrt(lam) * math.cos(math.radians(tau_deg)))
        )
        assert friction.average_bottom_velocity_ratio(tau_deg, lam, 0.0) == (
            pytest.approx(expected)
        )

    def test_bottom_velocity_is_below_forward_speed(self):
        # Bottom pressure exceeds free-stream pressure, so the flow over
        # the bottom is slower than the boat.
        assert friction.average_bottom_velocity_ratio(4.0, 2.5, 10.0) < 1.0

    def test_rises_toward_free_stream_with_more_wetted_length(self):
        values = [
            friction.average_bottom_velocity_ratio(6.0, lam, 10.0)
            for lam in (0.8, 1.5, 2.5, 4.0)
        ]
        assert values == sorted(values)

    def test_falls_with_increasing_trim(self):
        values = [
            friction.average_bottom_velocity_ratio(tau, 2.0, 10.0)
            for tau in (2.0, 6.0, 10.0, 15.0)
        ]
        assert values == sorted(values, reverse=True)

    def test_rises_with_increasing_deadrise(self):
        # Fig. 14's higher-deadrise panels sit higher: deadrise cuts lift,
        # hence bottom pressure, hence V1 moves back toward V.
        values = [
            friction.average_bottom_velocity_ratio(15.0, 1.0, beta)
            for beta in (0.0, 10.0, 20.0, 30.0)
        ]
        assert values == sorted(values)

    @pytest.mark.parametrize(
        "tau_deg, beta_deg, ratio_from_fig14",
        [
            (14.0, 0.0, 0.880),
            (15.0, 10.0, 0.890),
            (15.0, 20.0, 0.900),
            (15.0, 30.0, 0.915),
        ],
    )
    def test_against_fig14_where_it_is_readable(
        self, tau_deg, beta_deg, ratio_from_fig14
    ):
        # At lambda = 1.0 the curves are well separated; this is the only
        # part of Fig. 14 worth reading numbers off. Tolerance is chart
        # reading precision.
        assert friction.average_bottom_velocity_ratio(
            tau_deg, 1.0, beta_deg
        ) == pytest.approx(ratio_from_fig14, abs=0.006)

    @pytest.mark.parametrize("tau_deg, lam, vm, reynolds, cf, cf_total", TABLE1)
    def test_against_table1_vm(self, tau_deg, lam, vm, reynolds, cf, cf_total):
        # Looser: Table 1's Vm sits where Fig. 14's curves bunch near 0.99,
        # and the beta=0 vs beta=10 spread there (0.0014 in V1/V) is itself
        # smaller than the chart can be read to. We are consistently about
        # +0.3% high, which is inside that reading noise.
        computed = friction.average_bottom_velocity(
            V_EXAMPLE, tau_deg, lam, BETA_EXAMPLE_DEG
        )
        assert computed / FT == pytest.approx(vm, rel=0.005)

    def test_raises_when_radicand_goes_negative(self):
        with pytest.raises(ValueError, match="radicand is negative"):
            friction.average_bottom_velocity_ratio(15.0, 0.05, 0.0)


class TestReynoldsNumber:
    def test_matches_the_definition(self):
        assert friction.reynolds_number(10.0, 2.0, 0.5, 1e-6) == pytest.approx(1e7)

    def test_uses_mean_wetted_length_not_beam(self):
        # Doubling lambda must double Re; if the beam alone were the length
        # scale this would not change.
        single = friction.reynolds_number(10.0, 2.0, 0.5, 1e-6)
        assert friction.reynolds_number(10.0, 4.0, 0.5, 1e-6) == pytest.approx(
            2.0 * single
        )

    @pytest.mark.parametrize("tau_deg, lam, vm, reynolds, cf, cf_total", TABLE1)
    def test_against_table1_re(self, tau_deg, lam, vm, reynolds, cf, cf_total):
        # Built from the paper's own Vm so this isolates the Re definition.
        computed = friction.reynolds_number(vm * FT, lam, BEAM_EXAMPLE, NU_PAPER)
        assert computed == pytest.approx(reynolds, rel=0.005)
