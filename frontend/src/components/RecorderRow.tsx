import { MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client";
import type { Recorder } from "../types";
import { effectiveStatus } from "../lib/status";
import {
  displayRecorderName,
  formatHostPort,
  formatTime,
} from "../lib/utils";
import { useToasts } from "../hooks/useToasts";
import { Button } from "./ui/Button";
import { StatusBadge } from "./ui/Badge";

interface RecorderRowProps {
  recorder: Recorder;
  checkingId: string | null;
  onCheckStart: (id: string) => void;
  onCheckEnd: (recorder: Recorder) => void;
  onEdit: (recorder: Recorder) => void;
  onDelete: (recorder: Recorder) => void;
}

export function RecorderRow({
  recorder,
  checkingId,
  onCheckStart,
  onCheckEnd,
  onEdit,
  onDelete,
}: RecorderRowProps) {
  const { push } = useToasts();
  const [menuOpen, setMenuOpen] = useState(false);
  const status =
    checkingId === recorder.id ? "checking" : effectiveStatus(recorder);
  const checking = checkingId === recorder.id;

  const handleCheck = async () => {
    onCheckStart(recorder.id);
    try {
      const res = await api.checkRecorder(recorder.id);
      onCheckEnd(res.recorder);
      if (res.check.status === "online") {
        push("success", `${displayRecorderName(recorder)}: доступен`);
      } else if (res.check.status !== "disabled") {
        push("error", res.check.error ?? "Недоступен");
      }
    } catch (e) {
      push("error", e instanceof Error ? e.message : "Ошибка проверки");
      onCheckEnd(recorder);
    }
  };

  return (
    <div className="flex flex-wrap items-center gap-3 border-t border-border/60 px-4 py-3 first:border-t-0 sm:px-6">
      <div className="min-w-0 flex-1">
        <div className="font-medium">{displayRecorderName(recorder)}</div>
        <div className="font-mono text-xs text-secondary">
          {formatHostPort(recorder.host, recorder.port, recorder.use_https)}
        </div>
      </div>
      <div className="flex items-center gap-3">
        <StatusBadge
          status={status}
          error={recorder.last_error}
        />
        <span className="hidden text-xs text-muted sm:inline">
          {formatTime(recorder.last_check_at)}
        </span>
        <Button
          variant="outline"
          loading={checking}
          disabled={!recorder.enabled || checking}
          onClick={handleCheck}
        >
          Проверить
        </Button>
        <div className="relative">
          <Button
            variant="ghost"
            aria-label="Действия"
            className="!min-h-10 !w-10 !p-0"
            onClick={() => setMenuOpen((v) => !v)}
          >
            <MoreHorizontal className="h-5 w-5" />
          </Button>
          {menuOpen && (
            <>
              <button
                type="button"
                className="fixed inset-0 z-10"
                aria-label="Закрыть меню"
                onClick={() => setMenuOpen(false)}
              />
              <div className="absolute right-0 top-full z-20 mt-1 min-w-[140px] rounded-lg border border-border bg-elevated py-1 shadow-lg">
                <button
                  type="button"
                  className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-surface"
                  onClick={() => {
                    setMenuOpen(false);
                    onEdit(recorder);
                  }}
                >
                  <Pencil className="h-4 w-4" /> Изменить
                </button>
                <button
                  type="button"
                  className="flex w-full items-center gap-2 px-3 py-2 text-sm text-status-error hover:bg-surface"
                  onClick={() => {
                    setMenuOpen(false);
                    onDelete(recorder);
                  }}
                >
                  <Trash2 className="h-4 w-4" /> Удалить
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
