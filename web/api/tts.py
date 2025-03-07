import uuid

from gtts import gTTS
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import re

router = APIRouter()

AUDIO_DIR = "static/audio/"  # Thư mục lưu file âm thanh
os.makedirs(AUDIO_DIR, exist_ok=True)  # Tạo thư mục nếu chưa có


def reset_audio_folder():
    """Deletes all audio files in the static/audio/ folder before generating new audio."""
    for file in os.listdir(AUDIO_DIR):
        file_path = os.path.join(AUDIO_DIR, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)  # Delete the file
        except Exception as e:
            print(f"❌ Error deleting file {file_path}: {e}")




def text_to_speech(text: str):
    """Chuyển đổi văn bản thành giọng nói bằng gTTS"""
    try:
        reset_audio_folder()
        cleaned_text = clean_text(text)
        unique_filename = f"{uuid.uuid4().hex}.mp3"  # Generate a unique filename
        output_file = os.path.join(AUDIO_DIR, unique_filename)

        tts = gTTS(text=cleaned_text, lang="vi")  # Chọn tiếng Việt
        tts.save(output_file)

        return {"audio_url": f"/play_audio/{unique_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo giọng nói: {str(e)}")


@router.get("/play_audio/{filename}")
async def play_audio(filename: str):
    """Serves a dynamically generated audio file."""
    audio_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(audio_path, media_type="audio/mpeg", filename=filename)