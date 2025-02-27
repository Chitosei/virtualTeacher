import json
import os
import sys

import openai
from pydantic import BaseModel
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.setting import store_message
# Load .env file
load_dotenv()

# Database Config
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# OpenAI Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def generate_response(message):
    """
    Generates a response using OpenAI GPT-4o-mini.
    """
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=message,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def generate_talk_response(user_input):
    """
    Generates a response using OpenAI GPT-4o-mini.
    """
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Bạn là một chatbot hỗ trợ giáo viên trả lời vấn đề học đường. Hãy trả lời bằng tiếng Việt."},
                {"role": "user", "content": user_input}  # ✅ Fix: Pass as a list of objects
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def generate_knowledge_response(message, user_id, session_id):
    """
        Generates a structured JSON response.
    """
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role":"system",
                    "content":"Bạn là một chuyên viên hỗ trợ cung cấp câu trả lời chi tiết về kiến thức học. "
                            "Trả về câu trả lời dưới dạng JSON với các phần: 'subject', 'topic', 'content'. "
                            "Hãy cung cấp nội dung đầy đủ với định nghĩa, lịch sử, ứng dụng thực tế, công thức, và ví dụ cụ thể."

                },
                {"role": "user", "content": f"Hãy giải thích chi tiết về chủ đề sau: {message}."}
            ],
            temperature=0.8,
            max_tokens=500
        )

        response_text = response.choices[0].message.content.strip()

        # Store response in chat_history
        store_message(user_id, session_id, "assistant", response_text)

        return response_text

    except Exception as e:
        print(f"Error in LLM response: {e}")
        return "Xin lỗi, tôi không thể trả lời câu hỏi này ngay bây giờ."


class ChatRequest(BaseModel):
    """Request object for AI chatbot."""
    llm_model: str = "gpt-4o-mini"
    session_id: str
    user_input: str
    language: str = "vi"


