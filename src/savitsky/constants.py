"""Physical constants and water property presets.

Not sourced from the Savitsky paper (the paper takes rho and nu as given
inputs) -- these are standard textbook values provided as convenience
presets. Callers may always supply their own WaterProperties.
"""

from dataclasses import dataclass

# Standard gravity, m/s^2.
G = 9.80665


@dataclass(frozen=True)
class WaterProperties:
    """Water properties needed by the planing equations.

    Attributes:
        rho: Mass density, kg/m^3.
        nu: Kinematic viscosity, m^2/s.
    """

    rho: float
    nu: float


# Fresh water at ~20 C.
FRESH_WATER = WaterProperties(rho=998.2, nu=1.004e-6)

# Standard ITTC seawater at ~15 C.
SALT_WATER = WaterProperties(rho=1025.9, nu=1.19e-6)
