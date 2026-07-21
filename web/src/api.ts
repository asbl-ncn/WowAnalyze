import type { AnalysisResult, Difficulty, ReportSummary, Target } from "./types";

// A WCL report URL looks like https://www.warcraftlogs.com/reports/<code>#...
// Accept either a full URL or a bare code.
export function parseReportCode(input: string): string | null {
  const trimmed = input.trim();
  const match = trimmed.match(/reports\/([a-zA-Z0-9]+)/);
  if (match) return match[1];
  if (/^[a-zA-Z0-9]{10,}$/.test(trimmed)) return trimmed;
  return null;
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function fetchReport(code: string): Promise<ReportSummary> {
  return json<ReportSummary>(await fetch(`/api/report/${encodeURIComponent(code)}`));
}

export async function analyze(
  targets: Target[],
  difficulty: Difficulty = "mythic",
): Promise<AnalysisResult> {
  const res = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ targets, difficulty }),
  });
  return json<AnalysisResult>(res);
}
