import type { Finding } from "../types";

const SEVERITY_ORDER = ["critical", "major", "minor", "info"] as const;

export function FindingList({ findings }: { findings: Finding[] }) {
  if (findings.length === 0) {
    return <p className="muted">No findings — either clean, or no reference profile yet.</p>;
  }

  const sorted = [...findings].sort(
    (a, b) =>
      SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity) ||
      b.impact_score - a.impact_score,
  );

  return (
    <ul className="findings">
      {sorted.map((f, i) => (
        <li key={i} className={`finding sev-${f.severity}`}>
          <div className="finding-head">
            <span className={`badge sev-${f.severity}`}>{f.severity}</span>
            <span className="dim">{f.dimension}</span>
            <strong>{f.title}</strong>
          </div>
          <p>{f.detail}</p>
          {f.reference_value != null && (
            <p className="muted">
              you {f.your_value} · top parses {f.reference_value} {f.unit}
            </p>
          )}
        </li>
      ))}
    </ul>
  );
}
