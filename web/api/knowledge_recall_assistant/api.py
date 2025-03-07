import os
import sys

import requests
from fastapi import APIRouter, HTTPException
from web.api.api_utils import generate_knowledge_response, enhance_response_with_openai

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.setting import retrieve_relevant_knowledge, store_knowledge, GG_DRIVE
from ..knowledge_recall_assistant.schema import KnowledgeRecall, NewKnowledge
# Create router for Knowledge Recall API
router = APIRouter()
# Voice API URL
VOICE_API_URL = "http://localhost:8001/api/voice/voice"


@router.post("/add_knowledge")
def add_knowledge(request: NewKnowledge):
    """Stores new knowledge with references, embeddings, and chunking."""
    try:
        store_knowledge(request.question, request.answer, request.references)

        return {"message": "Knowledge added successfully!", "question": request.question, "references": references}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search_knowledge")
def search_knowledge(request: KnowledgeRecall):
    """
    Searches for relevant knowledge in the database. If no knowledge exists,
    generates a new response using LLM and stores it in knowledge_base.
    """
    try:
        # Step 1: Retrieve relevant stored knowledge
        relevant_knowledge = retrieve_relevant_knowledge(request.query)

        if relevant_knowledge:
            print("Found existing knowledge.")
            # Enhance the retrieved knowledge using OpenAI
            enhanced_answer = enhance_response_with_openai(request.query, relevant_knowledge)
        else:
            # Step 2: If no stored knowledge, generate a new response using LLM
            print("Generating new knowledge.")
            enhanced_answer = generate_knowledge_response(request.query, request.user_id, request.session_id)

            # Step 3: Store the new response in `knowledge_base`
            if enhanced_answer:
                store_knowledge(request.query, enhanced_answer)

        # Call voice API to generate speech
        voice_payload = {"file_url": f"{GG_DRIVE}", "text": enhanced_answer}
        voice_response = requests.post(VOICE_API_URL, json=voice_payload)

        if voice_response.status_code == 200:
            audio_url = "Audio saved in voice_clone/app/static/media"
        else:
            audio_url = None  # Fallback in case the voice API fails

        return {"result": enhanced_answer, "audio_url": audio_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
