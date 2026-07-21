# Glossary

The canonical vocabulary for WowAnalyze. One term, one meaning. If a word here
starts drifting in conversation or code, fix the drift — don't overload the term.

This file is a glossary and nothing else. Architecture lives in `docs/ARCHITECTURE.md`;
the phased plan lives in `docs/ROADMAP.md`.

---

**Report**
A WarcraftLogs log upload, identified by its report *code* (the string in the URL,
e.g. `a1B2c3D4`). A report contains many fights and many players. A report is never
"a fight" — it is the container.

**Fight** / **Pull**
One encounter attempt inside a report — a single boss pull, kill or wipe. Identified
by a `fight_id` that is unique *within its report*. "Pull" and "Fight" are synonyms;
we prefer **Pull** in user-facing text, **Fight** in code that mirrors the WCL API.

**Actor**
A participant in a fight as the WCL API sees it, identified by a `source id` that is
unique within its report. The player *you* are analyzing is one Actor among many.

**Target**
The atomic unit of analysis: one `(Report, Fight, Actor)` triple — i.e. "this player,
on this pull." **Every analysis is a list of Targets.** One Target = single-player
coaching. Two Targets = side-by-side diff. N Targets = raid-wide coaching. The engine
never special-cases the count; more Targets is the only difference.

**Spec**
A class specialization (e.g. Havoc Demon Hunter, Fire Mage). The unit at which the
reference model is organized.

**Build Cluster** (or just **Build**)
A grouping of top parses that play the same way: same hero-talent tree plus the key
talent choices that change the rotation (e.g. single-target vs cleave). A Spec on a
given boss usually has a small number of Build Clusters. You are only ever compared
against parses in *your* Build Cluster — never a blended average across builds.

**Reference Profile**
The precomputed, aggregated behavior of the top-ranked parses for one
`(Spec, Build Cluster, Boss, Difficulty)` in the current patch. It is derived data:
"what the best players in your build actually did on this boss." It is **not** a
hand-written statement of ideal play. Stored as JSON committed to the repo.

**Top Parses**
The reference population: the top ~100 Mythic **kills** for a `(Spec, Boss)`, ranked
by rDPS. Kills only — wipes are excluded from the reference. The number and metric are
configurable but this is the default.

**Dimension**
One axis of analysis. There are four, in MVP priority order:
`cooldowns` → `rotation` → `uptime` → `survival`.

**Finding**
One detected gap between a Target and its Reference Profile, on one Dimension. Carries
a severity, a plain-language explanation, your value, the reference value, and an
`impact_score` used to rank Findings (and, later, to rank players raid-wide).

**Guardrail**
A thin layer of hand-coded domain rules that sits on top of the empirical diff to
suppress or correct misleading Findings (e.g. "ignore add-padding on this boss",
"this proc is only wasted if unused within 2s"). Guardrails exist because
*top parsers doing X* does not always mean *you should do X* — correlation is not
optimal play.

**Precompute**
The scheduled GitHub Actions job that builds Reference Profiles from Top Parses and
commits the resulting JSON back to the repo. The repo — not a database — is the store.
