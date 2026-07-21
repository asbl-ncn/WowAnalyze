"""Fetch and normalize one Target's fight data into ActorFightData.

This is the boundary between "talking to WCL" and "analyzing". Same split as
report.py: `map_actor_casts` is a pure function (dict -> ActorFightData), and
`fetch_actor_fight_data` is the thin live wrapper. The precompute reuses the exact
same fetch for each Top Parse, so getting it right here pays off 100x later.

Currently only the Casts table is wired (Dimension 1 groundwork). Buffs/debuffs,
active time, and deaths follow as the other Dimensions come online.
"""

from __future__ import annotations

from typing import Any

from wowanalyze.diff.base import ActorFightData


def map_actor_casts(data: dict[str, Any]) -> ActorFightData:
    """Map an ACTOR_CASTS response into ActorFightData (duration + cast counts)."""
    report = (data.get("reportData") or {}).get("report") or {}

    fights = report.get("fights") or []
    duration_ms = 0
    if fights:
        f = fights[0]
        duration_ms = int((f.get("endTime") or 0) - (f.get("startTime") or 0))

    cast_counts: dict[str, int] = {}
    table = report.get("table") or {}
    for entry in (table.get("data") or {}).get("entries") or []:
        name = entry.get("name")
        if not name:
            continue
        # In a Casts table, `total` is the number of casts of that ability.
        cast_counts[name] = int(entry.get("total") or 0)

    return ActorFightData(duration_ms=duration_ms, cast_counts=cast_counts)


async def fetch_actor_fight_data(
    code: str, fight_id: int, source_id: int, client: Any | None = None
) -> ActorFightData:
    """Live: fetch one Target's casts for one fight and normalize them."""
    from wowanalyze.wcl.client import WCLClient
    from wowanalyze.wcl.queries import ACTOR_CASTS

    client = client or WCLClient()
    data = await client.query(
        ACTOR_CASTS,
        {"code": code, "fightId": fight_id, "sourceId": source_id},
    )
    return map_actor_casts(data)
