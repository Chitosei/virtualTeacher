import openai
from pydantic import BaseModel
api_key = "api_key"


def generate_response(messages):
    """
    Generates a response using OpenAI GPT-4o-mini.
    """
    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


class ChatRequest(BaseModel):
    """Request object for AI chatbot."""
    llm_model: str = "gpt-4o-mini"
    session_id: str
    user_input: str
    language: str = "vi"


