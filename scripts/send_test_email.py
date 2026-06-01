#!/usr/bin/env python3
"""Тестовая отправка письма по секции email_report из config.json."""

from __future__ import annotations

import argparse
import smtplib
import ssl
import sys
import traceback
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.config_store import ConfigStore  # noqa: E402
from app.models import EmailReportSettings  # noqa: E402


def _mask_secret(value: str) -> str:
    if not value:
        return "(пусто)"
    if len(value) <= 2:
        return "**"
    return f"{value[0]}{'*' * (len(value) - 2)}{value[-1]}"


def _print_settings(cfg: EmailReportSettings) -> None:
    print("--- email_report ---")
    print(f"  enabled:           {cfg.enabled}")
    print(f"  smtp_host:         {cfg.smtp_host}")
    print(f"  smtp_port:         {cfg.smtp_port}")
    print(f"  use_starttls:      {cfg.use_starttls}")
    print(f"  smtp_user:         {cfg.smtp_user or '(пусто)'}")
    print(f"  smtp_password:     {_mask_secret(cfg.smtp_password)}")
    print(f"  from_email:        {cfg.from_email}")
    print(f"  to_emails:         {', '.join(cfg.to_emails) or '(пусто)'}")
    print(f"  subject (боевой):  {cfg.subject}")
    print()


def _validate(cfg: EmailReportSettings) -> list[str]:
    errors: list[str] = []
    if not cfg.from_email:
        errors.append("from_email не задан")
    if not cfg.to_emails:
        errors.append("to_emails пустой")
    if not cfg.smtp_host:
        errors.append("smtp_host не задан")
    return errors


def send_test_email(cfg: EmailReportSettings) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    subject = "[TEST] Wisenet Диагностика — тестовое письмо"
    body = (
        "Это тестовое письмо от scripts/send_test_email.py.\n\n"
        f"Время отправки: {now}\n"
        f"SMTP: {cfg.smtp_host}:{cfg.smtp_port}\n"
        "Если вы видите это сообщение, отправка из конфигурации работает.\n"
    )

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = cfg.from_email
    msg["To"] = ", ".join(cfg.to_emails)

    print("--- письмо ---")
    print(f"  Subject: {subject}")
    print(f"  From:    {cfg.from_email}")
    print(f"  To:      {', '.join(cfg.to_emails)}")
    print()

    print(f"Подключение к {cfg.smtp_host}:{cfg.smtp_port} ...")
    with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=120) as server:
        print("  OK: TCP-соединение установлено")

        code, resp = server.ehlo()
        print(f"  EHLO: {code} {resp!r}")

        if cfg.use_starttls:
            print("  STARTTLS ...")
            context = ssl.SSLContext(
                getattr(ssl, "PROTOCOL_TLSv1_2", ssl.PROTOCOL_TLS_CLIENT)
            )
            server.starttls(context=context)
            print("  OK: STARTTLS")

            code, resp = server.ehlo()
            print(f"  EHLO после TLS: {code} {resp!r}")

        if cfg.smtp_user:
            print(f"  LOGIN как {cfg.smtp_user!r} ...")
            server.login(cfg.smtp_user, cfg.smtp_password)
            print("  OK: LOGIN")
        else:
            print("  LOGIN пропущен (smtp_user пустой)")

        print("  sendmail ...")
        server.sendmail(cfg.from_email, cfg.to_emails, msg.as_string())
        print("  OK: sendmail завершён")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Отправить тестовое письмо по email_report из config.json",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config.json",
        help="Путь к config.json (по умолчанию: config.json в корне проекта)",
    )
    args = parser.parse_args()

    print("=== Wisenet: тест отправки почты ===\n")
    print(f"Файл конфигурации: {args.config.resolve()}")

    if not args.config.is_file():
        print(f"ОШИБКА: файл не найден: {args.config}")
        return 1

    try:
        app_config = ConfigStore(args.config).load()
    except Exception:
        print("ОШИБКА: не удалось прочитать config.json:")
        traceback.print_exc()
        return 1

    cfg = app_config.email_report
    _print_settings(cfg)

    if not cfg.enabled:
        print(
            "Предупреждение: email_report.enabled = false "
            "(для теста скрипт всё равно отправит письмо).\n"
        )

    errors = _validate(cfg)
    if errors:
        print("ОШИБКА: проверьте настройки:")
        for err in errors:
            print(f"  - {err}")
        return 1

    try:
        send_test_email(cfg)
    except Exception:
        print("\nОШИБКА при отправке:")
        traceback.print_exc()
        return 1

    print("\nГотово: тестовое письмо отправлено.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
