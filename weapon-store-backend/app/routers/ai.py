from fastapi import APIRouter, Depends, Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ai_service import generate_ai_response
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.chat_message import ChatMessage
from app.models.user import User
from app.schemas.ai import ChatRequest, ChatResponse
from app.schemas.chat import ChatMessageResponse

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


@router.delete("/history", status_code=204)
async def clear_chat_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.scalar(select(User.id).where(User.id == current_user.id).with_for_update())
    await db.execute(delete(ChatMessage).where(ChatMessage.user_id == current_user.id))
    await db.commit()
    return Response(status_code=204)
