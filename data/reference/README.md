# Reference Profiles — the JSON-in-git "database"

This directory holds the committed **Reference Profiles**: the aggregated behavior of
the Top Parses per `(Spec, Build Cluster, Boss, Difficulty)`. The precompute job
(`scripts/precompute.py`, run by GitHub Actions) writes them; the live API only reads.

Layout:

```
<spec>/<difficulty>/<bossId>__<buildKey>.json
e.g.  havoc/mythic/3009__havoc__aldrachi__single-target.json
```

Do not edit these by hand — they are regenerated each run. Git history *is* the
version log of how the reference standard shifts patch to patch.
