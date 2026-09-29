"""Student notifications, behind a small interface (section 9 of the
brief): a console/log fallback for dev, and SMTP -- configurable via env
vars -- for real sending. The allocator only ever talks to the Notifier
interface, so swapping which one is active never touches workflow code.
"""

import os
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage

from app.models import ProjectRequest


class Notifier(ABC):
    @abstractmethod
    def notify_ready(self, request: ProjectRequest) -> None:
        """All requested items were reserved; ready for pickup."""

    @abstractmethod
    def notify_pending(self, request: ProjectRequest) -> None:
        """Some requested item(s) are out of stock; request is queued."""


class ConsoleNotifier(Notifier):
    """Default dev/demo notifier: logs what would have been emailed."""

    def notify_ready(self, request: ProjectRequest) -> None:
        print(
            f"[NOTIFY] To: {request.student_email or request.student_name} | "
            f"Project {request.project_id} ({request.project_name}) is READY "
            f"for pickup on {request.pick_up_date}."
        )

    def notify_pending(self, request: ProjectRequest) -> None:
        print(
            f"[NOTIFY] To: {request.student_email or request.student_name} | "
            f"Project {request.project_id} ({request.project_name}) is PENDING: "
            f"{request.pending_reason}"
        )


class SMTPNotifier(Notifier):
    """Real email sending via smtplib. Configure with RAI_SMTP_* env vars
    (see notifier_from_env below); falls back to ConsoleNotifier if the
    host isn't set, so a dev machine never needs a mail server."""

    def __init__(
        self,
        host: str,
        port: int = 587,
        username: str = "",
        password: str = "",
        from_addr: str = "",
        use_tls: bool = True,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_addr = from_addr or username or "no-reply@rai.kmitl"
        self.use_tls = use_tls

    def _send(self, to_addr: str, subject: str, body: str) -> None:
        if not to_addr:
            return
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = to_addr
        msg.set_content(body)
        with smtplib.SMTP(self.host, self.port, timeout=10) as server:
            if self.use_tls:
                server.starttls()
            if self.username:
                server.login(self.username, self.password)
            server.send_message(msg)

    def notify_ready(self, request: ProjectRequest) -> None:
        self._send(
            request.student_email,
            f"[RAI Item Allocator] {request.project_id} is ready for pickup",
            f"Hi {request.student_name},\n\n"
            f"Your project '{request.project_name}' ({request.project_id}) has been "
            f"reserved and is ready for pickup on {request.pick_up_date}.\n\n"
            f"-- RAI Student Project Item Allocator",
        )

    def notify_pending(self, request: ProjectRequest) -> None:
        self._send(
            request.student_email,
            f"[RAI Item Allocator] {request.project_id} is pending stock",
            f"Hi {request.student_name},\n\n"
            f"Your project '{request.project_name}' ({request.project_id}) is queued "
            f"pending stock: {request.pending_reason}\n\n"
            f"-- RAI Student Project Item Allocator",
        )


def notifier_from_env() -> Notifier:
    """RAI_SMTP_HOST unset (the dev default) -> console/log fallback.
    Set it (plus optionally RAI_SMTP_PORT/USERNAME/PASSWORD/FROM/
    RAI_SMTP_USE_TLS=false) to send real email instead."""
    host = os.environ.get("RAI_SMTP_HOST", "").strip()
    if not host:
        return ConsoleNotifier()
    return SMTPNotifier(
        host=host,
        port=int(os.environ.get("RAI_SMTP_PORT", "587")),
        username=os.environ.get("RAI_SMTP_USERNAME", ""),
        password=os.environ.get("RAI_SMTP_PASSWORD", ""),
        from_addr=os.environ.get("RAI_SMTP_FROM", ""),
        use_tls=os.environ.get("RAI_SMTP_USE_TLS", "true").strip().lower() != "false",
    )
