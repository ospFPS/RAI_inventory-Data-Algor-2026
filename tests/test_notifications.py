from datetime import date, datetime
from unittest.mock import MagicMock, patch

from app.models import ProjectRequest, RequestStatus
from app.notifications import ConsoleNotifier, SMTPNotifier, notifier_from_env


def make_request(**overrides):
    defaults = dict(
        project_id="P0001",
        project_name="Bot",
        student_name="Nan",
        group="ROW",
        pick_up_date=date(2026, 1, 5),
        submitted_at=datetime(2026, 1, 1, 12, 0, 0),
        student_email="nan@example.com",
        status=RequestStatus.RESERVED,
        pending_reason="",
    )
    defaults.update(overrides)
    return ProjectRequest(**defaults)


def test_console_notifier_prints_ready(capsys):
    ConsoleNotifier().notify_ready(make_request())
    out = capsys.readouterr().out
    assert "P0001" in out
    assert "READY" in out


def test_console_notifier_prints_pending(capsys):
    req = make_request(status=RequestStatus.PENDING, pending_reason="Relay 5V: need 2, have 0")
    ConsoleNotifier().notify_pending(req)
    out = capsys.readouterr().out
    assert "PENDING" in out
    assert "Relay 5V" in out


def test_notifier_from_env_defaults_to_console(monkeypatch):
    monkeypatch.delenv("RAI_SMTP_HOST", raising=False)
    notifier = notifier_from_env()
    assert isinstance(notifier, ConsoleNotifier)


def test_notifier_from_env_builds_smtp_notifier(monkeypatch):
    monkeypatch.setenv("RAI_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("RAI_SMTP_PORT", "2525")
    monkeypatch.setenv("RAI_SMTP_USERNAME", "user")
    monkeypatch.setenv("RAI_SMTP_PASSWORD", "pass")
    monkeypatch.setenv("RAI_SMTP_FROM", "rai@kmitl.ac.th")
    notifier = notifier_from_env()
    assert isinstance(notifier, SMTPNotifier)
    assert notifier.host == "smtp.example.com"
    assert notifier.port == 2525
    assert notifier.from_addr == "rai@kmitl.ac.th"


def test_smtp_notifier_sends_via_smtplib():
    notifier = SMTPNotifier(host="smtp.example.com", port=587, username="u", password="p", from_addr="rai@kmitl.ac.th")
    mock_server = MagicMock()
    mock_smtp_cm = MagicMock()
    mock_smtp_cm.__enter__.return_value = mock_server
    with patch("smtplib.SMTP", return_value=mock_smtp_cm) as mock_smtp:
        notifier.notify_ready(make_request())
        mock_smtp.assert_called_once_with("smtp.example.com", 587, timeout=10)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("u", "p")
        mock_server.send_message.assert_called_once()
        sent_msg = mock_server.send_message.call_args[0][0]
        assert sent_msg["To"] == "nan@example.com"
        assert "ready" in sent_msg["Subject"].lower()


def test_smtp_notifier_skips_send_when_no_email():
    notifier = SMTPNotifier(host="smtp.example.com")
    with patch("smtplib.SMTP") as mock_smtp:
        notifier.notify_ready(make_request(student_email=""))
        mock_smtp.assert_not_called()


def test_smtp_notifier_no_tls_no_login_when_configured_off():
    notifier = SMTPNotifier(host="smtp.example.com", use_tls=False, username="")
    mock_server = MagicMock()
    mock_smtp_cm = MagicMock()
    mock_smtp_cm.__enter__.return_value = mock_server
    with patch("smtplib.SMTP", return_value=mock_smtp_cm):
        notifier.notify_pending(make_request(status=RequestStatus.PENDING, pending_reason="short"))
        mock_server.starttls.assert_not_called()
        mock_server.login.assert_not_called()
