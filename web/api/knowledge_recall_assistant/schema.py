from pydantic import BaseModel, Field


class NewKnowledge(BaseModel):
    question: str
    answer: str
    references: str = Field(default="General")


class KnowledgeRecall(BaseModel):
    user_id: str
    session_id: str
    query: str