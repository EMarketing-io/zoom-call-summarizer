import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import tempfile
import io
from dotenv import load_dotenv

load_dotenv()


def authenticate_with_oauth():
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


def get_drive_service(api_key=None):
    if api_key:
        service = build("drive", "v3", developerKey=api_key)
    else:
        service = authenticate_with_oauth()
    return service


def download_audio_from_drive(file_id, api_key):
    service = get_drive_service(api_key)
    request = service.files().get_media(fileId=file_id)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

    downloader = MediaIoBaseDownload(temp_file, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Downloading audio: {int(status.progress() * 100)}%")

    temp_file.close()
    return temp_file.name


def upload_file_to_drive_in_memory(
    file_data, folder_id, api_key=None, final_name="Zoom Call Notes.docx"
):
    service = get_drive_service(api_key)
    file_metadata = {"name": final_name, "parents": [folder_id]}

    file_stream = io.BytesIO(file_data)
    media = MediaIoBaseUpload(
        file_stream,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    print(f"File uploaded: {file.get('id')}")
    return file.get("id")
