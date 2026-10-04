"""Future extension points: interfaces only, not implemented.

Added opportunistically as each relevant batch lands:
  - effective_deadrise(...): effective deadrise for variable-deadrise hulls
    (deadrise evaluated over the wetted region).
  - pre_planing_resistance(...): pre-planing / hump resistance estimate
    below the planing speed range.
  - DrivetrainModel / BatteryModel / PropellerModel: Protocol classes for a
    later combined drivetrain + battery + prop sweep.
"""
