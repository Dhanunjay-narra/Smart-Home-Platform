from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.intelligence.nlp_engine import nlp_engine
from services.identity.routes import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_with_assistant(req: QueryRequest, user = Depends(get_current_user)):
    return await nlp_engine.process_query(req.query)
