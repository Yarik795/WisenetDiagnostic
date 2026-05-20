import { Building2, HardDrive, Settings } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "../../lib/utils";

const nav = [
  { to: "/objects", label: "Объекты", icon: Building2 },
  { to: "/recorders", label: "Регистраторы", icon: HardDrive },
  { to: "/settings", label: "Настройки", icon: Settings },
];

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r border-border bg-[#0a0d12]">
      <div className="border-b border-border px-5 py-5">
        <div className="text-xs font-medium uppercase tracking-wider text-muted">
          Wisenet
        </div>
        <div className="mt-1 text-base font-semibold">Диагностика</div>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                "flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm transition-colors duration-150",
                isActive
                  ? "bg-elevated text-primary"
                  : "text-secondary hover:bg-elevated hover:text-primary"
              )
            }
          >
            <Icon className="h-5 w-5 shrink-0" aria-hidden />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
