import { useToasts } from "../../hooks/useToasts";
import { cn } from "../../lib/utils";

export function ToastContainer() {
  const { toasts, dismiss } = useToasts();

  if (toasts.length === 0) return null;

  return (
    <div
      className="fixed bottom-4 right-4 z-[70] flex flex-col gap-2"
      aria-live="polite"
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          className={cn(
            "min-w-[280px] rounded-lg border px-4 py-3 text-sm shadow-lg",
            t.type === "success" &&
              "border-status-ok/40 bg-status-ok/10 text-status-ok",
            t.type === "error" &&
              "border-status-error/40 bg-status-error/10 text-status-error",
            t.type === "info" &&
              "border-accent/40 bg-accent/10 text-primary"
          )}
        >
          <div className="flex items-start justify-between gap-2">
            <span>{t.message}</span>
            <button
              type="button"
              className="text-muted hover:text-primary"
              aria-label="Закрыть"
              onClick={() => dismiss(t.id)}
            >
              ×
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
