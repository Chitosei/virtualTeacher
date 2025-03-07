from fastapi import HTTPException

from src.setting import GG_DRIVE
from .models import TeachingSimulationRequest
from .memory import ConversationMemory
from web.api.api_utils import generate_response, clean_text
import requests
# Khởi tạo bộ nhớ hội thoại
conversation_memory = ConversationMemory(max_length=20)


async def teaching_simulation_endpoint(request: TeachingSimulationRequest):
    session_id = request.session_id
    user_input = request.user_input
    role = request.role.lower()

    if role not in ["teacher", "student"]:
        raise HTTPException(status_code=400, detail="Role phải là 'teacher' hoặc 'student'.")

    # Khởi tạo lịch sử hội thoại nếu chưa có
    if session_id not in conversation_memory.sessions:
        conversation_memory.sessions[session_id] = []

    # Thêm tin nhắn của người dùng vào lịch sử
    conversation_memory.add_message(session_id, role, user_input)

    # Lấy lịch sử hội thoại
    history = conversation_memory.get_history(session_id)
    conversation_history_text = "\n".join([f"{m['role'].capitalize()}: {m['message']}" for m in history])

    # Xác định ai sẽ nói tiếp
    next_speaker = "student" if role == "teacher" else "teacher"

    # Tạo prompt cho AI
    prompt = f"""
    Bạn đang tham gia một cuộc hội thoại giữa giáo viên và học sinh.
    - Giáo viên cung cấp hướng dẫn và phản hồi.
    - Học sinh có thể đặt câu hỏi hoặc phản hồi.
    - Trả lời với vai trò: {next_speaker}.
    - Không được để tên vai trò của mình ở đầu câu trả lời.
    Cuộc hội thoại hiện tại:
    {conversation_history_text}

    Phản hồi tiếp theo:
    """

    # Gọi AI để tạo phản hồi
    ai_response = generate_response([{"role": "system", "content": "Bạn là một chuyên gia giáo dục. Hãy trả lời không quá 300 tokens"},
                                     {"role": "user", "content": prompt}])

    cleaned_text = clean_text(ai_response)
    # Gửi phản hồi AI đến API chuyển giọng nói
    voice_api_url = "http://localhost:8001/api/voice/voice"
    voice_payload = {"file_url": f"{GG_DRIVE}", "text": cleaned_text}

    voice_response = requests.post(voice_api_url, json=voice_payload)
    if voice_response.status_code == 200:
        audio_url = voice_response.json().get("audio_url")
    else:
        audio_url = None  # Nếu API voice thất bại, chỉ trả về văn bản

    # Lưu phản hồi của AI
    conversation_memory.add_message(session_id, next_speaker, ai_response)

    return {"response": ai_response, "role": next_speaker}
