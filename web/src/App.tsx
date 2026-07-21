import { useState } from "react";
import { analyze, fetchReport, parseReportCode } from "./api";
import { FindingList } from "./components/FindingList";
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
                onChange={(e) =>
                  setFight(report.fights[Number(e.target.value)] ?? null)
                }
                defaultValue=""
              >
                <option value="" disabled>
                  Choose a pull…
                </option>
                {report.fights.map((f, i) => (
                  <option key={f.fight_id} value={i}>
                    {f.boss_name} — {f.kill ? "Kill" : "Wipe"}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>You (character)</label>
              <select
                onChange={(e) =>
                  setActor(report.actors[Number(e.target.value)] ?? null)
                }
                defaultValue=""
              >
                <option value="" disabled>
                  Choose your character…
                </option>
                {report.actors.map((a, i) => (
                  <option key={a.actor_id} value={i}>
                    {a.name}
                    {a.spec ? ` (${a.spec})` : ""}
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
            {a.target.character_name ?? "Player"} — {a.boss_name ?? "?"}
            {a.build ? ` · ${a.build.label}` : ""}
          </h2>
          <FindingList findings={a.findings} />
        </section>
      ))}
    </main>
  );
}
