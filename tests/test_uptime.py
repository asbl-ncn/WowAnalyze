"""Test the uptime dimension (dot maintenance vs top parses)."""

from __future__ import annotations

from wowanalyze.diff.base import ActorFightData
from wowanalyze.diff.uptime import UptimeDimension
from wowanalyze.models import (
    BuildCluster,
    Difficulty,
    Dimension,
    ReferenceMetric,
    ReferenceProfile,
)


def _profile(metric: ReferenceMetric) -> ReferenceProfile:
    return ReferenceProfile(
        spec="shaman-elemental",
        boss_id=1,
        boss_name="Test",
        difficulty=Difficulty.mythic,
        build=BuildCluster(key="all", hero_talent="mixed", label="all"),
        patch="t",
        generated_at="2026-01-01T00:00:00+00:00",
        sample_size=20,
        metrics=[metric],
    )


def _flame_shock(median: float) -> ReferenceMetric:
    return ReferenceMetric(
        key="uptime:Flame Shock",
        dimension=Dimension.uptime,
        label="Flame Shock uptime",
        median=median,
        unit="fraction",
    )


def test_low_uptime_is_flagged():
    profile = _profile(_flame_shock(0.95))
    # 70% uptime vs 95% expected.
    data = ActorFightData(duration_ms=200_000, debuff_uptime_ms={"Flame Shock": 140_000})

    findings = UptimeDimension().evaluate(data, profile)

    assert len(findings) == 1
    assert findings[0].dimension is Dimension.uptime


def test_good_uptime_is_clean():
    profile = _profile(_flame_shock(0.95))
    data = ActorFightData(duration_ms=200_000, debuff_uptime_ms={"Flame Shock": 192_000})

    assert UptimeDimension().evaluate(data, profile) == []
