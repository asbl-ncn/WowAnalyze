# Roadmap

Phased so the MVP stays tight while the data model (see the **Target** concept in
[`../CONTEXT.md`](../CONTEXT.md)) is built for the full ambition from day one.

Legend: 🟢 scaffolded · 🟡 partial · ⚪ not started

---

## v1 — Single-player coach (MVP)

The vertical slice: paste a report, pick your Actor + Pull, get ranked Findings.

- 🟢 Repo scaffold, engine package, docs, CI workflow stub
- 🟢 `Target` data model and multi-Target-ready orchestration
- 🟢 WCL client — OAuth client-credentials + GraphQL (`wowanalyze/wcl/`)
- 🟢 `/api/report/{code}` — list Fights + Actors so the UI can offer pickers
      (fight-scoped roster + class; validated live against a real report)
- 🟡 `/api/analyze` — live per-Target casts fetch; returns **observed** casts even
      before a reference exists (Dimension 1 groundwork; diff activates once profiles land)
- 🟡 Precompute: pull Top Parses → resolve sourceIDs → fetch casts → aggregate →
      Reference Profile JSON. Single **provisional** blended cluster for now
      (Build-Cluster segmentation still ⚪); `--dump-rankings` + `--top` to control cost.
- 🟡 **Dimension 1 — Cooldowns**: flags casts below the top parses' 25th percentile.
      Still treats every ability as a cast-count metric — major-CD tagging + guardrails ⚪
- ⚪ **Dimension 2 — Rotation**: key-ability CPM, activity/GCD uptime, resource overcap
- ⚪ **Dimension 3 — Uptime**: buff/debuff uptime you're responsible for
- ⚪ **Dimension 4 — Survival**: defensive-CD usage, avoidable damage, deaths
- ⚪ Findings UI: ranked list by `impact_score`, grouped by Dimension
- ⚪ Thin **Guardrail** layer (start with: exclude add-padding, proc-window sanity)

**Seed targets for validation:** the maintainer's mains — **Elemental Shaman**
(`elemental`) and **Shadow Priest** (`shadow`) — configured in `scripts/seeds.py`
alongside a real validation report. Boss/encounter IDs for the current tier are
discovered via `python -m scripts.precompute --list-zones` (do not hard-code a tier).

**Definition of done for v1:** for the seeded spec+boss, paste a real report → get
Findings that a competent player agrees with when they eyeball the log.

## v1.5 — Auto-derived reference hub

Falls out of data the Precompute already collects — zero hand-writing, self-updating.

- ⚪ Most-common **Build Clusters** per spec+boss (talent strings + prevalence)
- ⚪ Typical stat lines of Top Parses
- ⚪ Ability-usage frequencies ("top Havoc casts Eye Beam ~N times / pull here")
- ⚪ Reference-hub pages in the frontend

## v2 — Multi-Target

Same engine, more Targets. No rewrite — this is the payoff of the Target model.

- ⚪ **Side-by-side diff**: your Pull vs a chosen Top Parse — two aligned, annotated
  cooldown timelines (the flagship visual; React + Recharts/visx)
- ⚪ **Guild / raid-wide coaching**: analyze the whole roster in one report; rank
  players by biggest fixable gap and by estimated raid-DPS / survival impact
- ⚪ Phase-aware timeline alignment (hard; needed for honest CD-timing comparison)

## v3 — Ecosystem fusion

Merge the scattered sites into one view.

- ⚪ Your stat line vs the Top-Parse stat profile
- ⚪ Sim-based stat weights / trinket rankings (Bloodmallet-style static data first;
  Raidbots later)
- ⚪ lorrgs-style cooldown timelines integrated alongside Findings

## Later / conditional

- ⚪ Public launch: swap JSON-in-git read path for a cache/KV if needed, add abuse
  protection and points-budget fairness, migrate to Postgres **only if** a datastore
  becomes necessary
- ⚪ Progression tracking over time — **only** if we accept adding a per-user store
  (explicitly deferred; it breaks the current DB-free design)
