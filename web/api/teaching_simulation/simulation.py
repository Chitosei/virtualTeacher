import json
import os

from fastapi import APIRouter, HTTPException
from web.api.api_utils import generate_talk_response, ChatRequest
from web.api.api_utils import text_to_speech
# Initialize FastAPI app
router = APIRouter()

# File to store chat history (to be replaced with DB later)
os.makedirs("data",exist_ok=True)
CHAT_HISTORY_FILE = "data/chat_history.json"


# Load chat history from file
def load_chat_history():
    """Loads chat history from a JSON file."""
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):  # Đảm bảo dữ liệu là dict
                    return data
            except json.JSONDecodeError:
                return {}  # Trả về dict rỗng thay vì list
    return {}  # Trả về dict rỗng thay vì list



# Save chat history to file
def save_chat_history(chat_data):
    """Saves chat history to a JSON file."""
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=4)


# ✅ Load chat history into chat_sessions on startup
chat_sessions = load_chat_history()


@router.post("/talk_to_yourself")
def chat(request: ChatRequest):
    """
    API endpoint to handle user input and return chatbot response, storing conversation history.
    """
    try:
        # Get chat history for the session_id
        if request.session_id not in chat_sessions:
            chat_sessions[request.session_id] = []

        chat_history = chat_sessions[request.session_id]

        # Append previous messages to maintain conversation context
        messages = [{"role": "system", "content": "Bạn là một chatbot hỗ trợ giáo viên trả lời vấn đề học đường. Hãy trả lời bằng tiếng Việt."}]
        messages.extend(chat_history)  # Add chat history
        messages.append({"role": "user", "content": request.user_input})  # Add new user message

        # Generate response from GPT-4o-mini
        response_text = generate_talk_response(request.user_input)
        audio_url = text_to_speech(response_text)
        # Store conversation history
        chat_sessions[request.session_id].append({"role": "user", "content": request.user_input})
        chat_sessions[request.session_id].append({"role": "assistant", "content": response_text})

        # Save updated history to file
        save_chat_history(chat_sessions)

        return {"session_id": request.session_id, "response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_chat_history")
def get_chat_history(session_id: str):
    """Retrieves chat history for a specific session."""
    if session_id not in chat_sessions:
        return {"message": "No chat history found for this session."}

    return {"session_id": session_id, "chat_history": chat_sessions[session_id]}
