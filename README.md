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
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .            # makes `wowanalyze` importable
cp .env.example .env        # then fill in your WCL credentials

# run the API locally
uvicorn api.index:app --reload --port 8000

# discover current-tier encounter IDs, then build reference profiles
python -m scripts.precompute --list-zones
python -m scripts.precompute --spec "havoc" --difficulty mythic --boss <encounterID>
```

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
