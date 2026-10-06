"""Batch 5: planing drag, eq. (17)-(19) and (25)-(27) of Savitsky (1964).

A density inconsistency in the paper governs how these tests are written.
Inverting eq. (19) on all four printed Df values (Table 1's three trim
columns plus Table 2) backs out rho = 1.994 / 2.007 / 1.998 / 2.000
slug/ft^3 -- i.e. the drag rows were computed with rho = 2.00 slug/ft^3, a
rounded seawater value. But the CLbeta line printed at the head of those
same tables reads `60,000 / 0.97 x 67.5^2 x 14^2`, and that 0.97 is
rho/2 for *fresh* water, rho = 1.94. The paper mixes the two, a 3%
discrepancy. Using 1.94 in eq. (19) misses the printed Df by about -3%
consistently.

These tests therefore use rho = 2.00 slug/ft^3 for the drag comparisons,
which is what the drag rows were actually computed with. That is a
statement about reproducing the paper, not about our code: density is a
caller input in this library, so nothing here hardcodes either value.
See notes/paper_reference.md.
"""

import math

import pytest

from savitsky import drag

FT = 0.3048
LBF = 4.448222
SLUG_PER_FT3 = 515.379

# Density the paper's own Df rows imply (rounded seawater), NOT the 1.94
# its CLbeta line implies. See module docstring.
RHO_PAPER_DRAG = 2.00 * SLUG_PER_FT3

LOAD_EXAMPLE = 60000.0 * LBF
BEAM_EXAMPLE = 14.0 * FT
BETA_EXAMPLE_DEG = 10.0

# Table 1: (tau, Cf+dCf, V1 fps, lambda, Df lb, Dp lb, D lb)
TABLE1 = [
    (2.0, 0.00214, 67.0, 3.85, 7340, 2094, 9434),
    (3.0, 0.00224, 66.6, 2.60, 5160, 3144, 8304),
    (4.0, 0.00232, 66.2, 1.86, 3760, 4188, 7948),
]


class TestPressureDrag:
    """Eq. (17)."""

    def test_matches_published_form(self):
        assert drag.pressure_drag(1000.0, 5.0) == pytest.approx(
            1000.0 * math.tan(math.radians(5.0))
        )

    @pytest.mark.parametrize("tau_deg, cf, v1, lam, df, dp, d", TABLE1)
    def test_against_table1_row14(self, tau_deg, cf, v1, lam, df, dp, d):
        assert drag.pressure_drag(LOAD_EXAMPLE, tau_deg) / LBF == pytest.approx(
            dp, rel=0.005
        )

    def test_vanishes_at_zero_trim(self):
        # With the bottom horizontal the pressure force is purely vertical.
        assert drag.pressure_drag(1000.0, 0.0) == pytest.approx(0.0)

    def test_grows_with_trim(self):
        values = [drag.pressure_drag(1000.0, tau) for tau in (2.0, 5.0, 10.0, 15.0)]
        assert values == sorted(values)


class TestFrictionDrag:
    """Eq. (19)."""

    def test_matches_published_form(self):
        cf, rho, v1, lam, beam, beta = 0.003, 1000.0, 20.0, 2.5, 0.5, 15.0
        expected = cf * rho * v1**2 * (lam * beam**2) / (2.0 * math.cos(math.radians(beta)))
        assert drag.friction_drag(cf, rho, v1, lam, beam, beta) == pytest.approx(
            expected
        )

    @pytest.mark.parametrize("tau_deg, cf, v1, lam, df, dp, d", TABLE1)
    def test_against_table1_row10(self, tau_deg, cf, v1, lam, df, dp, d):
        computed = drag.friction_drag(
            cf, RHO_PAPER_DRAG, v1 * FT, lam, BEAM_EXAMPLE, BETA_EXAMPLE_DEG
        )
        assert computed / LBF == pytest.approx(df, rel=0.005)

    def test_against_table2_row15(self):
        computed = drag.friction_drag(
            0.00217, RHO_PAPER_DRAG, 66.9 * FT, 3.45, BEAM_EXAMPLE, BETA_EXAMPLE_DEG
        )
        assert computed / LBF == pytest.approx(6670, rel=0.005)

    def test_fresh_water_density_misses_the_paper_by_three_percent(self):
        # Documents the inconsistency rather than hiding it: the density
        # implied by the tables' own CLbeta line underestimates their own
        # printed Df by about 3%.
        fresh = 1.94 * SLUG_PER_FT3
        computed = drag.friction_drag(
            0.00214, fresh, 67.0 * FT, 3.85, BEAM_EXAMPLE, BETA_EXAMPLE_DEG
        )
        assert computed / LBF == pytest.approx(7340 * 0.97, rel=0.01)

    def test_scales_with_velocity_squared(self):
        single = drag.friction_drag(0.003, 1000.0, 10.0, 2.5, 0.5, 15.0)
        assert drag.friction_drag(0.003, 1000.0, 20.0, 2.5, 0.5, 15.0) == pytest.approx(
            4.0 * single
        )

    def test_scales_with_wetted_length(self):
        single = drag.friction_drag(0.003, 1000.0, 20.0, 1.0, 0.5, 15.0)
        assert drag.friction_drag(0.003, 1000.0, 20.0, 3.0, 0.5, 15.0) == pytest.approx(
            3.0 * single
        )

    def test_deadrise_increases_wetted_area(self):
        # A V-bottom has more surface than its projected area, by 1/cos(beta).
        flat = drag.friction_drag(0.003, 1000.0, 20.0, 2.5, 0.5, 0.0)
        vee = drag.friction_drag(0.003, 1000.0, 20.0, 2.5, 0.5, 20.0)
        assert vee / flat == pytest.approx(1.0 / math.cos(math.radians(20.0)))


class TestTotalDrag:
    """Eq. (18)/(25)."""

    def test_is_pressure_plus_resolved_friction(self):
        load, tau_deg, df = 5000.0, 4.0, 800.0
        expected = drag.pressure_drag(load, tau_deg) + df / math.cos(
            math.radians(tau_deg)
        )
        assert drag.total_drag(load, tau_deg, df) == pytest.approx(expected)

    def test_matches_the_combined_eq25_form(self):
        # Writing eq. (25) out in one go must equal composing (17) and (19).
        load, tau_deg = 5000.0, 4.0
        cf, rho, v1, lam, beam, beta = 0.003, 1000.0, 20.0, 2.5, 0.5, 15.0
        tau_rad, beta_rad = math.radians(tau_deg), math.radians(beta)
        eq25 = load * math.tan(tau_rad) + (
            rho * v1**2 * cf * lam * beam**2
        ) / (2.0 * math.cos(beta_rad) * math.cos(tau_rad))
        df = drag.friction_drag(cf, rho, v1, lam, beam, beta)
        assert drag.total_drag(load, tau_deg, df) == pytest.approx(eq25)

    @pytest.mark.parametrize("tau_deg, cf, v1, lam, df, dp, d", TABLE1)
    def test_against_table1_row16(self, tau_deg, cf, v1, lam, df, dp, d):
        friction_force = drag.friction_drag(
            cf, RHO_PAPER_DRAG, v1 * FT, lam, BEAM_EXAMPLE, BETA_EXAMPLE_DEG
        )
        computed = drag.total_drag(LOAD_EXAMPLE, tau_deg, friction_force)
        assert computed / LBF == pytest.approx(d, rel=0.005)

    def test_against_table2_row17(self):
        friction_force = drag.friction_drag(
            0.00217, RHO_PAPER_DRAG, 66.9 * FT, 3.45, BEAM_EXAMPLE, BETA_EXAMPLE_DEG
        )
        computed = drag.total_drag(LOAD_EXAMPLE, 2.23, friction_force)
        assert computed / LBF == pytest.approx(9010, rel=0.005)


class TestDragLiftRatio:
    """Eq. (26)/(27)."""

    def test_is_total_drag_over_load(self):
        load, tau_deg, df = 5000.0, 4.0, 800.0
        assert drag.drag_lift_ratio(load, tau_deg, df) == pytest.approx(
            drag.total_drag(load, tau_deg, df) / load
        )

    def test_matches_eq27_coefficient_form(self):
        # Eq. (27) rewrites eq. (26) using CL = 2*Delta/(rho*V^2*b^2):
        #     D/Delta = tan(tau) + (V1/V)^2 * Cf * lambda / (CL*cos(tau)*cos(beta))
        # The two must agree identically; this pins our eq. (19) area
        # convention, since a wrong area would break the identity.
        rho, speed, beam, load = 1000.0, 20.0, 0.5, 5000.0
        tau_deg, beta_deg, lam, cf = 4.0, 15.0, 2.5, 0.003
        velocity_ratio = 0.97
        v1 = speed * velocity_ratio

        lift_coefficient = 2.0 * load / (rho * speed**2 * beam**2)
        eq27 = math.tan(math.radians(tau_deg)) + (
            velocity_ratio**2 * cf * lam
        ) / (
            lift_coefficient
            * math.cos(math.radians(tau_deg))
            * math.cos(math.radians(beta_deg))
        )

        df = drag.friction_drag(cf, rho, v1, lam, beam, beta_deg)
        assert drag.drag_lift_ratio(load, tau_deg, df) == pytest.approx(eq27)

    def test_table2_ratio_is_in_the_planing_range(self):
        # A planing hull near its best trim sits around 0.12-0.18.
        friction_force = drag.friction_drag(
            0.00217, RHO_PAPER_DRAG, 66.9 * FT, 3.45, BEAM_EXAMPLE, BETA_EXAMPLE_DEG
        )
        ratio = drag.drag_lift_ratio(LOAD_EXAMPLE, 2.23, friction_force)
        assert 0.12 < ratio < 0.18
