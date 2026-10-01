"""Student email notifications for the RAI Item Allocator.

If SMTP settings are present in the repository-root .env file, the app sends
real email. Otherwise it falls back to console notifications for development.
"""

import os
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

from backend.models import ProjectRequest

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)


class Notifier(ABC):
    @abstractmethod
    def notify_ready(self, request: ProjectRequest) -> None:
        """Notify the student that the request is reserved and ready."""

    @abstractmethod
    def notify_pending(self, request: ProjectRequest) -> None:
        """Notify the student that the request is pending because of stock."""


class ConsoleNotifier(Notifier):
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

        with smtplib.SMTP(self.host, self.port, timeout=15) as server:
            server.ehlo()
            if self.use_tls:
                server.starttls()
                server.ehlo()
            if self.username:
                server.login(self.username, self.password)
            server.send_message(msg)

    @staticmethod
    def _format_items(request: ProjectRequest) -> str:
        if not request.items:
            return "- No item details available"

        return "\n".join(
            f"- {line.quantity} x {line.item_name} ({line.type})"
            for line in request.items
        )

    @staticmethod
    def _format_pickup_date(request: ProjectRequest) -> str:
        return request.pick_up_date.strftime("%d %B %Y")

    def notify_ready(self, request: ProjectRequest) -> None:
        items = self._format_items(request)
        pickup_date = self._format_pickup_date(request)

        subject = (
            f"[RAI Item Allocator] {request.project_id} - Items Ready for Pickup"
        )

        body = (
            f"Hi {request.student_name},\n\n"
            "Good news! Your project item request has been approved, and the "
            "requested items are now reserved for you.\n\n"
            "PROJECT DETAILS\n"
            f"Project ID: {request.project_id}\n"
            f"Project Name: {request.project_name}\n"
            f"Student ID: {request.student_id or '-'}\n"
            f"Group: {request.group or '-'}\n"
            f"Pickup Date: {pickup_date}\n\n"
            "RESERVED ITEMS\n"
            f"{items}\n\n"
            "STATUS: READY FOR PICKUP\n\n"
            "Please keep your Project ID for reference when collecting the items. "
            "If your pickup plan changes, please contact the RAI administrator.\n\n"
            "Thank you,\n"
            "RAI Student Project Item Allocator\n"
            "KMITL Robotics and AI Engineering\n\n"
            "This is an automated notification."
        )

        self._send(request.student_email, subject, body)

    def notify_pending(self, request: ProjectRequest) -> None:
        items = self._format_items(request)
        pickup_date = self._format_pickup_date(request)

        subject = (
            f"[RAI Item Allocator] {request.project_id} - Request Pending"
        )

        body = (
            f"Hi {request.student_name},\n\n"
            "We received your project item request, but it cannot be fully reserved "
            "yet because one or more requested items do not currently have enough "
            "available stock.\n\n"
            "PROJECT DETAILS\n"
            f"Project ID: {request.project_id}\n"
            f"Project Name: {request.project_name}\n"
            f"Student ID: {request.student_id or '-'}\n"
            f"Group: {request.group or '-'}\n"
            f"Requested Pickup Date: {pickup_date}\n\n"
            "REQUESTED ITEMS\n"
            f"{items}\n\n"
            "PENDING REASON\n"
            f"{request.pending_reason or 'Waiting for inventory availability'}\n\n"
            "STATUS: PENDING\n\n"
            "Your request will remain in the Pending Queue and will be checked again "
            "when inventory changes. You do not need to submit the same request again. "
            "You will receive another notification when the request is approved and "
            "the items are reserved.\n\n"
            "Thank you,\n"
            "RAI Student Project Item Allocator\n"
            "KMITL Robotics and AI Engineering\n\n"
            "This is an automated notification."
        )

        self._send(request.student_email, subject, body)


def notifier_from_env() -> Notifier:
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

