import { useEffect, useState } from "react";
import type { Recorder, RecorderCreate } from "../types";
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";

interface RecorderFormProps {
  recorder?: Recorder | null;
  objectNames: string[];
  onSubmit: (data: RecorderCreate) => Promise<void>;
  onCancel: () => void;
}

const HOST_RE =
  /^(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[01]?\d?\d)){3}|[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*)$/;

function validate(data: RecorderCreate): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!data.object_name.trim()) {
    errors.object_name = "Укажите название объекта";
  }
  if (!data.host.trim()) {
    errors.host = "Укажите IP или DNS";
  } else if (!HOST_RE.test(data.host.trim())) {
    errors.host = "Некорректный формат адреса";
  }
  if (data.port < 1 || data.port > 65535) {
    errors.port = "Порт должен быть от 1 до 65535";
  }
  return errors;
}

export function RecorderForm({
  recorder,
  objectNames,
  onSubmit,
  onCancel,
}: RecorderFormProps) {
  const [objectName, setObjectName] = useState(recorder?.object_name ?? "");
  const [name, setName] = useState(recorder?.name ?? "");
  const [host, setHost] = useState(recorder?.host ?? "");
  const [port, setPort] = useState(String(recorder?.port ?? 80));
  const [useHttps, setUseHttps] = useState(recorder?.use_https ?? false);
  const [enabled, setEnabled] = useState(recorder?.enabled ?? true);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (recorder) {
      setObjectName(recorder.object_name);
      setName(recorder.name ?? "");
      setHost(recorder.host);
      setPort(String(recorder.port));
      setUseHttps(recorder.use_https);
      setEnabled(recorder.enabled);
    }
  }, [recorder]);

  const buildPayload = (): RecorderCreate => ({
    object_name: objectName.trim(),
    name: name.trim() || null,
    host: host.trim(),
    port: parseInt(port, 10) || 80,
    use_https: useHttps,
    enabled,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = buildPayload();
    const v = validate(payload);
    setErrors(v);
    if (Object.keys(v).length > 0) return;
    setSaving(true);
    try {
      await onSubmit(payload);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-1.5">
        <label htmlFor="object_name" className="block text-sm text-secondary">
          Название объекта *
        </label>
        <input
          id="object_name"
          list="object-names"
          value={objectName}
          onChange={(e) => setObjectName(e.target.value)}
          placeholder="Отделение №12"
          className="w-full rounded-lg border border-border bg-elevated px-3 py-2 text-sm focus-visible:ring-2 focus-visible:ring-accent"
        />
        <datalist id="object-names">
          {objectNames.map((n) => (
            <option key={n} value={n} />
          ))}
        </datalist>
        {errors.object_name && (
          <p className="text-xs text-status-error">{errors.object_name}</p>
        )}
      </div>

      <Input
        label="Имя регистратора"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="NVR-1 (необязательно)"
      />

      <Input
        label="Host (IP/DNS) *"
        value={host}
        onChange={(e) => setHost(e.target.value)}
        placeholder="10.1.2.3"
        error={errors.host}
        className="font-mono"
      />

      <Input
        label="Порт *"
        type="number"
        min={1}
        max={65535}
        value={port}
        onChange={(e) => setPort(e.target.value)}
        error={errors.port}
      />

      <label className="flex cursor-pointer items-center gap-3">
        <input
          type="checkbox"
          checked={useHttps}
          onChange={(e) => setUseHttps(e.target.checked)}
          className="h-4 w-4 rounded border-border accent-accent"
        />
        <span className="text-sm">HTTPS</span>
      </label>

      <label className="flex cursor-pointer items-center gap-3">
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => setEnabled(e.target.checked)}
          className="h-4 w-4 rounded border-border accent-accent"
        />
        <span className="text-sm">Включён</span>
      </label>

      <div className="flex gap-3 pt-4">
        <Button type="submit" loading={saving}>
          Сохранить
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>
          Отмена
        </Button>
      </div>
    </form>
  );
}
