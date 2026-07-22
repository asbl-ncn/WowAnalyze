"""Test the ACTOR_CASTS -> ActorFightData mapping with a canned WCL response."""

from __future__ import annotations

from wowanalyze.wcl.actor import map_actor_casts

_SAMPLE = {
    "reportData": {
        "report": {
            "fights": [
                {
                    "startTime": 1000,
                    "endTime": 205000,
                    "encounterID": 3177,
                    "difficulty": 5,
                }
            ],
            "casts": {
                "data": {
                    "entries": [
                        {"name": "Lava Burst", "total": 40},
                        {"name": "Lightning Bolt", "total": 55},
                        {"name": "Stormkeeper", "total": 3},
                    ]
                }
            },
            "debuffs": {
                "data": {
                    "auras": [
                        {"name": "Flame Shock", "totalUptime": 190000},
                    ]
                }
            },
        }
    }
}


def test_maps_duration_casts_boss_and_uptime():
    data = map_actor_casts(_SAMPLE)

    assert data.duration_ms == 204000  # 205000 - 1000
    assert data.boss_id == 3177
    assert data.difficulty_id == 5
    assert data.cast_counts["Lava Burst"] == 40
    assert data.debuff_uptime_ms["Flame Shock"] == 190000


def test_empty_tables_are_safe():
    data = map_actor_casts(
        {"reportData": {"report": {"fights": [], "casts": {}, "debuffs": {}}}}
    )
    assert data.duration_ms == 0
    assert data.cast_counts == {}
    assert data.debuff_uptime_ms == {}
