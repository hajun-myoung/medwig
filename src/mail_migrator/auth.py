import json
from pathlib import Path
from urllib.request import Request as URLRequest
from urllib.request import urlopen

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.insert",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def get_credentials(credentials_path: Path, token_path: Path):
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes=SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        token_path.write_text(creds.to_json(), encoding="utf-8")

    return creds


def get_gmail_service(creds):
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def get_authenticated_email(creds: Credentials) -> str:
    if not creds.valid:
        creds.refresh(Request())

    request = URLRequest(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {creds.token}"},
    )

    with urlopen(request, timeout=15) as response:
        info = json.load(response)

    return info["email"]
