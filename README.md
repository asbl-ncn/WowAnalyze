# WowAnalyze

A free, git-native **World of Warcraft Mythic-raid coach**. Paste a WarcraftLogs
report, pick your pull, and get a ranked list of what you did wrong — measured against
what the **top parsers actually did** on that boss, in your build, this patch.

Not a WoWAnalyzer clone: the standard is *empirical and auto-recomputed*, not
hand-coded. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the why, and
[`docs/ROADMAP.md`](docs/ROADMAP.md) for the plan. Vocabulary lives in
[`CONTEXT.md`](CONTEXT.md).

> Status: **scaffold.** The structure, data model, and docs are in place; the diff
> dimensions and precompute are stubs with clear TODOs. This is a skeleton to react to,
> not a working analyzer yet.

## Layout

```
wowanalyze/        Python engine (WCL client, models, diff dimensions, reference) — shared
api/               FastAPI serverless function (Vercel) — the live fetch + diff
scripts/           precompute.py — the scheduled reference builder
data/reference/    committed Reference Profile JSON — "git is the database"
web/               React + Vite (TypeScript) frontend
.github/workflows/ precompute.yml — scheduled reference build, commits results back
tests/             pytest
```

## Getting a WarcraftLogs API client

1. Log in at warcraftlogs.com → **Settings → API Clients** → create a client.
2. Copy the **Client ID** and **Client Secret**.
3. Provide them as env vars locally, as Vercel environment variables, and as GitHub
   Actions repository secrets:
   - `WCL_CLIENT_ID`
   - `WCL_CLIENT_SECRET`

## Local development

Backend / engine (Python 3.11+):

```bash
# 1. create + activate a virtualenv
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

# 2. install the package + dev tools (uvicorn, pytest) in one shot
pip install -e ".[dev]"              # includes app deps; no separate requirements.txt step

# 3. credentials
cp .env.example .env                 # Windows: copy .env.example .env  — then fill in WCL creds

# 4. run the API locally (use `python -m uvicorn` — more reliable on Windows PATH)
python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8000

# discover current-tier encounter IDs (only when the tier changes)
python -m scripts.precompute --list-zones

# confirm the rankings shape, then build a reference profile for one spec+boss
python -m scripts.precompute --dump-rankings --spec shaman-elemental --boss 3177
python -m scripts.precompute --spec shaman-elemental --boss 3177 --top 20

# or build the whole configured seed set (scripts/seeds.py)
python -m scripts.precompute --seeds --top 20
```

> Windows note: if uvicorn fails with `WinError 10013` (socket access forbidden), the
> port is in a Windows-reserved range — pick another, e.g. `--port 8123`. The Vite dev
> proxy defaults to `:8000`; adjust `web/vite.config.ts` if you change it.

Frontend:

```bash
cd web
npm install
npm run dev                 # Vite dev server, proxies /api to :8000
```

## Deploy (free)

- **Vercel Hobby** — connect the repo; it builds `web/` and runs `api/`. Set the two
  WCL env vars in the Vercel dashboard.
- **GitHub Actions** — add the two secrets; the precompute workflow runs on a schedule
  and commits refreshed profiles under `data/reference/`.
