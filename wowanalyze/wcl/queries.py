"""GraphQL query strings for the WCL API v2.

Kept as plain strings (not a client library) to stay dependency-light and to make the
exact points cost of each call obvious. Variables are passed separately.
"""

# List a report's fights and players — cheap. Powers the UI's Pull/Actor pickers.
REPORT_SUMMARY = """
query ReportSummary($code: String!) {
  reportData {
    report(code: $code) {
      title
      fights(killType: Encounters) {
        id
        encounterID
        name
        difficulty
        kill
        startTime
        endTime
        friendlyPlayers
      }
      masterData {
        actors(type: "Player") {
          id
          name
          subType
        }
      }
    }
  }
}
"""

# Discover the current tier's zones/encounters. Run once per patch to seed configs;
# do NOT hard-code encounter IDs anywhere.
LIST_ZONES = """
query ListZones {
  worldData {
    zones {
      id
      name
      encounters { id name }
    }
  }
}
"""

# Top-parse rankings for a spec on an encounter — the reference population.
# `characterRankings` is a JSON scalar: { rankings: [ { name, amount,
# report: { code, fightID }, ... } ], hasMorePages, ... }.
ENCOUNTER_RANKINGS = """
query EncounterRankings(
  $encounterId: Int!, $difficulty: Int!, $className: String!,
  $specName: String!, $page: Int!
) {
  worldData {
    encounter(id: $encounterId) {
      name
      characterRankings(
        difficulty: $difficulty
        className: $className
        specName: $specName
        metric: dps
        page: $page
      )
    }
  }
}
"""

# Per-actor cast/aura tables for one fight — the input to the diff. Table queries are
# the expensive ones; used sparingly (one report live, top parses only in precompute).
# TODO(diff): split into casts / buffs / debuffs / damage-taken as each Dimension needs.
ACTOR_TABLE = """
query ActorTable(
  $code: String!, $fightId: Int!, $sourceId: Int!, $dataType: TableDataType!
) {
  reportData {
    report(code: $code) {
      table(
        fightIDs: [$fightId]
        sourceID: $sourceId
        dataType: $dataType
      )
    }
  }
}
"""

# One Target's casts for one fight, plus that fight's timing (for duration/CPM).
# The `table` field is a JSON scalar; for dataType Casts each entry is an ability
# with a `total` cast count.
ACTOR_CASTS = """
query ActorCasts($code: String!, $fightId: Int!, $sourceId: Int!) {
  reportData {
    report(code: $code) {
      fights(fightIDs: [$fightId]) {
        startTime
        endTime
        encounterID
        difficulty
      }
      table(fightIDs: [$fightId], sourceID: $sourceId, dataType: Casts)
    }
  }
}
"""

# Just a report's players (id + name) — for resolving a ranked parse's sourceID by
# name. Lighter than REPORT_SUMMARY (no fights list).
REPORT_ACTORS = """
query ReportActors($code: String!) {
  reportData {
    report(code: $code) {
      masterData {
        actors(type: "Player") { id name }
      }
    }
  }
}
"""
