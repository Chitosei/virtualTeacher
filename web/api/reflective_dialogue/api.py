from fastapi import APIRouter, HTTPException, Form
from web.api.api_utils import generate_response, ChatRequest

# Create a separate router for reflective dialogue
router = APIRouter()

# Store chat history in memory
reflection_sessions = {}


@router.post("/reflective_dialogue")
def reflect(request: ChatRequest):
    """API to guide reflective teaching discussions."""
    try:

        if request.session_id not in reflection_sessions:
            reflection_sessions[request.session_id] = []

        reflection_history = reflection_sessions[request.session_id]

        # System prompt to encourage reflection
        messages = [{"role": "system", "content":
            f"Bạn là cố vấn AI hướng dẫn giáo viên tự đánh giá về việc giảng dạy của mình. "
            f"Khuyến khích suy nghĩ sâu sắc hơn và đặt câu hỏi mở. Trả lời trong bằng tiếng việt."
                     }]

        messages.extend(reflection_history)
        messages.append({"role": "user", "content": request.user_input})

        # Generate reflective response
        response_text = generate_response(messages)

        reflection_sessions[request.session_id].append({"role": "user", "content": request.user_input})
        reflection_sessions[request.session_id].append({"role": "assistant", "content": response_text})

        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
