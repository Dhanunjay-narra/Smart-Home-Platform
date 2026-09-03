from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from services.intelligence.nlp_engine import nlp_engine
from services.identity.routes import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)

    @field_validator("query")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Query cannot be empty or whitespace only.")
        return cleaned

@router.post("/chat")
async def chat_with_assistant(req: QueryRequest, user = Depends(get_current_user)):
    return await nlp_engine.process_query(req.query)
