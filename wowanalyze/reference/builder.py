"""Build Reference Profiles from Top Parses.

The expensive, offline half of the system. Run by `scripts/precompute.py` on GitHub
Actions. Steps:

    1. rankings  -> the Top ~100 Mythic kills for (spec, boss) by rDPS
    2. cluster   -> group those parses into Build Clusters (hero tree + key talents)
    3. aggregate -> per cluster, distill ActorFightData into ReferenceMetrics (median + spread)

Everything here is a stub with the shape locked in. The statistics are simple on
purpose — medians and quartiles — because the value is the *data*, not fancy math.
"""

from __future__ import annotations

import statistics

from wowanalyze.diff.base import ActorFightData
from wowanalyze.models import (
    BuildCluster,
    Difficulty,
    Dimension,
    ReferenceMetric,
    ReferenceProfile,
)


def cluster_parses(
    parses: list[tuple[BuildCluster, ActorFightData]],
) -> dict[str, list[ActorFightData]]:
    """Group parses by Build Cluster key.

    TODO(reference): derive the BuildCluster from each parse's talent data (hero tree +
    the handful of talents that change the rotation). For now the caller supplies it.
    """
    clusters: dict[str, list[ActorFightData]] = {}
    for build, data in parses:
        clusters.setdefault(build.key, []).append(data)
    return clusters


def _median(values: list[float]) -> tuple[float, float | None, float | None]:
    if not values:
        return 0.0, None, None
    values = sorted(values)
    med = statistics.median(values)
    if len(values) >= 4:
        q = statistics.quantiles(values, n=4)
        return med, q[0], q[2]
    return med, None, None


def aggregate_cluster(
    cluster_data: list[ActorFightData],
) -> list[ReferenceMetric]:
    """Turn a cluster of parses into ReferenceMetrics (median cast counts, uptimes...)."""
    metrics: list[ReferenceMetric] = []

    # Cast counts -> cooldowns/rotation metrics.
    n = len(cluster_data)
    abilities = {a for d in cluster_data for a in d.cast_counts}
    for ability in sorted(abilities):
        # Only trust an ability as "expected" if most top parses actually used it —
        # drops one-off utility/consumable casts from becoming a false standard.
        present = sum(1 for d in cluster_data if d.cast_counts.get(ability, 0) > 0)
        if n and present * 2 < n:
            continue
        # Store casts-per-minute, not raw totals, so pulls of different lengths compare
        # fairly (a longer kill naturally has more casts).
        rates = [
            (d.cast_counts.get(ability, 0) / (d.duration_ms / 60000))
            if d.duration_ms
            else 0.0
            for d in cluster_data
        ]
        med, p25, p75 = _median(rates)
        metrics.append(
            ReferenceMetric(
                key=f"cast_count:{ability}",
                dimension=Dimension.cooldowns,  # TODO: tag major CDs vs rotational fillers
                label=f"{ability}",
                median=med,
                p25=p25,
                p75=p75,
                unit="per-min",
            )
        )

    # Activity fraction -> rotation.
    activity = [
        d.active_time_ms / d.duration_ms
        for d in cluster_data
        if d.active_time_ms is not None and d.duration_ms > 0
    ]
    if activity:
        med, p25, p75 = _median(activity)
        metrics.append(
            ReferenceMetric(
                key="activity",
                dimension=Dimension.rotation,
                label="Activity (GCD uptime)",
                median=med,
                p25=p25,
                p75=p75,
                unit="fraction",
            )
        )

    # TODO(reference): uptime:<aura> (Dimension.uptime) and survival metrics.
    return metrics


def build_profile(
    *,
    spec: str,
    boss_id: int,
    boss_name: str,
    difficulty: Difficulty,
    build: BuildCluster,
    patch: str,
    generated_at: str,
    cluster_data: list[ActorFightData],
) -> ReferenceProfile:
    return ReferenceProfile(
        spec=spec,
        boss_id=boss_id,
        boss_name=boss_name,
        difficulty=difficulty,
        build=build.model_copy(update={"sample_size": len(cluster_data)}),
        patch=patch,
        generated_at=generated_at,
        sample_size=len(cluster_data),
        metrics=aggregate_cluster(cluster_data),
    )
