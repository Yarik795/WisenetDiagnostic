import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  loadCollapsed,
  ObjectGroupCard,
  saveCollapsed,
} from "../components/ObjectGroupCard";
import { EmptyState } from "../components/EmptyState";
import { ErrorBanner } from "../components/ErrorBanner";
import { RecorderForm } from "../components/RecorderForm";
import { Header } from "../components/layout/Header";
import { Dialog } from "../components/ui/Dialog";
import { Drawer } from "../components/ui/Drawer";
import { GroupSkeleton } from "../components/ui/Skeleton";
import { useRecordersContext } from "../context/RecordersContext";
import { useToasts } from "../hooks/useToasts";
import { groupByObject, type SortMode } from "../lib/grouping";
import type { Recorder } from "../types";
import { displayRecorderName } from "../lib/utils";

export function ObjectsPage() {
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
  const [searchParams] = useSearchParams();
  const highlightObject = searchParams.get("object");

  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<SortMode>("status");
  const [collapsed, setCollapsed] = useState<Set<string>>(loadCollapsed);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<Recorder | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Recorder | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [checkingId, setCheckingId] = useState<string | null>(null);

  const objectNames = useMemo(
    () => [...new Set(recorders.map((r) => r.object_name))].sort(),
    [recorders]
  );

  const groups = useMemo(
    () => groupByObject(recorders, search, sort),
    [recorders, search, sort]
  );

  useEffect(() => {
    if (highlightObject) {
      setCollapsed((prev) => {
        const next = new Set(prev);
        next.delete(highlightObject);
        saveCollapsed(next);
        return next;
      });
    }
  }, [highlightObject]);

  const toggleCollapse = (name: string) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      saveCollapsed(next);
      return next;
    });
  };

  const openCreate = () => {
    setEditing(null);
    setDrawerOpen(true);
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
      <Header title="Объекты" onAdd={openCreate}>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            type="search"
            placeholder="Поиск объекта, NVR, IP…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-10 w-56 rounded-lg border border-border bg-elevated pl-9 pr-3 text-sm focus-visible:ring-2 focus-visible:ring-accent sm:w-72"
          />
        </div>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortMode)}
          className="h-10 rounded-lg border border-border bg-elevated px-3 text-sm"
          aria-label="Сортировка"
        >
          <option value="status">Проблемные сверху</option>
          <option value="name">По имени (А–Я)</option>
        </select>
      </Header>

      <main className="mx-auto max-w-content flex-1 overflow-y-auto px-4 py-6 sm:px-6">
        {error && <ErrorBanner message={error} onRetry={refresh} />}

        {loading && <GroupSkeleton />}

        {!loading && !error && recorders.length === 0 && (
          <EmptyState onAdd={openCreate} />
        )}

        {!loading && !error && recorders.length > 0 && (
          <div className="space-y-3">
            {groups.length === 0 && (
              <p className="text-center text-secondary">
                Ничего не найдено по запросу
              </p>
            )}
            {groups.map((g) => (
              <ObjectGroupCard
                key={g.objectName}
                group={g}
                expanded={!collapsed.has(g.objectName)}
                onToggle={() => toggleCollapse(g.objectName)}
                checkingId={checkingId}
                onCheckStart={setCheckingId}
                onCheckEnd={(r) => {
                  setCheckingId(null);
                  patchRecorder(r);
                }}
                onEdit={(r) => {
                  setEditing(r);
                  setDrawerOpen(true);
                }}
                onDelete={setDeleteTarget}
              />
            ))}
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
