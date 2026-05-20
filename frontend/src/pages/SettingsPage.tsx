import { AlertTriangle } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { Header } from "../components/layout/Header";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { useToasts } from "../hooks/useToasts";

export function SettingsPage() {
  const { push } = useToasts();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api
      .getSettings()
      .then((c) => {
        setUsername(c.username);
        setPassword(c.password);
      })
      .catch((e) =>
        push("error", e instanceof Error ? e.message : "Ошибка загрузки")
      )
      .finally(() => setLoading(false));
  }, [push]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      push("error", "Укажите логин и пароль");
      return;
    }
    setSaving(true);
    try {
      await api.updateSettings({ username: username.trim(), password });
      push("success", "Учётные данные сохранены");
    } catch (err) {
      push(
        "error",
        err instanceof Error ? err.message : "Ошибка сохранения"
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Header title="Настройки" />
      <main className="mx-auto max-w-content flex-1 px-4 py-6 sm:px-6">
        <div className="max-w-lg rounded-lg border border-border bg-surface p-6">
          <div className="mb-6 flex gap-3 rounded-lg border border-status-warn/30 bg-status-warn/10 p-4 text-sm text-status-warn">
            <AlertTriangle className="h-5 w-5 shrink-0" aria-hidden />
            <p>
              Пароль хранится в локальном <code className="font-mono">config.json</code> на
              сервере. Не добавляйте реальные пароли в публичный репозиторий.
            </p>
          </div>

          {loading ? (
            <p className="text-secondary">Загрузка…</p>
          ) : (
            <form onSubmit={handleSave} className="space-y-4">
              <Input
                label="Логин SUNAPI"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
              />
              <Input
                label="Пароль"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <Button type="submit" loading={saving}>
                Сохранить
              </Button>
            </form>
          )}
        </div>
      </main>
    </>
  );
}
