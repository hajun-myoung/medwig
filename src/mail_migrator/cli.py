import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from mail_migrator.auth import (
    get_authenticated_email,
    get_credentials,
    get_gmail_service,
)
from mail_migrator.eml import parse_eml
from mail_migrator.gamil import insert_eml


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--mailbox", choices=["INBOX", "SENT"], required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--account",
    )
    parser.add_argument("--commit", action="store_true")

    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be >= 1")

    if args.commit and not args.account:
        parser.error("--account is required with --commit")

    files = sorted(
        p for p in args.folder.rglob("*") if p.is_file() and p.suffix.lower() == ".eml"
    )

    print(f"Discovered: {len(files)} emails")

    if not args.commit:
        print("DRY RUN - no upload")

        for file in files[: args.limit]:
            metadata = parse_eml(file)
            print(metadata.date, metadata.subject, metadata.size_bytes)

        return

    creds = get_credentials(Path("credentials.json"), Path("token.json"))

    actual_account = get_authenticated_email(creds)

    if actual_account.lower() != args.account.lower():
        raise RuntimeError(f"Wrong Google Account: {actual_account}")

    service = get_gmail_service(creds)
    db = sqlite3.connect("migration.sqlite3")

    db.execute("""
        CREATE TABLE IF NOT EXIST uploads (
            account TEXT NOT NULL,
            mailbox TEXT NOT NULL,
            digest TEXT NOT NULL,
            gmail_id TEXT NOT NULL,
            PRIMARY KEY (account, mailbox, digest)
        )
    """)

    # counters
    uploaded = 0
    skipped = 0
    failed = 0

    for file in files:
        if uploaded >= args.limit:
            # stop by limit
            break

        digest = hashlib.sha256(file.read_bytes()).hexdigest()

        existing = db.execute(
            """
                SELECT gmail_id FROM uploads
                WHERE account = ?
                  AND mailbox = ?
                  AND digest = ?
            """,
            (actual_account, args.mailbox, digest),
        ).fetchone()

        if existing:
            # skip by duplicated email
            skipped += 1
            continue

        try:
            gmail_id = insert_eml(service, actual_account, file, args.mailbox)

            with db:
                db.execute(
                    """
                    INSERT INTO uploads
                    (account, mailbox, digest, gmail_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (actual_account, args.mailbox, digest, gmail_id),
                )

                uploaded += 1
                print(f"[OK] {file.name} => {gmail_id}")
        except Exception as error:  # noqa: BLE001
            failed += 1
            print(f"[FAIL] {file.name}: {error}")

        db.close()

        print(
            json.dumps(
                {"uploaded": uploaded, "skipped": skipped, "failed": failed}, indent=2
            )
        )


if __name__ == "__main__":
    main()
