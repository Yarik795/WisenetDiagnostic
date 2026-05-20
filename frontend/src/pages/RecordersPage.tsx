import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { EmptyState } from "../components/EmptyState";
import { ErrorBanner } from "../components/ErrorBanner";
import { RecorderForm } from "../components/RecorderForm";
import { Header } from "../components/layout/Header";
import { Dialog } from "../components/ui/Dialog";
import { Drawer } from "../components/ui/Drawer";
import { GroupSkeleton } from "../components/ui/Skeleton";
import { StatusBadge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { useRecordersContext } from "../context/RecordersContext";
import { useToasts } from "../hooks/useToasts";
import { api } from "../api/client";
import { effectiveStatus } from "../lib/status";
import type { Recorder } from "../types";
import {
  displayRecorderName,
  formatHostPort,
  formatTime,
} from "../lib/utils";

export function RecordersPage() {
  const {
    recorders,
    loading,
    error,
    refresh,
    create,
    update,
    remove,
    patchRecorder,
  } = useRecordersContext();
  const { push } = useToasts();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<Recorder | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Recorder | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [checkingId, setCheckingId] = useState<string | null>(null);

  const objectNames = useMemo(
    () => [...new Set(recorders.map((r) => r.object_name))].sort(),
    [recorders]
  );

  const sorted = useMemo(
    () =>
      [...recorders].sort((a, b) =>
        a.object_name.localeCompare(b.object_name, "ru")
      ),
    [recorders]
  );

  const openCreate = () => {
    setEditing(null);
    setDrawerOpen(true);
  };

  const handleCheck = async (r: Recorder) => {
    setCheckingId(r.id);
    try {
      const res = await api.checkRecorder(r.id);
      patchRecorder(res.recorder);
      if (res.check.status === "online") {
        push("success", `${displayRecorderName(r)}: доступен`);
      } else if (res.check.status !== "disabled") {
        push("error", res.check.error ?? "Недоступен");
      }
    } catch (e) {
      push("error", e instanceof Error ? e.message : "Ошибка проверки");
    } finally {
      setCheckingId(null);
    }
  };

  const handleSubmit = async (data: Parameters<typeof create>[0]) => {
    try {
      if (editing) {
        await update(editing.id, data);
        push("success", "Регистратор обновлён");
      } else {
        await create(data);
        push("success", "Регистратор добавлен");
      }
      setDrawerOpen(false);
      setEditing(null);
    } catch (e) {
      push("error", e instanceof Error ? e.message : "Ошибка сохранения");
      throw e;
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await remove(deleteTarget.id);
      push("success", "Регистратор удалён");
      setDeleteTarget(null);
    } catch (e) {
      push("error", e instanceof Error ? e.message : "Ошибка удаления");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <>
      <Header title="Регистраторы" onAdd={openCreate} />

      <main className="mx-auto max-w-content flex-1 overflow-y-auto px-4 py-6 sm:px-6">
        {error && <ErrorBanner message={error} onRetry={refresh} />}
        {loading && <GroupSkeleton />}

        {!loading && !error && recorders.length === 0 && (
          <EmptyState onAdd={openCreate} />
        )}

        {!loading && !error && recorders.length > 0 && (
          <div className="overflow-x-auto rounded-lg border border-border bg-surface">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="sticky top-0 bg-elevated text-secondary">
                <tr>
                  <th className="px-4 py-3 font-medium">Объект</th>
                  <th className="px-4 py-3 font-medium">Имя NVR</th>
                  <th className="px-4 py-3 font-medium">Host</th>
                  <th className="px-4 py-3 font-medium">Статус</th>
                  <th className="px-4 py-3 font-medium">Проверка</th>
                  <th className="px-4 py-3 font-medium">Действия</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((r) => {
                  const status =
                    checkingId === r.id ? "checking" : effectiveStatus(r);
                  return (
                    <tr
                      key={r.id}
                      className="border-t border-border/60 hover:bg-elevated/30"
                    >
                      <td className="px-4 py-3">
                        <Link
                          to={`/objects?object=${encodeURIComponent(r.object_name)}`}
                          className="text-accent hover:underline"
                        >
                          {r.object_name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 font-medium">
                        {displayRecorderName(r)}
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-secondary">
                        {formatHostPort(r.host, r.port, r.use_https)}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge
                          status={status}
                          error={r.last_error}
                        />
                      </td>
                      <td className="px-4 py-3 text-muted">
                        {formatTime(r.last_check_at)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            loading={checkingId === r.id}
                            disabled={!r.enabled}
                            onClick={() => handleCheck(r)}
                          >
                            Проверить
                          </Button>
                          <Button
                            variant="ghost"
                            onClick={() => {
                              setEditing(r);
                              setDrawerOpen(true);
                            }}
                          >
                            Изменить
                          </Button>
                          <Button
                            variant="ghost"
                            onClick={() => setDeleteTarget(r)}
                          >
                            Удалить
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </main>

      <Drawer
        open={drawerOpen}
        title={editing ? "Редактирование регистратора" : "Добавить регистратор"}
        onClose={() => {
          setDrawerOpen(false);
          setEditing(null);
        }}
      >
        <RecorderForm
          recorder={editing}
          objectNames={objectNames}
          onSubmit={handleSubmit}
          onCancel={() => {
            setDrawerOpen(false);
            setEditing(null);
          }}
        />
      </Drawer>

      <Dialog
        open={!!deleteTarget}
        title="Удалить регистратор?"
        message={
          deleteTarget
            ? `Удалить регистратор ${displayRecorderName(deleteTarget)} на объекте ${deleteTarget.object_name}?`
            : ""
        }
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        loading={deleting}
      />
    </>
  );
}
