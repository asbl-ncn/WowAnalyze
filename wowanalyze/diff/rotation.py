"""Dimension 2 — Rotation & ability usage.

Casts-per-minute of key abilities, activity/GCD uptime (time spent doing nothing), and
resource overcapping. Catches sloppy moment-to-moment play.
"""

from __future__ import annotations

from wowanalyze.diff.base import ActorFightData, DiffDimension
from wowanalyze.models import Dimension, Finding, ReferenceProfile, Severity


class RotationDimension(DiffDimension):
    dimension = Dimension.rotation

    def evaluate(
        self, data: ActorFightData, profile: ReferenceProfile
    ) -> list[Finding]:
        findings: list[Finding] = []

        # Activity / GCD uptime — a spec-agnostic, high-signal rotation check.
        if data.active_time_ms is not None and data.duration_ms > 0:
            activity = data.active_time_ms / data.duration_ms
            ref = next(
                (m for m in profile.metrics if m.key == "activity"), None
            )
            target = ref.median if ref else 0.95
            if activity < target - 0.03:
                findings.append(
                    Finding(
                        dimension=self.dimension,
                        severity=Severity.major if activity < target - 0.08 else Severity.minor,
                        title=f"Low activity ({activity:.0%})",
                        detail=(
                            f"You were actively casting {activity:.0%} of the fight; "
                            f"top {profile.build.label} parses sit around {target:.0%}. "
                            f"Dead GCDs are lost damage — usually movement or hesitation."
                        ),
                        your_value=round(activity, 3),
                        reference_value=round(target, 3),
                        unit="fraction",
                        impact_score=(target - activity) * 10,
                    )
                )

        # TODO(rotation): key-ability CPM deltas and resource overcap Findings,
        # driven by `cast_count:` and `overcap:` metrics in the profile.
        return findings
