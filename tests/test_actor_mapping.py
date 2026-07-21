"""Test the ACTOR_CASTS -> ActorFightData mapping with a canned WCL response."""

from __future__ import annotations

from wowanalyze.wcl.actor import map_actor_casts

_SAMPLE = {
    "reportData": {
        "report": {
            "fights": [{"startTime": 1000, "endTime": 205000}],
            "table": {
                "data": {
                    "entries": [
                        {"name": "Lava Burst", "total": 40},
                        {"name": "Lightning Bolt", "total": 55},
                        {"name": "Stormkeeper", "total": 3},
                    ]
                }
            },
        }
    }
}


def test_maps_duration_and_casts():
    data = map_actor_casts(_SAMPLE)

    assert data.duration_ms == 204000  # 205000 - 1000
    assert data.cast_counts["Lava Burst"] == 40
    assert data.cast_counts["Stormkeeper"] == 3


def test_empty_table_is_safe():
    data = map_actor_casts({"reportData": {"report": {"fights": [], "table": {}}}})
    assert data.duration_ms == 0
    assert data.cast_counts == {}
