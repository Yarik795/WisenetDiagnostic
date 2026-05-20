import { Button } from "./ui/Button";

interface ErrorBannerProps {
  message: string;
  onRetry: () => void;
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div
      role="alert"
      className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-status-error/40 bg-status-error/10 px-4 py-3 text-sm text-status-error"
    >
      <span>Не удалось загрузить данные: {message}</span>
      <Button variant="outline" onClick={onRetry}>
        Повторить
      </Button>
    </div>
  );
}
