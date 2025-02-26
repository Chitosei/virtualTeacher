from fastapi import HTTPException
from .models import TeachingFeedback
from .nlp_model import classify_teaching_style

# Bộ nhớ tạm để lưu phản hồi của giáo viên
feedback_storage = {}

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

    return {
        "session_id": session_id,
        "teaching_style": teaching_style,
        "message": "Đã phân tích phong cách giảng dạy thành công."
    }
