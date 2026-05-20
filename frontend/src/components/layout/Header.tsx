import { Plus } from "lucide-react";
import { Button } from "../ui/Button";

interface HeaderProps {
  title: string;
  onAdd?: () => void;
  children?: React.ReactNode;
}

export function Header({ title, onAdd, children }: HeaderProps) {
  return (
    <header className="flex shrink-0 flex-wrap items-center justify-between gap-4 border-b border-border bg-surface px-6 py-4">
      <h1 className="text-2xl font-semibold">{title}</h1>
      <div className="flex flex-wrap items-center gap-3">
        {children}
        {onAdd && (
          <Button onClick={onAdd}>
            <Plus className="h-4 w-4" aria-hidden />
            Добавить регистратор
          </Button>
        )}
      </div>
    </header>
  );
}
