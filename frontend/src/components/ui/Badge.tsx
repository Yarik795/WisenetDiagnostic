import type { CheckStatus } from "../../types";
import { STATUS_DOT, STATUS_LABELS } from "../../lib/status";
import { cn } from "../../lib/utils";

interface StatusBadgeProps {
  status: CheckStatus;
  compact?: boolean;
  error?: string | null;
}

export function StatusBadge({ status, compact, error }: StatusBadgeProps) {
  const label = STATUS_LABELS[status];
  const title = error ?? label;

  if (compact) {
    return (
      <span
        className={cn("inline-block h-2 w-2 rounded-full", STATUS_DOT[status])}
        title={title}
        aria-label={label}
      />
    );
  }

  return (
    <span
      className="inline-flex items-center gap-2 text-sm"
      title={title}
    >
      <span
        className={cn("h-2 w-2 shrink-0 rounded-full", STATUS_DOT[status])}
        aria-hidden
      />
      <span className="text-secondary">{label}</span>
    </span>
  );
}
