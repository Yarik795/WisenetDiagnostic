from __future__ import annotations

import smtplib
import ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .models import EmailReportSettings


def send_report_email(
    settings: EmailReportSettings,
    *,
    body_html: str,
    attachment_html: str | None = None,
    attachment_filename: str | None = None,
    attachments: list[tuple[str, str]] | None = None,
    subject: str | None = None,
) -> None:
    if not settings.to_emails:
        raise ValueError("email_report.to_emails is empty")
    if not settings.from_email:
        raise ValueError("email_report.from_email is empty")

    attachment_items: list[tuple[str, str]] = []
    if attachments:
        attachment_items = list(attachments)
    elif attachment_html is not None and attachment_filename is not None:
        attachment_items = [(attachment_filename, attachment_html)]

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject if subject is not None else settings.subject
    msg["From"] = settings.from_email
    msg["To"] = ", ".join(settings.to_emails)

    msg.attach(MIMEText(body_html, "html", "utf-8"))

    for filename, html_content in attachment_items:
        attachment = MIMEApplication(
            html_content.encode("utf-8"),
            _subtype="html",
            Name=filename,
        )
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=filename,
        )
        msg.attach(attachment)

    if settings.use_starttls:
        context = ssl.SSLContext(getattr(ssl, "PROTOCOL_TLSv1_2", ssl.PROTOCOL_TLS_CLIENT))
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=120) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(
                settings.from_email,
                settings.to_emails,
                msg.as_string(),
            )
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=120) as server:
            server.ehlo()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(
                settings.from_email,
                settings.to_emails,
                msg.as_string(),
            )
