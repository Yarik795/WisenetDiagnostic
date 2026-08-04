# Запуск Wisenet Диагностика на Linux

Инструкция для сервера или рабочей станции Linux **без виртуального окружения**: зависимости устанавливаются в системный Python.

Пример корня проекта: `/opt/wisenet-diagnostics` — далее **корень проекта**. Команды запуска выполняются из каталога **`backend/`**.

---

## Требования

| Компонент | Версия / примечание |
|-----------|---------------------|
| Python | 3.11 или новее |
| pip | для установки зависимостей |
| ICMP ping | пакет `iputils-ping` (Debian/Ubuntu) или аналог |

Проверка:

```bash
python3 --version
pip3 --version
ping -c 1 127.0.0.1
```

Node.js **не нужен** — интерфейс отдаёт сервер (Jinja2 + HTMX).

---

## 1. Размещение проекта

Скопируйте репозиторий на сервер, например:

```bash
sudo mkdir -p /opt/wisenet-diagnostics
sudo chown "$USER:$USER" /opt/wisenet-diagnostics
git clone https://github.com/Yarik795/WisenetDiagnostic.git /opt/wisenet-diagnostics
cd /opt/wisenet-diagnostics
```

Или распакуйте архив в нужный каталог.

Создайте каталоги для runtime-данных (если их ещё нет):

```bash
mkdir -p data logs inputData
```

---

## 2. Установка зависимостей

Из каталога `backend` установите пакеты в **системный** Python:

```bash
cd /opt/wisenet-diagnostics/backend
pip3 install -r requirements.txt
```

Если `pip3 install` без прав root запрещён, используйте установку в домашний каталог пользователя сервиса:

```bash
pip3 install --user -r requirements.txt
export PATH="$HOME/.local/bin:$PATH"
```

Проверка:

```bash
python3 -m uvicorn --version
```

---

## 3. Конфигурация

```bash
cd /opt/wisenet-diagnostics
cp config.example.json config.json
chmod 600 config.json
```

Отредактируйте `config.json`:

- `credentials.username` / `credentials.password` — учётная запись SUNAPI для NVR;
- `recorders` — список регистраторов (можно добавить позже через UI);
- при необходимости — `email_report`, `monitoring`.

> `config.json` не коммитится в git (содержит пароли). На каждом сервере создайте свой файл или скопируйте вручную.

### Переменные окружения (опционально)

| Переменная | Назначение | По умолчанию |
|------------|------------|--------------|
| `CONFIG_PATH` | Путь к `config.json` | `../config.json` от `backend/` |
| `STATE_DB_PATH` | Путь к SQLite | `../data/monitoring.db` |
| `WISENET_LOG_DIR` | Каталог логов | `../logs/` |

Пример для текущей сессии:

```bash
export CONFIG_PATH=/opt/wisenet-diagnostics/config.json
export STATE_DB_PATH=/opt/wisenet-diagnostics/data/monitoring.db
export WISENET_LOG_DIR=/opt/wisenet-diagnostics/logs
```

---

## 4. Запуск вручную

```bash
cd /opt/wisenet-diagnostics/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Для локальной отладки с автоперезагрузкой:

```bash
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Признаки успешного старта

В терминале появится строка вида:

```text
Wisenet: логи -> /opt/wisenet-diagnostics/logs/wisenet.log
```

Проверка:

- [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) — `{"status":"ok","log_file":"..."}`
- [http://127.0.0.1:8000/objects](http://127.0.0.1:8000/objects) — веб-интерфейс

---

## 5. Запуск как systemd-сервис

Создайте пользователя и unit-файл (пути подставьте свои):

```bash
sudo useradd --system --home /opt/wisenet-diagnostics --shell /usr/sbin/nologin wisenet || true
sudo chown -R wisenet:wisenet /opt/wisenet-diagnostics
```

Файл `/etc/systemd/system/wisenet.service`:

```ini
[Unit]
Description=Wisenet Diagnostic
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=wisenet
Group=wisenet
WorkingDirectory=/opt/wisenet-diagnostics/backend
Environment=CONFIG_PATH=/opt/wisenet-diagnostics/config.json
Environment=STATE_DB_PATH=/opt/wisenet-diagnostics/data/monitoring.db
Environment=WISENET_LOG_DIR=/opt/wisenet-diagnostics/logs
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Если использовали `pip3 install --user`, укажите полный путь к Python пользователя `wisenet` и добавьте `Environment=PATH=/home/wisenet/.local/bin:...`.

Запуск:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wisenet
sudo systemctl start wisenet
sudo systemctl status wisenet
journalctl -u wisenet -f
```

---

## 6. ICMP ping (СКУД, биотерминалы)

Модуль `ping_check.py` вызывает системную утилиту `ping`. На Linux непривилегированный пользователь может не иметь прав на ICMP.

Варианты:

1. **Capabilities для ping** (предпочтительно):

```bash
sudo apt install iputils-ping   # Debian/Ubuntu
sudo setcap cap_net_raw+ep "$(command -v ping)"
getcap "$(command -v ping)"
```

2. Запуск сервиса от root (не рекомендуется для постоянной эксплуатации).

Без прав на ping устройства СКУД/биотерминалов будут помечаться недоступными; опрос NVR по SUNAPI при этом работает.

---

## 7. Первый вход в UI

1. Откройте **Настройки** (`/settings`) и сохраните логин/пароль SUNAPI.
2. На **Объектах** (`/objects`) добавьте регистратор или обновите список из CMDB.
3. Включите **Автообновление** в шапке, если нужен фоновый опрос по расписанию.

По умолчанию планировщик **не опрашивает** устройства, пока не включено автообновление. Ручной **Опросить все NVR** доступен и при паузе.

---

## 8. Тесты

```bash
cd /opt/wisenet-diagnostics/backend
python3 -m pytest
```

---

## 9. Логи

Файл `wisenet.log` создаётся в каталоге из `WISENET_LOG_DIR` или в `logs/` корня проекта.

```bash
tail -f /opt/wisenet-diagnostics/logs/wisenet.log
grep '"event":"sunapi_check_done"' /opt/wisenet-diagnostics/logs/wisenet.log | tail
```

Формат: одна строка = один JSON-объект. Пароли в лог не попадают.

---

## 10. Частые проблемы

| Симптом | Что проверить |
|---------|----------------|
| `ModuleNotFoundError: No module named 'fastapi'` | Выполните `pip3 install -r requirements.txt` из `backend/` |
| `uvicorn: command not found` | Запускайте через `python3 -m uvicorn ...` |
| Страница не открывается | `ss -tlnp \| grep 8000`, firewall (`ufw`, `firewalld`) |
| NVR — таймаут | Маршрутизация и доступ к подсети устройств с сервера |
| Ping СКУД всегда недоступен | Права на ICMP (см. раздел 6) |
| Нет записи в `logs/` | Права на каталог, задайте `WISENET_LOG_DIR` |
| Permission denied на `config.json` | `chmod 600`, владелец = пользователь сервиса |

---

## Связанные документы

- [README.md](../README.md) — обзор проекта
- [business-logic.md](./business-logic.md) — поведение планировщика и автоопроса
