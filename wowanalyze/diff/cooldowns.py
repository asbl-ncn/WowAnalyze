"""Dimension 1 — Cooldowns (MVP centerpiece).

Did you get the expected number of major-cooldown casts, and (later) were they timed
like the Top Parses? This is the highest-signal, clearest "you did X wrong" dimension.
"""

from __future__ import annotations

from wowanalyze.diff.base import ActorFightData, DiffDimension
from wowanalyze.models import Dimension, Finding, ReferenceProfile, Severity


class CooldownDimension(DiffDimension):
    dimension = Dimension.cooldowns

    def evaluate(
        self, data: ActorFightData, profile: ReferenceProfile
    ) -> list[Finding]:
        findings: list[Finding] = []

        for metric in profile.metrics:
            if metric.dimension is not Dimension.cooldowns:
                continue
            if not metric.key.startswith("cast_count:"):
                continue

            ability = metric.key.split(":", 1)[1]
            yours = float(data.cast_counts.get(ability, 0))
            expected = metric.median

            # Only flag when you're clearly low — below the top parses' 25th percentile
            # (not merely under the median, where half the field sits by definition).
            low_bar = metric.p25 if metric.p25 is not None else expected
            missed = expected - yours
            if yours < low_bar and missed >= 1:
                severity = Severity.critical if missed >= 2 else Severity.major
                findings.append(
                    Finding(
                        dimension=self.dimension,
                        severity=severity,
                        title=f"Missed {missed:.0f}× {ability}",
                        detail=(
                            f"You cast {ability} {yours:.0f}× this pull; the top "
                            f"{profile.build.label} parses averaged {expected:.0f}×. "
                            f"Each missed use of a major cooldown is a large chunk of "
                            f"lost throughput."
                        ),
                        your_value=yours,
                        reference_value=expected,
                        unit=metric.unit,
                        # Rough proxy until we weight by ability value; more missed = worse.
                        impact_score=missed,
                    )
                )

        # TODO(cooldowns): timing analysis — compare cast timestamps against Top-Parse
        # windows (on pull, burst windows, add waves), which needs phase alignment.
        return findings
