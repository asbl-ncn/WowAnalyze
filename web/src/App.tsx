import { useState } from "react";
import { analyze, fetchReport, parseReportCode } from "./api";
import { FindingList } from "./components/FindingList";
import { ObservedCasts } from "./components/ObservedCasts";
import type { ActorSummary, AnalysisResult, FightSummary, ReportSummary } from "./types";

export default function App() {
  const [url, setUrl] = useState("");
  const [report, setReport] = useState<ReportSummary | null>(null);
  const [fight, setFight] = useState<FightSummary | null>(null);
  const [actor, setActor] = useState<ActorSummary | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function loadReport() {
    setError(null);
    setResult(null);
    const code = parseReportCode(url);
    if (!code) {
      setError("That doesn't look like a WarcraftLogs report link or code.");
      return;
    }
    setBusy(true);
    try {
      setReport(await fetchReport(code));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function runAnalysis() {
    if (!report || !fight || !actor) return;
    setBusy(true);
    setError(null);
    try {
      setResult(
        await analyze([
          {
            report_code: report.report_code,
            fight_id: fight.fight_id,
            actor_id: actor.actor_id,
            character_name: actor.name,
            spec: actor.spec,
          },
        ]),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  // Once a pull is picked, only show the characters who were actually in it —
  // a full report can carry hundreds of players across all fights.
  const visibleActors =
    report && fight
      ? report.actors.filter((a) => fight.participant_ids.includes(a.actor_id))
      : [];

  return (
    <main className="app">
      <header>
        <h1>WowAnalyze</h1>
        <p className="muted">
          Paste a WarcraftLogs report, pick your pull, and see what you did wrong versus
          the top parses.
        </p>
      </header>

      <section className="card">
        <label htmlFor="report">Report link or code</label>
        <div className="row">
          <input
            id="report"
            value={url}
            placeholder="https://www.warcraftlogs.com/reports/…"
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && loadReport()}
          />
          <button onClick={loadReport} disabled={busy}>
            Load
          </button>
        </div>
      </section>

      {report && (
        <section className="card">
          <div className="row">
            <div className="field">
              <label>Pull</label>
              <select
                onChange={(e) => {
                  setFight(report.fights[Number(e.target.value)] ?? null);
                  setActor(null); // roster changes with the pull
                }}
                defaultValue=""
              >
                <option value="" disabled>
                  Choose a pull…
                </option>
                {report.fights.map((f, i) => (
                  <option key={f.fight_id} value={i}>
                    {f.boss_name} · {f.kill ? "Kill" : "Wipe"} ·{" "}
                    {Math.round(f.duration_ms / 1000)}s
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>You (character)</label>
              <select
                value={
                  actor ? String(visibleActors.indexOf(actor)) : ""
                }
                onChange={(e) =>
                  setActor(visibleActors[Number(e.target.value)] ?? null)
                }
                disabled={!fight}
              >
                <option value="" disabled>
                  {fight ? "Choose your character…" : "Pick a pull first"}
                </option>
                {visibleActors.map((a, i) => (
                  <option key={a.actor_id} value={i}>
                    {a.name}
                    {a.class_name ? ` – ${a.class_name}` : ""}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <button onClick={runAnalysis} disabled={busy || !fight || !actor}>
            Analyze
          </button>
        </section>
      )}

      {error && <p className="error">{error}</p>}

      {result?.analyses.map((a, i) => (
        <section className="card" key={i}>
          <h2>
            {a.target.character_name ?? "Player"} —{" "}
            {a.boss_name ?? fight?.boss_name ?? "?"}
            {a.build ? ` · ${a.build.label}` : ""}
          </h2>
          {a.observed && <ObservedCasts observed={a.observed} />}
          <FindingList findings={a.findings} />
        </section>
      ))}
    </main>
  );
}
