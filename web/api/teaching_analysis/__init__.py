import openai
from fastapi import APIRouter
from .analysis import analyze_teaching_style

router = APIRouter()

# Endpoint phân tích phong cách giảng dạy
router.post("/teaching_analysis/")(analyze_teaching_style)
