import uvicorn
from fastapi import FastAPI
from web.api.talk_to_yourself.api import router as chatbot_router
from web.api.reflective_dialogue.api import router as reflective_router

# Initialize FastAPI app
app = FastAPI()

# ✅ IncludeAPIs
app.include_router(chatbot_router)   # Include Chatbot API
app.include_router(reflective_router)


# change the route if conflict
if __name__ == "__main__":
    uvicorn.run("web.__main__:app", port=8000, reload=True)
