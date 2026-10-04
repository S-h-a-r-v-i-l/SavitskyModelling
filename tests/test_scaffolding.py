"""Batch 1 smoke test: the package installs and imports cleanly."""

from savitsky.constants import FRESH_WATER, SALT_WATER, G, WaterProperties
from savitsky.result import PlaningResult, ResultFlag


def test_water_properties_presets():
    assert isinstance(FRESH_WATER, WaterProperties)
    assert isinstance(SALT_WATER, WaterProperties)
    assert FRESH_WATER.rho > 0
    assert FRESH_WATER.nu > 0
    assert SALT_WATER.rho > FRESH_WATER.rho
    assert G > 9.7


def test_default_result_is_unconverged_with_no_flags():
    result = PlaningResult()
    assert result.converged is False
    assert result.flags == ResultFlag.NONE
    assert result.tau_deg is None
