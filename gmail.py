import os

from dotenv import load_dotenv

load_dotenv()


def create_message(to: str, subject: str, body: str) -> dict:
    from email.mime.text import MIMEText
    import base64

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def send_email_with_refresh_token(
        recipient_email: str,
        subject: str,
        body: str,
        refresh_token: str,
        token_uri: str = "https://oauth2.googleapis.com/token",
):
    """Send email using Gmail API and refresh token."""

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET")
    )

    # Refresh access token
    creds.refresh(Request())

    # Build Gmail service
    service = build("gmail", "v1", credentials=creds)

    # Create and send the message
    message = create_message(recipient_email, subject, body)
    sent_message = service.users().messages().send(userId="me", body=message).execute()
    print("sent with Gmail API")
    return {
        "message_id": sent_message["id"],
        "thread_id": sent_message["threadId"],
        "access_token": creds.token,
        "token_expiry": creds.expiry.isoformat() if creds.expiry else None
    }