import { HardDrive, Plus } from "lucide-react";
import { Button } from "./ui/Button";

interface EmptyStateProps {
  onAdd: () => void;
}

export function EmptyState({ onAdd }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <HardDrive className="h-12 w-12 text-muted" aria-hidden />
      <p className="mt-4 text-lg font-medium">Нет регистраторов</p>
      <p className="mt-1 max-w-sm text-sm text-secondary">
        Добавьте первый регистратор, указав название объекта и адрес NVR.
      </p>
      <Button className="mt-6" onClick={onAdd}>
        <Plus className="h-4 w-4" aria-hidden />
        Добавить регистратор
      </Button>
    </div>
  );
}
