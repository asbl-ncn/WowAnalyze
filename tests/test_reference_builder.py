"""Test reference aggregation — medians, the presence filter, and profile wrapping.

Pure functions, no network.
"""

from __future__ import annotations

from wowanalyze.diff.base import ActorFightData
from wowanalyze.models import BuildCluster, Difficulty
from wowanalyze.reference.builder import aggregate_cluster, build_profile


# 60s pulls, so casts-per-minute equals raw counts and the medians stay readable.
def _fd(**casts: int) -> ActorFightData:
    return ActorFightData(duration_ms=60_000, cast_counts=dict(casts))


def test_aggregate_medians():
    cluster = [
        _fd(**{"Lava Burst": 30, "Stormkeeper": 2}),
        _fd(**{"Lava Burst": 34, "Stormkeeper": 2}),
        _fd(**{"Lava Burst": 32, "Stormkeeper": 3}),
    ]
    by_key = {m.key: m for m in aggregate_cluster(cluster)}
    # Stored as per-minute; at 60s pulls that equals the raw counts.
    assert by_key["cast_count:Lava Burst"].median == 32
    assert by_key["cast_count:Lava Burst"].unit == "per-min"
    assert by_key["cast_count:Stormkeeper"].median == 2


def test_rare_ability_is_dropped():
    # A cast present in only 1 of 4 parses must not become an "expected" metric.
    cluster = [
        _fd(**{"Lava Burst": 30}),
        _fd(**{"Lava Burst": 31}),
        _fd(**{"Lava Burst": 29}),
        _fd(**{"Lava Burst": 30, "Silvermoon Health Potion": 1}),
    ]
    keys = {m.key for m in aggregate_cluster(cluster)}
    assert "cast_count:Lava Burst" in keys
    assert "cast_count:Silvermoon Health Potion" not in keys


def test_build_profile_wraps_metrics():
    profile = build_profile(
        spec="shaman-elemental",
        boss_id=3177,
        boss_name="Vorasius",
        difficulty=Difficulty.mythic,
        build=BuildCluster(key="all", hero_talent="mixed", label="all"),
        patch="x",
        generated_at="2026-01-01T00:00:00+00:00",
        cluster_data=[_fd(**{"Lava Burst": 5})],
    )
    assert profile.sample_size == 1
    assert profile.boss_name == "Vorasius"
    assert any(m.key == "cast_count:Lava Burst" for m in profile.metrics)
