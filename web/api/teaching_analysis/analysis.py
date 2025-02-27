from fastapi import HTTPException
from .models import TeachingFeedback
from .nlp_model import classify_teaching_style
import os
import json

# Directory to store feedback history
os.makedirs("data", exist_ok=True)
TEACHING_FEEDBACK_FILE = "data/teaching_feedback.json"


# Load feedback history from file
def load_feedback_history():
    """Loads teaching feedback history from a JSON file."""
    if os.path.exists(TEACHING_FEEDBACK_FILE):
        with open(TEACHING_FEEDBACK_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):  # ✅ Ensure correct dictionary format
                    return data
            except json.JSONDecodeError:
                return {}  # Return empty dictionary if file is corrupted
    return {}  # Return empty dictionary if file doesn't exist


# Save feedback history to file
def save_feedback_history():
    """Saves teaching feedback history to a JSON file."""
    with open(TEACHING_FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback_storage, f, ensure_ascii=False, indent=4)


# ✅ Load feedback history on startup
feedback_storage = load_feedback_history()


async def analyze_teaching_style(feedback: TeachingFeedback):
    """Phân tích phong cách giảng dạy từ phản hồi của giáo viên"""
    session_id = feedback.session_id
    teacher_feedback = feedback.teacher_feedback

    if not teacher_feedback:
        raise HTTPException(status_code=400, detail="Phản hồi của giáo viên không được để trống.")

    # Phân tích phong cách giảng dạy
    teaching_style = classify_teaching_style(teacher_feedback)

    # Lưu phản hồi vào bộ nhớ tạm
    if session_id not in feedback_storage:
        feedback_storage[session_id] = []

    feedback_storage[session_id].append({"feedback": teacher_feedback, "style": teaching_style})

    # ✅ Save updated feedback history to file
    save_feedback_history()

    return {
        "session_id": session_id,
        "teaching_style": teaching_style,
        "message": "Đã phân tích phong cách giảng dạy thành công."
    }
