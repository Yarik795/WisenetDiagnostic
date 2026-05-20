import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Button } from "../ui/Button";
import { ToastContainer } from "../ui/ToastContainer";

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-base">
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {mobileOpen && (
        <div className="fixed inset-0 z-40 flex lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/50"
            aria-label="Закрыть меню"
            onClick={() => setMobileOpen(false)}
          />
          <div className="relative z-10 h-full">
            <Sidebar onNavigate={() => setMobileOpen(false)} />
          </div>
        </div>
      )}

      <div className="flex min-h-screen flex-1 flex-col">
        <div className="flex items-center gap-2 border-b border-border bg-surface px-4 py-3 lg:hidden">
          <Button
            variant="ghost"
            aria-label={mobileOpen ? "Закрыть меню" : "Открыть меню"}
            onClick={() => setMobileOpen((v) => !v)}
            className="!min-h-10 !w-10 !p-0"
          >
            {mobileOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </Button>
          <span className="font-semibold">Wisenet Диагностика</span>
        </div>
        <Outlet />
      </div>
      <ToastContainer />
    </div>
  );
}
