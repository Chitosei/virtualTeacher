import json
import os

from fastapi import APIRouter, HTTPException, Form
from web.api.api_utils import generate_response, ChatRequest
from web.api.api_utils import text_to_speech
# Create a separate router for reflective dialogue
router = APIRouter()

# File to store reflective dialogue history (later will move to DB)
os.makedirs("data", exist_ok=True)
REFLECTIVE_HISTORY_FILE = "data/reflective_history.json"


# Load reflective dialogue history from file
def load_reflective_history():
    """Loads reflective dialogue history from a JSON file."""
    if os.path.exists(REFLECTIVE_HISTORY_FILE):
        with open(REFLECTIVE_HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}  # Return empty dictionary if file is corrupted
    return {}  # Return empty dictionary if file doesn't exist


# Save reflective dialogue history to file
def save_reflective_history(history_data):
    """Saves reflective dialogue history to a JSON file."""
    with open(REFLECTIVE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=4)


# Load reflective history when API starts
reflection_sessions = load_reflective_history()


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
        audio_url = text_to_speech(response_text)
        reflection_sessions[request.session_id].append({"role": "user", "content": request.user_input})
        reflection_sessions[request.session_id].append({"role": "assistant", "content": response_text})

        save_reflective_history(reflection_sessions)

        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_reflective_history")
def get_reflective_history(session_id: str):
    """Retrieves reflective dialogue history for a specific session."""
    if session_id not in reflection_sessions:
        return {"message": "No reflective dialogue history found for this session."}

    return {"session_id": session_id, "reflective_history": reflection_sessions[session_id]}
