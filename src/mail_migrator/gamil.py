import base64
from pathlib import Path

VALID_MAILBOXES = {"INBOX", "SENT"}


def build_message(raw_eml: bytes, mailbox: str) -> dict:
    if mailbox not in VALID_MAILBOXES:
        raise ValueError(f"Unsupported mailbox: {mailbox}")

    encoded = base64.urlsafe_b64encode(raw_eml).decode("ascii")

    return {"raw": encoded, "labelIds": [mailbox]}


def insert_eml(service, account: str, path: Path, mailbox: str) -> str:
    raw_eml = path.read_bytes()

    body = build_message(raw_eml, mailbox)

    response = (
        service.users()
        .messages()
        .insert(userId=account, body=body, internalDateSource="dateHeader")
    ).execute()

    return response["id"]
