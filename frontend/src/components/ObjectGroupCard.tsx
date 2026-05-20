import { ChevronDown, ChevronRight } from "lucide-react";
import type { ObjectGroup, Recorder } from "../types";
import { offlineCount } from "../lib/grouping";
import { STATUS_DOT, STATUS_LABELS } from "../lib/status";
import { cn } from "../lib/utils";
import { RecorderRow } from "./RecorderRow";

const COLLAPSE_KEY = "wisenet-collapsed-objects";

export function loadCollapsed(): Set<string> {
  try {
    const raw = localStorage.getItem(COLLAPSE_KEY);
    if (!raw) return new Set();
    return new Set(JSON.parse(raw) as string[]);
  } catch {
    return new Set();
  }
}

export function saveCollapsed(set: Set<string>) {
  localStorage.setItem(COLLAPSE_KEY, JSON.stringify([...set]));
}

interface ObjectGroupCardProps {
  group: ObjectGroup;
  expanded: boolean;
  onToggle: () => void;
  checkingId: string | null;
  onCheckStart: (id: string) => void;
  onCheckEnd: (recorder: Recorder) => void;
  onEdit: (recorder: Recorder) => void;
  onDelete: (recorder: Recorder) => void;
}

export function ObjectGroupCard({
  group,
  expanded,
  onToggle,
  ...rowProps
}: ObjectGroupCardProps) {
  const offline = offlineCount(group.recorders);
  const total = group.recorders.length;

  return (
    <section className="overflow-hidden rounded-lg border border-border bg-surface">
      <button
        type="button"
        className="flex w-full items-center gap-3 px-4 py-4 text-left hover:bg-elevated/50 sm:px-6"
        onClick={onToggle}
        aria-expanded={expanded}
      >
        {expanded ? (
          <ChevronDown className="h-5 w-5 shrink-0 text-muted" />
        ) : (
          <ChevronRight className="h-5 w-5 shrink-0 text-muted" />
        )}
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-semibold">{group.objectName}</h2>
            <span className="rounded bg-elevated px-2 py-0.5 text-xs text-secondary">
              {total} NVR
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "h-2 w-2 rounded-full",
              STATUS_DOT[group.aggregateStatus]
            )}
            title={STATUS_LABELS[group.aggregateStatus]}
          />
          {offline > 0 && (
            <span className="text-xs text-status-error">
              {offline} из {total} недоступен
            </span>
          )}
        </div>
      </button>
      {expanded && (
        <div className="border-t border-border">
          {group.recorders.map((r) => (
            <RecorderRow key={r.id} recorder={r} {...rowProps} />
          ))}
        </div>
      )}
    </section>
  );
}
