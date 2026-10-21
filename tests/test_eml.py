from datetime import UTC, datetime
from email.message import EmailMessage

from mail_migrator.eml import parse_eml, read_raw_eml


def test_parse_eml_with_attachment(tmp_path):
    message = EmailMessage()

    message["From"] = "sender@example.com"
    message["To"] = "receiver@example.com"
    message["Subject"] = "한글 메일 제목 테스트"
    message["Date"] = "Mon, 19 Oct 2026 12:20:00 +0900"

    # TODO: 여기는 나중에 Lorem 장문도 넣어서 테스트 요망
    message.set_content("Testing Contents\n테스트 메일 본문")

    message.add_attachment(
        b"Hello, Attachment.",
        maintype="application",
        subtype="octet-stream",
        filename="lorem.txt",
    )

    path = tmp_path / "sample.eml"
    original = message.as_bytes()
    path.write_bytes(original)

    metadata = parse_eml(path)

    assert metadata.subject == "한글 메일 제목 테스트"
    assert metadata.sender == "sender@example.com"
    assert metadata.recipients == "receiver@example.com"
    assert metadata.attachments == "lorem.txt"

    assert metadata.date == datetime(2026, 10, 19, 12, 20, tzinfo=UTC).astimezone(
        UTC
    ).replace(hour=3, minute=30)

    assert metadata.size_bytes == len(original)
    assert read_raw_eml(path) == original
