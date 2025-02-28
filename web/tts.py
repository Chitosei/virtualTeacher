from gtts import gTTS
import os
from fastapi import APIRouter, HTTPException

router = APIRouter()

AUDIO_DIR = "static/audio/"  # Thư mục lưu file âm thanh
os.makedirs(AUDIO_DIR, exist_ok=True)  # Tạo thư mục nếu chưa có

@router.post("/text_to_speech/")
async def text_to_speech(text: str):
    """Chuyển đổi văn bản thành giọng nói bằng gTTS"""
    try:
        output_file = os.path.join(AUDIO_DIR, "output.mp3")
        tts = gTTS(text=text, lang="vi")  # Chọn tiếng Việt
        tts.save(output_file)

        return {"audio_url": f"/audio/output.mp3"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo giọng nói: {str(e)}")
