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
    attachment_html: str,
    attachment_filename: str,
) -> None:
    if not settings.to_emails:
        raise ValueError("email_report.to_emails is empty")
    if not settings.from_email:
        raise ValueError("email_report.from_email is empty")

    msg = MIMEMultipart("mixed")
    msg["Subject"] = settings.subject
    msg["From"] = settings.from_email
    msg["To"] = ", ".join(settings.to_emails)

    msg.attach(MIMEText(body_html, "html", "utf-8"))

    attachment = MIMEApplication(
        attachment_html.encode("utf-8"),
        _subtype="html",
        Name=attachment_filename,
    )
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=attachment_filename,
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
