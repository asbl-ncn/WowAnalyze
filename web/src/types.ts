// Mirrors wowanalyze/models.py. Keep in sync with the backend Pydantic models.

export type Difficulty = "normal" | "heroic" | "mythic";
export type Dimension = "cooldowns" | "rotation" | "uptime" | "survival";
export type Severity = "critical" | "major" | "minor" | "info";
export type Role = "dps" | "healer" | "tank";

export interface Target {
  report_code: string;
  fight_id: number;
  actor_id: number;
  character_name?: string | null;
  spec?: string | null;
}

export interface FightSummary {
  fight_id: number;
  boss_id: number;
  boss_name: string;
  difficulty?: Difficulty | null;
  kill: boolean;
  duration_ms: number;
  participant_ids: number[];
}

export interface ActorSummary {
  actor_id: number;
  name: string;
  class_name?: string | null;
  spec?: string | null;
  role?: Role | null;
}

export interface ReportSummary {
  report_code: string;
  title?: string | null;
  fights: FightSummary[];
  actors: ActorSummary[];
}

export interface Finding {
  dimension: Dimension;
  severity: Severity;
  title: string;
  detail: string;
  your_value?: number | null;
  reference_value?: number | null;
  unit: string;
  impact_score: number;
}

export interface ObservedPlay {
  duration_ms: number;
  cast_counts: Record<string, number>;
}

export interface TargetAnalysis {
  target: Target;
  boss_name?: string | null;
  build?: { key: string; label: string } | null;
  observed?: ObservedPlay | null;
  findings: Finding[];
}

export interface AnalysisResult {
  report_code: string;
  analyses: TargetAnalysis[];
}
