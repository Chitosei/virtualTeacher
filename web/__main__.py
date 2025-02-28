import uvicorn
from fastapi import FastAPI
from web.api.talk_to_yourself.api import router as chatbot_router
from web.api.reflective_dialogue.api import router as reflective_router
from web.api.knowledge_recall_assistant.api import router as knowledge_router
from web.api.teaching_analysis import router as teaching_analysis_router
from web.api.teaching_simulation import router as teaching_simulation_router
from web.api.time_management_assistant.api import router as time_management_router

# Initialize FastAPI app
app = FastAPI()


# ✅ Include APIs
app.include_router(chatbot_router)   # Include Chatbot API
app.include_router(reflective_router)
app.include_router(knowledge_router)
app.include_router(teaching_analysis_router)
app.include_router(teaching_simulation_router)
app.include_router(time_management_router)

# change the route if conflict
if __name__ == "__main__":
    uvicorn.run("web.__main__:app", port=8000, reload=True)
