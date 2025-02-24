from fastapi import APIRouter, HTTPException
from web.api.api_utils import generate_response, ChatRequest

# Initialize FastAPI app
router = APIRouter()

# Store chat history in memory (temporary)
chat_sessions = {}


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
        messages = [{"role": "system", "content": f"Bạn là một chatbot hỗ trợ giáo viên trả lời vấn đề học đường"
                                                  f". Hãy trả lời bằng tiếng việt."}]
        messages.extend(chat_history)  # Add chat history
        messages.append({"role": "user", "content": request.user_input})  # Add new user message

        # Generate response from GPT-4o-mini
        response_text = generate_response(messages)

        # Store conversation history
        chat_sessions[request.session_id].append({"role": "user", "content": request.user_input})
        chat_sessions[request.session_id].append({"role": "assistant", "content": response_text})

        return {"session_id": request.session_id, "response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
