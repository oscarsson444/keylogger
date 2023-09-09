import os
import pickle

# Gmail API utilities
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Encoding utilities
from base64 import urlsafe_b64encode

# Email utilities
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

# Constants
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


# Authenticate the user to the Gmail API
def authenticate():
    creds = None

    # Check if token.pickle exists
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh token
            creds.refresh(Request())
        else:
            # Request new token
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


# Create a message with an embedded image
def create_email_with_embedded_image(sender, to, subject, message_text, image_filename):
    # Create message container
    msg = MIMEMultipart()
    msg["to"] = to
    msg["from"] = sender
    msg["subject"] = subject

    # Create HTML message with embedded image
    html = f"""\
    <html>
    <body>
        <img src="cid:image1">
        <p>{message_text}</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    # Attach the image with a Content-ID
    with open(image_filename, "rb") as image_file:
        image_data = image_file.read()
        image = MIMEImage(image_data)
        image.add_header("Content-ID", "<image1>")
        msg.attach(image)

    return msg


# Create a raw email message from the MIME message
def create_raw_email_message(message):
    return {"raw": urlsafe_b64encode(message.as_bytes()).decode()}


# Send email with embedded image
def send_email_with_embedded_image(sender, to, subject, message_text, image_filename):
    print(sender, to)

    # Get Gmail API service
    service = authenticate()

    # Create message with embedded image
    email_message = create_email_with_embedded_image(
        sender, to, subject, message_text, image_filename
    )

    # Convert the MIME message to a raw email message
    raw_email_message = create_raw_email_message(email_message)

    # Send message
    try:
        message = (
            service.users()
            .messages()
            .send(userId="me", body=raw_email_message)
            .execute()
        )
        print("Message Id: %s" % message["id"])
        return message
    except Exception as error:
        print("An error occurred: %s" % error)
        return None
