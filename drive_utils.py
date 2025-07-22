import re
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from config import SERVICE_ACCOUNT_FILE, SCOPES


credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)


def extract_drive_file_id(link):
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", link) or re.search(
        r"id=([a-zA-Z0-9_-]+)", link
    )
    return match.group(1) if match else None


def download_audio_from_drive(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    downloader = MediaIoBaseDownload(temp_file, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Downloading audio: {int(status.progress() * 100)}%")
    temp_file.close()
    return temp_file.name


def upload_file_to_drive(filepath, folder_id, final_name="Zoom Call Notes.docx"):
    file_metadata = {"name": final_name, "parents": [folder_id]}
    media = MediaFileUpload(filepath, resumable=True)
    uploaded_file = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id, webViewLink")
        .execute()
    )
    print(f"✅ Uploaded DOCX to Drive: {uploaded_file['webViewLink']}")
    return uploaded_file["webViewLink"]


def get_parent_folder(file_id, default_folder):
    metadata = drive_service.files().get(fileId=file_id, fields="parents").execute()
    return metadata.get("parents", [default_folder])[0]
