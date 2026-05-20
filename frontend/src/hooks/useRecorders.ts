import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import type { Recorder, RecorderCreate } from "../types";

export function useRecorders() {
  const [recorders, setRecorders] = useState<Recorder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listRecorders();
      setRecorders(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const create = async (data: RecorderCreate) => {
    const created = await api.createRecorder(data);
    setRecorders((prev) => [...prev, created]);
    return created;
  };

  const update = async (id: string, data: RecorderCreate) => {
    const updated = await api.updateRecorder(id, data);
    setRecorders((prev) => prev.map((r) => (r.id === id ? updated : r)));
    return updated;
  };

  const remove = async (id: string) => {
    await api.deleteRecorder(id);
    setRecorders((prev) => prev.filter((r) => r.id !== id));
  };

  const patchRecorder = (recorder: Recorder) => {
    setRecorders((prev) =>
      prev.map((r) => (r.id === recorder.id ? recorder : r))
    );
  };

  return {
    recorders,
    loading,
    error,
    refresh,
    create,
    update,
    remove,
    patchRecorder,
    setRecorders,
  };
}
