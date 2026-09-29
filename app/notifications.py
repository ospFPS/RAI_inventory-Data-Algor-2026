"""Student notifications, behind a small interface (section 9 of the
brief): a console/log fallback for dev, with SMTP added later behind the
same interface so the allocator never has to change when real sending is
wired up.
"""

from abc import ABC, abstractmethod

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
