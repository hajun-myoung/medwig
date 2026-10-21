import base64

import pytest

from mail_migrator.gmail import build_message


def test_build_inbox_message():
    raw = (
        b"From: sender@example.com\r\n"
        b"To: receiver@example.com"
        b"Subject: Test\r\n"
        b"\r\n"
        b"Hello"
    )

    result = build_message(raw, "INBOX")

    assert result["labelIds"] == ["INBOX"]

    decoded = base64.urlsafe_b64decode(result["raw"])

    assert decoded == raw


def test_build_sent_message():
    result = build_message(b"Subject: Hello\r\n\r\nBody", "SENT")

    assert result["labelIds"] == ["SENT"]


def test_invalid_mailbox():
    with pytest.raises(ValueError):
        build_message(b"Subject: Test\r\n\r\nBody", "Starred")
