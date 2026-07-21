"""Fetch a report's Fights + Actors and map them to our models.

Powers the UI's Pull/Actor pickers. Cheap (one metadata query, no event tables).

The mapping is split from the fetch on purpose: `map_report_summary` is a pure function
(dict -> ReportSummary) that is trivially unit-testable without any network or WCL
client, and `fetch_report_summary` is the thin live wrapper.
"""

from __future__ import annotations

from typing import Any

from wowanalyze.models import (
    ActorSummary,
    Difficulty,
    FightSummary,
    ReportSummary,
)

# WCL raid difficulty ids. Anything else (LFR, timewalking, null for trash) -> None.
_DIFFICULTY_BY_ID: dict[int, Difficulty] = {
    3: Difficulty.normal,
    4: Difficulty.heroic,
    5: Difficulty.mythic,
}


def map_report_summary(code: str, data: dict[str, Any]) -> ReportSummary:
    """Map a REPORT_SUMMARY GraphQL response into a ReportSummary."""
    report = (data.get("reportData") or {}).get("report")
    if report is None:
        raise ValueError(f"Report {code!r} was not found or is not accessible.")

    fights: list[FightSummary] = []
    for f in report.get("fights") or []:
        start = f.get("startTime") or 0
        end = f.get("endTime") or 0
        fights.append(
            FightSummary(
                fight_id=f["id"],
                boss_id=f.get("encounterID") or 0,
                boss_name=f.get("name") or "Unknown",
                difficulty=_DIFFICULTY_BY_ID.get(f.get("difficulty")),
                kill=bool(f.get("kill")),
                duration_ms=int(end - start),
                participant_ids=list(f.get("friendlyPlayers") or []),
            )
        )

    actors: list[ActorSummary] = []
    for a in (report.get("masterData") or {}).get("actors") or []:
        actors.append(
            ActorSummary(
                actor_id=a["id"],
                name=a.get("name") or "?",
                # `subType` is the class for players (e.g. "Shaman"). Spec/role need
                # combatantInfo/talent data — a later slice.
                class_name=a.get("subType"),
                spec=None,
                role=None,
            )
        )

    return ReportSummary(
        report_code=code,
        title=report.get("title"),
        fights=fights,
        actors=actors,
    )


async def fetch_report_summary(code: str, client: Any | None = None) -> ReportSummary:
    """Live: run REPORT_SUMMARY against WCL and map the result."""
    # Imported lazily so the pure mapper (and its tests) don't pull in httpx.
    from wowanalyze.wcl.client import WCLClient
    from wowanalyze.wcl.queries import REPORT_SUMMARY

    client = client or WCLClient()
    data = await client.query(REPORT_SUMMARY, {"code": code})
    return map_report_summary(code, data)
