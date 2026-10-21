from pathlib import Path

from mail_migrator.auth import (
    get_authenticated_email,
    get_credentials,
    get_gmail_service,
)

creds = get_credentials(Path("credentials.json"), Path("token.json"))

email = get_authenticated_email(creds)
service = get_gmail_service(creds)

print("Google Signin Successful")
print("Authenticated account: ", email)
print("Gmail client ready: ", service is not None)
