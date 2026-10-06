"""Batch 7: end-to-end single-point solve.

The headline test is a full reproduction of the paper's Table 2 worked
example (the simple case, all forces through the CG) from its raw inputs:
weight, beam, LCG, deadrise and speed in, trim and drag out, with nothing
read off a chart.

Density note: the tables are internally inconsistent (see
notes/caveats.md A2) -- the drag rows were computed with
rho = 2.00 slug/ft^3 but the CLbeta line implies 1.94. The headline test
uses 2.00, which is what the drag and power rows were actually computed
with; a separate test documents what the other choice costs, since no
single density reproduces every printed number.
"""

import pytest

from savitsky.constants import FRESH_WATER, WaterProperties
from savitsky.core import solve_single_point
from savitsky.friction import FrictionLine
from savitsky.result import ResultFlag

FT = 0.3048
LBF = 4.448222
SLUG_PER_FT3 = 515.379
HP = 745.7
GRAVITY = 9.80665

PAPER_EXAMPLE = dict(
    load=60000.0 * LBF,
    beam=14.0 * FT,
    lcg=29.0 * FT,
    deadrise_deg=10.0,
    speed=67.5 * FT,
    roughness_allowance=0.0004,  # "ATTC Standard Roughness"
)
# Water the paper actually used: nu backed out of its own Reynolds numbers,
# rho from its drag rows. Neither is stated in the paper.
PAPER_WATER = WaterProperties(rho=2.00 * SLUG_PER_FT3, nu=1.0e-5 * FT * FT)


@pytest.fixture(scope="module")
def paper_result():
    return solve_single_point(water=PAPER_WATER, **PAPER_EXAMPLE)


class TestPaperTable2:
    """Full reproduction of the simple-case worked example, p. 90."""

    def test_converges_cleanly(self, paper_result):
        assert paper_result.converged
        assert paper_result.flags == ResultFlag.NONE

    def test_speed_coefficient(self, paper_result):
        assert paper_result.cv == pytest.approx(3.18, rel=0.005)

    def test_equilibrium_trim(self, paper_result):
        # Paper: 2.23 deg, itself read off the Fig. 19 nomogram.
        assert paper_result.tau_deg == pytest.approx(2.23, rel=0.02)

    def test_wetted_length_ratio(self, paper_result):
        # Paper: 3.45, also a nomogram read.
        assert paper_result.lam == pytest.approx(3.45, rel=0.02)

    def test_friction_drag(self, paper_result):
        assert paper_result.Df / LBF == pytest.approx(6670, rel=0.01)

    def test_total_drag(self, paper_result):
        assert paper_result.D / LBF == pytest.approx(9010, rel=0.01)

    def test_effective_power(self, paper_result):
        # Paper quotes EHP = 1100; our effective_power is in watts.
        assert paper_result.effective_power / HP == pytest.approx(1100, rel=0.01)

    def test_centre_of_pressure_sits_over_the_cg(self, paper_result):
        # The defining condition of the simple case, eq. (37).
        assert paper_result.lp == pytest.approx(PAPER_EXAMPLE["lcg"])

    def test_wetted_lengths_straddle_the_mean(self, paper_result):
        mean_length = paper_result.lam * PAPER_EXAMPLE["beam"]
        assert paper_result.Lc < mean_length < paper_result.Lk


class TestDensityInconsistency:
    """Documents caveats.md A2 rather than hiding it."""

    def test_fresh_water_reproduces_the_lift_coefficient_but_not_the_drag(self):
        # rho = 1.94 is what the tables' CLbeta line implies. It nails
        # CLbeta = 0.069 and then misses the printed drag by about 2%.
        fresh = WaterProperties(rho=1.94 * SLUG_PER_FT3, nu=1.0e-5 * FT * FT)
        result = solve_single_point(water=fresh, **PAPER_EXAMPLE)
        assert result.cl_beta == pytest.approx(0.069, rel=0.01)
        assert result.D / LBF == pytest.approx(9010, rel=0.03)
        assert result.D / LBF < 9010  # consistently low, as expected

    def test_seawater_reproduces_the_drag_but_not_the_lift_coefficient(
        self, paper_result
    ):
        # rho = 2.00 is what the drag rows imply: drag lands within 0.5%,
        # while CLbeta comes out 0.067 against the printed 0.069.
        assert paper_result.D / LBF == pytest.approx(9010, rel=0.005)
        assert paper_result.cl_beta == pytest.approx(0.067, rel=0.01)


class TestFlags:
    """The never-raise contract: awkward cases return flags, not exceptions."""

    def test_dry_chines_are_flagged(self):
        # Light, fast and sharply veed: the chines never get wet.
        result = solve_single_point(
            load=200.0, beam=0.5, lcg=0.6, deadrise_deg=30.0, speed=12.0
        )
        assert ResultFlag.DRY_CHINES in result.flags
        assert result.Lc < 0.0

    def test_unbalanceable_hull_is_flagged(self):
        # CG far forward of anywhere the pressure force can reach.
        result = solve_single_point(
            load=700.0, beam=0.5, lcg=8.0, deadrise_deg=15.0, speed=9.0
        )
        assert not result.converged
        assert ResultFlag.NO_SOLUTION in result.flags

    def test_too_slow_to_plane_is_flagged(self):
        result = solve_single_point(
            load=700.0, beam=0.5, lcg=1.0, deadrise_deg=15.0, speed=1.2
        )
        assert not result.converged
        assert ResultFlag.NO_SOLUTION in result.flags

    def test_extreme_trim_reports_what_it_found_before_failing(self):
        # CG almost at the transom drives trim past the envelope, where
        # eq. (24) goes imaginary. The trim found is still reported.
        result = solve_single_point(
            load=700.0, beam=0.5, lcg=0.02, deadrise_deg=15.0, speed=9.0
        )
        assert not result.converged
        assert ResultFlag.NO_SOLUTION in result.flags
        assert ResultFlag.OUT_OF_VALID_RANGE in result.flags
        assert result.tau_deg is not None  # partial answer preserved
        assert result.D is None

    def test_never_raises_across_a_wide_parameter_sweep(self):
        # The contract that lets callers sweep thousands of variants
        # without try/except.
        for speed in (0.5, 2.0, 5.0, 9.0, 15.0, 30.0):
            for deadrise in (0.0, 10.0, 25.0, 40.0):
                for lcg in (0.05, 0.5, 1.0, 3.0):
                    result = solve_single_point(
                        load=700.0,
                        beam=0.5,
                        lcg=lcg,
                        deadrise_deg=deadrise,
                        speed=speed,
                    )
                    assert isinstance(result.flags, ResultFlag)
                    if result.converged:
                        assert result.D > 0.0


class TestPhysicalBehaviour:
    """Trend checks on a PEP27-scale hull (0.5 m beam, ~75 kg all-up)."""

    BOAT = dict(load=75.0 * GRAVITY, beam=0.5, lcg=0.9, deadrise_deg=18.0)

    def test_solves_cleanly_at_target_speed(self):
        result = solve_single_point(speed=8.0, water=FRESH_WATER, **self.BOAT)
        assert result.converged
        assert result.flags == ResultFlag.NONE
        assert 2.0 < result.tau_deg < 15.0

    def test_trim_falls_as_speed_rises(self):
        trims = [
            solve_single_point(speed=v, water=FRESH_WATER, **self.BOAT).tau_deg
            for v in (7.0, 8.0, 9.0, 10.0, 11.0)
        ]
        assert trims == sorted(trims, reverse=True)

    def test_wetted_length_falls_as_speed_rises(self):
        lambdas = [
            solve_single_point(speed=v, water=FRESH_WATER, **self.BOAT).lam
            for v in (7.0, 8.0, 9.0, 10.0, 11.0)
        ]
        assert lambdas == sorted(lambdas, reverse=True)

    def test_more_deadrise_means_more_drag(self):
        drags = []
        for deadrise in (5.0, 12.0, 20.0, 28.0):
            result = solve_single_point(
                load=75.0 * GRAVITY,
                beam=0.5,
                lcg=0.9,
                deadrise_deg=deadrise,
                speed=8.0,
                water=FRESH_WATER,
            )
            assert result.converged
            drags.append(result.D)
        assert drags == sorted(drags)

    def test_roughness_increases_drag(self):
        smooth = solve_single_point(speed=8.0, water=FRESH_WATER, **self.BOAT)
        rough = solve_single_point(
            speed=8.0, water=FRESH_WATER, roughness_allowance=0.0004, **self.BOAT
        )
        assert rough.D > smooth.D

    def test_friction_line_choice_shifts_drag_slightly(self):
        schoenherr = solve_single_point(
            speed=8.0, water=FRESH_WATER, friction_line=FrictionLine.SCHOENHERR,
            **self.BOAT
        )
        ittc = solve_single_point(
            speed=8.0, water=FRESH_WATER, friction_line=FrictionLine.ITTC57,
            **self.BOAT
        )
        # Different lines, same ballpark: a few percent apart at this scale.
        assert ittc.D == pytest.approx(schoenherr.D, rel=0.05)
        assert ittc.D != schoenherr.D

    def test_effective_power_is_drag_times_speed(self):
        result = solve_single_point(speed=8.0, water=FRESH_WATER, **self.BOAT)
        assert result.effective_power == pytest.approx(result.D * 8.0)
