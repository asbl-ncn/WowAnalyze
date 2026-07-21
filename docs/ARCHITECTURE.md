# Architecture

WowAnalyze is a **free, git-native World of Warcraft Mythic-raid coach**. It tells you
what you did wrong by diffing your pull against how the best players actually played
that exact boss, in your exact build, this patch.

It is **not** a WoWAnalyzer clone. WoWAnalyzer checks your log against hand-written,
per-spec rules encoding a human's idea of ideal play. WowAnalyze checks your log
against the **empirical behavior of the top parses** — recomputed automatically every
patch, specific to the boss and to your build. See "Why not just WoWAnalyzer?" below.

Terms in **bold** are defined in [`../CONTEXT.md`](../CONTEXT.md).

---

## 1. The one design decision everything hangs off

**Every analysis is a list of Targets** — a Target being one `(Report, Fight, Actor)`.

```
1 Target   → single-player coaching          (v1)
2 Targets  → side-by-side diff (you vs top)  (v2)
N Targets  → raid-wide coaching              (v2)
```

The engine takes `list[Target]` and returns one `TargetAnalysis` per Target. Nothing
in the pipeline knows or cares how many Targets there are. This is what keeps the
ambitious roadmap from ever becoming a rewrite.

## 2. Data flow

```
                         ┌─────────────────────────────────────────┐
                         │  GitHub Actions (scheduled, free)        │
                         │  scripts/precompute.py                   │
                         │  ├─ pull Top Parses via WCL API          │
                         │  ├─ cluster by Build                     │
                         │  ├─ aggregate → Reference Profiles       │
                         │  └─ commit JSON to data/reference/       │
                         └───────────────────┬─────────────────────┘
                                             │ git commit (the "DB")
                                             ▼
   ┌──────────┐   paste    ┌──────────────────────────────┐   read    ┌──────────────┐
   │  Browser │ ─ report ─▶│  FastAPI on Vercel (api/)     │◀── JSON ──│ data/        │
   │  React   │            │  ├─ /api/report/{code}        │           │ reference/   │
   │  (Vite)  │◀─ findings─│  │   list Fights + Actors     │           │ (committed)  │
   └──────────┘            │  └─ /api/analyze  (Targets)   │           └──────────────┘
                           │      └─ wowanalyze engine     │
                           │           holds WCL secret    │
                           └───────────────┬───────────────┘
                                           │ WCL API v2 (GraphQL, OAuth)
                                           ▼
                                   warcraftlogs.com
```

Two paths, deliberately split by cost:

- **Reference Profiles are expensive** (many logs, deep data) → built *offline* by the
  scheduled **Precompute**, amortized across all users, committed as JSON.
- **A user's analysis is cheap** (one report, the chosen Actors) → done *live* by the
  serverless function: fetch the Target(s), diff against the already-committed profile.

This is what makes the WCL points budget survivable.

## 3. Components

| Path | What it is | Language |
|------|------------|----------|
| `wowanalyze/` | The analysis engine — WCL client, models, diff dimensions, reference build/load. Shared by the live API and the precompute job. | Python |
| `api/index.py` | FastAPI app exposed as a Vercel serverless function. Holds the WCL secret. | Python |
| `scripts/precompute.py` | Entry point the GitHub Action runs to build Reference Profiles. | Python |
| `data/reference/` | Committed Reference Profile JSON. **Git is the database.** | JSON |
| `web/` | React + Vite frontend: paste a report, pick Actor + Pull, render Findings and (later) timelines. | TypeScript |
| `.github/workflows/precompute.yml` | Schedules the Precompute and commits results back. | YAML |

The engine is written once, in Python, and imported by **both** `api/` (live) and
`scripts/` (offline). The diff logic never forks across languages.

## 4. WarcraftLogs API

- **API v2**, GraphQL, at `https://www.warcraftlogs.com/api/v2/client`.
- **OAuth client-credentials** flow. You register a client at
  *WCL → Settings → API Clients* and get a `client_id` + `client_secret`.
- The secret lives **only** server-side — as env vars on Vercel (live) and as GitHub
  Actions **secrets** (precompute). It is never shipped to the browser.
- Rate limited by a **per-hour points budget**. Every query costs points by complexity;
  event/table queries are dear. Mitigations: precompute the expensive part; cache
  aggressively; prefer summary tables over raw event streams where they suffice.

Required secrets (both environments): `WCL_CLIENT_ID`, `WCL_CLIENT_SECRET`.

## 5. Deployment (free)

- **Vercel Hobby** (free), connected to the private GitHub repo, auto-deploys on push.
  - Static: `web/` is built and served.
  - Serverless: `api/index.py` runs as a Python function.
  - See `vercel.json`. Python packaging on Vercel is the one fiddly bit — the engine
    at repo root must be importable from `api/`; `api/index.py` adjusts `sys.path`, and
    `vercel.json` may need `includeFiles` once we do a real deploy pass.
- **GitHub Actions** (free minutes) runs the Precompute on a schedule and on demand,
  then commits changed JSON under `data/reference/`.
- **No database, no always-on server** beyond the serverless function.

## 6. Why not just WoWAnalyzer?

|  | WoWAnalyzer | WowAnalyze |
|--|-------------|------------|
| Standard of "correct" | Hand-coded ideal, per spec | **Empirical** top-parse behavior |
| Freshness | Per-spec volunteer upkeep | **Auto-recomputed** each patch |
| Specificity | Generic to the spec | Per **boss** + per **build** |
| Spec coverage | Uneven (depends on maintainers) | Uniform — one engine, all specs |
| Scope | Single player, single log, no memory | **Multi-Target**: player → raid → side-by-side |

The trade-off, stated honestly: a purely statistical diff can mislead — top parsers
have better gear and comps and sometimes pad damage in ways that inflate a parse but
aren't better play (**correlation ≠ optimal**). That is exactly what the **Guardrail**
layer is for, and why phase-aware alignment is called out as hard work in the roadmap.

## 7. Non-goals (deliberately out of scope)

- No `/grill-me` chat and **no LLM** in the product. The coach is deterministic.
- No hand-written rotation/stat guides — the reference "hub" is auto-derived from the
  same Top Parses data (v1.5).
- No user accounts and **no progression-over-time tracking** in v1 — that is the one
  feature that would force a per-user database into a deliberately DB-free design.
