import type { ObservedPlay } from "../types";

export function ObservedCasts({ observed }: { observed: ObservedPlay }) {
  const rows = Object.entries(observed.cast_counts).sort((a, b) => b[1] - a[1]);
  const minutes = observed.duration_ms / 60000;

  return (
    <div className="observed">
      <h3>
        What you cast{" "}
        <span className="muted">· {Math.round(observed.duration_ms / 1000)}s</span>
      </h3>
      {rows.length === 0 ? (
        <p className="muted">No casts found for this pull.</p>
      ) : (
        <table className="casts">
          <thead>
            <tr>
              <th>Ability</th>
              <th>Casts</th>
              <th>/min</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([name, count]) => (
              <tr key={name}>
                <td>{name}</td>
                <td>{count}</td>
                <td>{minutes > 0 ? (count / minutes).toFixed(1) : "–"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
