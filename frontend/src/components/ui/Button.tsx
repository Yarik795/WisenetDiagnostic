import { cn } from "../../lib/utils";

type Variant = "primary" | "ghost" | "danger" | "outline";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  loading?: boolean;
}

const variants: Record<Variant, string> = {
  primary:
    "bg-accent text-white hover:bg-accent-hover focus-visible:ring-2 focus-visible:ring-accent",
  ghost:
    "bg-transparent text-secondary hover:text-primary hover:bg-elevated",
  danger:
    "bg-status-error/15 text-status-error hover:bg-status-error/25",
  outline:
    "border border-border bg-transparent text-primary hover:bg-elevated",
};

export function Button({
  className,
  variant = "primary",
  loading,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex min-h-10 items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors duration-150 focus-visible:outline-none disabled:opacity-50",
        variants[variant],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <span
          className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
          aria-hidden
        />
      )}
      {children}
    </button>
  );
}
