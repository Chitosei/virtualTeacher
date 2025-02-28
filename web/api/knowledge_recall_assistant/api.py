
from web.api.api_utils import text_to_speech
import os
import sys
from fastapi import APIRouter, HTTPException, Form, Query
from web.api.api_utils import generate_knowledge_response, enhance_response_with_openai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.setting import retrieve_relevant_knowledge, store_knowledge, store_message

# Create router for Knowledge Recall API
router = APIRouter()


@router.post("/add_knowledge")
def add_knowledge(user_id: int = Form(...), session_id: int = Form(...), message: str = Form(...)):
    try:
        store_message(user_id, session_id, "assistant", message)  # Store in chat_history
        return {"message": "Knowledge added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_knowledge")
def search_knowledge(query: str = Query(..., description="Nhập câu hỏi về kiến thức học thuật")):
    """
    Searches for relevant knowledge in the database. If no knowledge exists,
    generates a new response using LLM and stores it in knowledge_base.
    """
    try:
        # Step 1: Retrieve relevant stored knowledge
        relevant_knowledge = retrieve_relevant_knowledge(query)

        if relevant_knowledge:
            print("Found questions!")
            print(relevant_knowledge)
            # Enhance the retrieved knowledge using OpenAI
            enhanced_answer = enhance_response_with_openai(query, relevant_knowledge)
            audio_url = text_to_speech(enhanced_answer)
            return {"result": enhanced_answer}

        # Step 2: If no stored knowledge, generate a new response using LLM
        new_knowledge = generate_knowledge_response(query)

        # Step 3: Store the new response in `knowledge_base`
        if new_knowledge:
            print("New questions!")
            store_knowledge(query, new_knowledge)
            return {"result": new_knowledge}

        return {"error": "Không thể tạo câu trả lời vào lúc này."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
