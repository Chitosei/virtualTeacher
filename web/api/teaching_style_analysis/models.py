from pydantic import BaseModel

class TeachingFeedback(BaseModel):
    session_id: str
    teacher_feedback: str  # Phản hồi của giáo viên sau bài giảng
