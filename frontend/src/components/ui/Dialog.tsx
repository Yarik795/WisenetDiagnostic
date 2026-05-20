import { Button } from "./Button";

interface DialogProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}

export function Dialog({
  open,
  title,
  message,
  confirmLabel = "Удалить",
  cancelLabel = "Отмена",
  onConfirm,
  onCancel,
  loading,
}: DialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <button
        type="button"
        className="absolute inset-0 bg-black/50"
        aria-label="Закрыть"
        onClick={onCancel}
      />
      <div
        role="alertdialog"
        aria-labelledby="dialog-title"
        className="relative w-full max-w-md rounded-lg border border-border bg-elevated p-6 shadow-xl"
      >
        <h3 id="dialog-title" className="text-lg font-semibold">
          {title}
        </h3>
        <p className="mt-2 text-sm text-secondary">{message}</p>
        <div className="mt-6 flex justify-end gap-3">
          <Button variant="ghost" onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={loading}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
