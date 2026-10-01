"""Send one real test email using the SMTP settings in .env."""

import os
from datetime import date, datetime

from backend.models import ProjectRequest
from backend.notifications import SMTPNotifier, notifier_from_env


def main():
    recipient = os.environ.get("RAI_TEST_EMAIL", "").strip()
    if not recipient:
        raise SystemExit("Set RAI_TEST_EMAIL in .env before running this test.")

    notifier = notifier_from_env()
    if not isinstance(notifier, SMTPNotifier):
        raise SystemExit("SMTP is not configured. Copy .env.example to .env and fill in the SMTP values.")

    request = ProjectRequest(
        project_id="PTEST",
        project_name="Email Notification Test",
        student_name="Test Student",
        group="TEST",
        pick_up_date=date.today(),
        submitted_at=datetime.now(),
        student_email=recipient,
    )

    notifier.notify_ready(request)
    print(f"Test email sent to {recipient}")


if __name__ == "__main__":
    main()
