from pydantic import BaseModel

class TeachingSimulationRequest(BaseModel):
    session_id: str
    user_input: str
    role: str  # "teacher" hoặc "student"
