"""The Dimension interface every comparator implements."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from wowanalyze.models import Dimension, Finding, ReferenceProfile


class ActorFightData(BaseModel):
    """Normalized fight data for one Target, ready to diff.

    This is the boundary between "talking to WCL" and "analyzing". The WCL client
    produces one of these per Target; Dimensions only ever read from it, so they are
    trivially unit-testable with hand-built fixtures.
    """

    duration_ms: int
    detected_build_key: str | None = None
    cast_counts: dict[str, int] = Field(default_factory=dict)
    buff_uptime_ms: dict[str, int] = Field(default_factory=dict)
    debuff_uptime_ms: dict[str, int] = Field(default_factory=dict)
    active_time_ms: int | None = None
    resource_overcap: dict[str, float] = Field(default_factory=dict)
    deaths: int = 0
    avoidable_damage_taken: int = 0
    # TODO(cooldowns): add per-cast timestamps once phase-aware timing lands.


class DiffDimension(ABC):
    """Compare one axis of an ActorFightData against a ReferenceProfile."""

    dimension: Dimension

    @abstractmethod
    def evaluate(
        self, data: ActorFightData, profile: ReferenceProfile
    ) -> list[Finding]:
        """Return Findings for this dimension. Empty list = nothing wrong here."""
        raise NotImplementedError
