import { X } from "lucide-react";
import { cn } from "../../lib/utils";
import { Button } from "./Button";

interface DrawerProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}

export function Drawer({ open, title, onClose, children }: DrawerProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <button
        type="button"
        className="absolute inset-0 bg-black/50"
        aria-label="Закрыть"
        onClick={onClose}
      />
      <aside
        className={cn(
          "relative flex h-full w-full max-w-[480px] flex-col bg-surface shadow-xl",
          "animate-in slide-in-from-right duration-200"
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
      >
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h2 id="drawer-title" className="text-lg font-semibold">
            {title}
          </h2>
          <Button
            variant="ghost"
            aria-label="Закрыть"
            onClick={onClose}
            className="!min-h-10 !w-10 !p-0"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto px-6 py-4">{children}</div>
      </aside>
    </div>
  );
}
