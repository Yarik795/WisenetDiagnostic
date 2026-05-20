import type {
  Credentials,
  Recorder,
  RecorderCheckResponse,
  RecorderCreate,
} from "../types";

const BASE = "/api";

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body.detail) {
        detail =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
      }
    } catch {
      /* ignore */
    }
    throw new Error(detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  listRecorders: () => request<Recorder[]>("/recorders"),
  createRecorder: (data: RecorderCreate) =>
    request<Recorder>("/recorders", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateRecorder: (id: string, data: RecorderCreate) =>
    request<Recorder>(`/recorders/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteRecorder: (id: string) =>
    request<void>(`/recorders/${id}`, { method: "DELETE" }),
  checkRecorder: (id: string) =>
    request<RecorderCheckResponse>(`/recorders/${id}/check`, {
      method: "POST",
    }),
  getSettings: () => request<Credentials>("/settings"),
  updateSettings: (data: Credentials) =>
    request<Credentials>("/settings", {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};
