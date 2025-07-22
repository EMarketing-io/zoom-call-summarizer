import os
import shutil
from pydub import AudioSegment

from drive_utils import (
    extract_drive_file_id,
    download_audio_from_drive,
    get_parent_folder,
)
from transcription import transcribe_audio
from summarizer import generate_summary
from doc_generator import generate_docx


def split_audio(audio_path, chunk_length_ms=5 * 60 * 1000):  # 5 minutes
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i : i + chunk_length_ms]
        chunk_path = f"{audio_path}_part{i // chunk_length_ms}.mp3"
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
    return chunks


def main():
    drive_link = input("Enter the Google Drive link of the audio file: ").strip()
    file_id = extract_drive_file_id(drive_link)

    if not file_id:
        raise Exception("Invalid Google Drive link")

    print("📥 Downloading audio...")
    audio_path = download_audio_from_drive(file_id)

    print("🎧 Splitting audio into smaller chunks...")
    chunks = split_audio(audio_path)

    print("📝 Transcribing chunks...")
    transcripts = [transcribe_audio(chunk) for chunk in chunks]
    transcript_text = "\n".join(transcripts)

    print("🧠 Generating summary...")
    summary_data = generate_summary(transcript_text)

    print("📄 Creating DOCX file...")
    docx_file = generate_docx(summary_data)

    save_folder = "docs"
    os.makedirs(save_folder, exist_ok=True)
    final_path = os.path.join(save_folder, "Zoom Call Notes.docx")
    shutil.move(docx_file, final_path)
    print(f"💾 Saved DOCX locally to: {final_path}")

    os.remove(audio_path)
    for chunk in chunks:
        os.remove(chunk)
    print("✅ All done! File saved locally.")


if __name__ == "__main__":
    main()
