from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

@dataclass(frozen=True)
class EmlMetadata:
    path: Path
    subject: str
    sender: str
    recipients: str
    date: datetime | None
    attachments: tuple[str, ...]
    size_bytes: int

def parse_eml(path: Path) -> EmlMetadata:
    raw = path.read_bytes()

    message = BytesParser(
        policy=policy.default
    ).parsebytes(raw)

    # 일단 파싱은 된듯

    date = None
    date_header = message.get("Date")

    if date_header:
        try:
            date = parsedate_to_datetime(str(date_header))
        except (TypeError, ValueError, IndexError):
            print("Error Captured on parsedate_to_datetime")
            pass

    attachments = []

    # 첨부파일 다루는 섹션(근데 naverworks에서 제공하는 백업 기능에 첨부파일이 빠져있는 듯한 불길한 느낌
    for part in message.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            attachments.append(filename or "unnamed")

    return EmlMetadata(
        path=path,
        subject=str(message.get("Subject", "Untitled")),
        sender=str(message.get("From", "Unknown sender")),
        recipients=str(message.get("To", "Unknown recipients")),
        date=date,
        attachments=tuple(attachments),
        size_bytes=len(raw)
    )

def read_raw_eml(path: Path) -> bytes:
    return path.read_bytes()