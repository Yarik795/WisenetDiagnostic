import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function displayRecorderName(recorder: {
  name: string | null;
  host: string;
}): string {
  return recorder.name?.trim() || recorder.host;
}

export function formatHostPort(
  host: string,
  port: number,
  useHttps: boolean
): string {
  const scheme = useHttps ? "https" : "http";
  const defaultPort = useHttps ? 443 : 80;
  if (port === defaultPort) return `${scheme}://${host}`;
  return `${scheme}://${host}:${port}`;
}

export function formatTime(iso: string | null): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleTimeString("ru-RU", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return "—";
  }
}
