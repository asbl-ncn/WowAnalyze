"""The diff engine: compare a Target's fight data against its Reference Profile.

Each Dimension is a self-contained comparator. `ALL_DIMENSIONS` is ordered by MVP
priority so Findings come out cooldowns-first.
"""

from wowanalyze.diff.base import ActorFightData, DiffDimension
from wowanalyze.diff.cooldowns import CooldownDimension
from wowanalyze.diff.rotation import RotationDimension
from wowanalyze.diff.survival import SurvivalDimension
from wowanalyze.diff.uptime import UptimeDimension

# Priority order: cooldowns -> rotation -> uptime -> survival.
ALL_DIMENSIONS: list[DiffDimension] = [
    CooldownDimension(),
    RotationDimension(),
    UptimeDimension(),
    SurvivalDimension(),
]

__all__ = ["ActorFightData", "DiffDimension", "ALL_DIMENSIONS"]
