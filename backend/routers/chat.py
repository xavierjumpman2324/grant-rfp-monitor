from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.database import get_db
from models.models import ChatMessage, User
from routers.auth import get_current_user
from services.ai_analyzer import chat_with_ai

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def send_message(req: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    history = (
        db.query(ChatMessage)
        .filter_by(user_id=current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
        .all()
    )
    history_dicts = [{"role": m.role, "content": m.content} for m in reversed(history)]

    response = chat_with_ai(current_user, req.message, history_dicts)

    db.add(ChatMessage(user_id=current_user.id, role="user", content=req.message))
    db.add(ChatMessage(user_id=current_user.id, role="assistant", content=response))
    db.commit()

    return {"response": response}


@router.get("/history")
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = (
        db.query(ChatMessage)
        .filter_by(user_id=current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(100)
        .all()
    )
    return [{"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in messages]
