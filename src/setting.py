import os

import numpy as np
import openai
import torch
import psycopg2
from transformers import AutoModel, AutoTokenizer
from dotenv import load_dotenv

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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load PhoBERT model & tokenizer
model = AutoModel.from_pretrained("vinai/phobert-large").to(device)
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-large")

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()


# Function to generate PhoBERT embeddings
def get_phobert_embedding(text):
    tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
    tokens = {k: v.to(device) for k, v in tokens.items()}  # Move to GPU

    with torch.no_grad():
        output = model(**tokens)

    embedding = output.last_hidden_state.mean(dim=1).cpu().numpy().flatten().tolist()  # Convert to list
    return embedding


def store_message(user_id, session_id, role, message):
    embedding = get_phobert_embedding(message)

    cursor.execute("""
        INSERT INTO chat_history (user_id, session_id, role, message, embedding)
        VALUES (%s, %s, %s, %s, %s::vector)
    """, (user_id, session_id, role, message, embedding))

    conn.commit()


def get_similar_messages(query_text, user_id, top_k=5):
    query_embedding = get_phobert_embedding(query_text)

    cursor.execute("""
        SELECT message FROM chat_history
        WHERE user_id = %s
        ORDER BY embedding <-> %s::vector 
        LIMIT %s
    """, (user_id, query_embedding, top_k))

    return [row[0] for row in cursor.fetchall()]


def retrieve_relevant_knowledge(query_text, top_k=5):
    query_embedding = get_phobert_embedding(query_text)

    # Ensure correct data format
    query_embedding = np.array(query_embedding, dtype=np.float32)

    cursor.execute("""
        SELECT answer FROM knowledge_base
        ORDER BY embedding <-> %s::vector
        LIMIT %s
    """, (query_embedding.tolist(), top_k))

    return [row[0] for row in cursor.fetchall()]


def generate_response(user_query):
    # Retrieve relevant knowledge from DB
    relevant_knowledge = retrieve_relevant_knowledge(user_query)

    # Construct the improved prompt
    context = "\n".join(relevant_knowledge)
    prompt = f"""
Bạn là một trợ lý AI chuyên hỗ trợ giáo viên và học sinh bằng tiếng Việt.
Nhiệm vụ của bạn là cung cấp câu trả lời chính xác, chi tiết và có tính giáo dục.

Câu hỏi của người dùng: {user_query}

Dưới đây là một số thông tin tham khảo từ cơ sở dữ liệu:
{context}

Hãy đưa ra một câu trả lời:
- Giải thích đầy đủ, chính xác, có ví dụ thực tế.
- Nếu có công thức hoặc định lý, hãy trình bày rõ ràng.
- Nếu cần, chia câu trả lời thành từng bước logic.
- Độ dài tối thiểu: 200 từ.

Trợ lý AI:
"""

    # Get response from GPT-4o-mini
    response = openai.OpenAI(api_key=OPENAI_API_KEY).chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=1000
    )

    return response.choices[0].message.content


def handle_user_query(user_query):
    response = generate_response(user_query)
    return response


def store_knowledge(query, response):
    """
    Stores newly generated knowledge in the knowledge_base table.
    """
    try:
        cursor.execute("""
            INSERT INTO knowledge_base (question, answer)
            VALUES (%s, %s)
        """, (query, response))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error storing knowledge: {e}")