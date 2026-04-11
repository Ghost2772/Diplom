from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.schemas.ai import ChatRequest, ChatResponse
from app.schemas.chat import ChatMessageResponse
from app.ai.ai_service import generate_ai_response

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer, blocked = await generate_ai_response(data.message, db, current_user.id)
    return ChatResponse(answer=answer, blocked=blocked)


@router.get("/history", response_model=list[ChatMessageResponse])
async def get_chat_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.id.asc())
    )
    messages = result.scalars().all()
    return messages