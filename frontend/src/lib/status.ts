import type { CheckStatus, Recorder } from "../types";

const SEVERITY: Record<CheckStatus, number> = {
  offline: 4,
  checking: 3,
  unknown: 2,
  online: 1,
  disabled: 0,
};

export function effectiveStatus(recorder: Recorder): CheckStatus {
  if (!recorder.enabled) return "disabled";
  return recorder.last_status ?? "unknown";
}

export function aggregateStatus(recorders: Recorder[]): CheckStatus {
  if (recorders.length === 0) return "unknown";
  const statuses = recorders.map(effectiveStatus);
  if (statuses.every((s) => s === "disabled")) return "disabled";
  let worst: CheckStatus = "disabled";
  let worstScore = -1;
  for (const s of statuses) {
    if (s === "disabled") continue;
    const score = SEVERITY[s];
    if (score > worstScore) {
      worstScore = score;
      worst = s;
    }
  }
  return worstScore >= 0 ? worst : "unknown";
}

export const STATUS_LABELS: Record<CheckStatus, string> = {
  online: "Доступен",
  offline: "Недоступен",
  unknown: "Не проверялся",
  disabled: "Выключен",
  checking: "Проверка…",
};

export const STATUS_DOT: Record<CheckStatus, string> = {
  online: "bg-status-ok",
  offline: "bg-status-error",
  unknown: "bg-status-unknown",
  disabled: "bg-muted",
  checking: "bg-accent animate-pulse",
};
