from fastapi import HTTPException
from .models import TeachingSimulationRequest
from .memory import ConversationMemory
from web.api.api_utils import generate_response

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
    - Không được để vai trò ở đầu câu trả lời 

    Cuộc hội thoại hiện tại:
    {conversation_history_text}

    Phản hồi tiếp theo:
    """

    # Gọi AI để tạo phản hồi
    ai_response = generate_response([{"role": "system", "content": "Bạn là một chuyên gia giáo dục."},
                                     {"role": "user", "content": prompt}])

    # Lưu phản hồi của AI
    conversation_memory.add_message(session_id, next_speaker, ai_response)
     # Gọi TTS để chuyển phản hồi thành giọng nói
    audio_url = text_to_speech(ai_response, session_id)
    return {
            "session_id": session_id,
            "response": ai_response,
            "audio_url": audio_url, 
            "role": next_speaker
        }
