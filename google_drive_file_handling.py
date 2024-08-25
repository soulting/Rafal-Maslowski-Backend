import base64
import io
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
SERVICE_ACCOUNT_INFO = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
PARENT_FOLDER_ID = os.getenv("PARENT_FOLDER_ID")


def authenticate():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES
    )
    return credentials


def uploadToDrive(file_data, file_name):
    """Zdekoduj dane Base64 i załaduj plik na Google Drive."""
    file_stream = io.BytesIO(file_data)

    credentials = authenticate()
    service = build("drive", "v3", credentials=credentials)

    file_metadata = {"name": file_name, "parents": [PARENT_FOLDER_ID]}

    media = MediaIoBaseUpload(file_stream, mimetype="application/octet-stream")

    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(
        fileId=file["id"],
        body=permission,
        fields='id'
    ).execute()

    return f"https://drive.usercontent.google.com/download?id={file["id"]}"
