"""Dimension 3 — Buff/debuff uptime.

Uptime on the buffs/debuffs YOU are responsible for maintaining, vs the Top-Parse
uptime. The classic "your DoT fell off" analysis.
"""

from __future__ import annotations

from wowanalyze.diff.base import ActorFightData, DiffDimension
from wowanalyze.models import Dimension, Finding, ReferenceProfile, Severity


class UptimeDimension(DiffDimension):
    dimension = Dimension.uptime

    def evaluate(
        self, data: ActorFightData, profile: ReferenceProfile
    ) -> list[Finding]:
        findings: list[Finding] = []
        if data.duration_ms <= 0:
            return findings

        combined = {**data.buff_uptime_ms, **data.debuff_uptime_ms}

        for metric in profile.metrics:
            if metric.dimension is not Dimension.uptime:
                continue
            if not metric.key.startswith("uptime:"):
                continue

            aura = metric.key.split(":", 1)[1]
            yours = combined.get(aura, 0) / data.duration_ms  # fraction 0..1
            expected = metric.median

            if yours < expected - 0.05:
                gap = expected - yours
                findings.append(
                    Finding(
                        dimension=self.dimension,
                        severity=Severity.major if gap > 0.15 else Severity.minor,
                        title=f"{aura} uptime {yours:.0%} (want {expected:.0%})",
                        detail=(
                            f"You held {aura} for {yours:.0%} of the pull; top "
                            f"{profile.build.label} parses kept it at {expected:.0%}. "
                            f"Refresh it before it drops."
                        ),
                        your_value=round(yours, 3),
                        reference_value=round(expected, 3),
                        unit="fraction",
                        impact_score=gap * 5,
                    )
                )
        return findings
