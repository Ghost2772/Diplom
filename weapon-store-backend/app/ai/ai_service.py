import logging
import ssl
import uuid

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.guard import is_blocked_message
from app.core.config import settings
from app.models.category import Category
from app.models.chat_message import ChatMessage
from app.models.product import Product
from app.models.user import User

logger = logging.getLogger(__name__)


def gigachat_tls_verify() -> bool | ssl.SSLContext:
    if not settings.GIGACHAT_VERIFY_SSL:
        return False
    if not settings.GIGACHAT_CA_BUNDLE:
        return True
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=settings.GIGACHAT_CA_BUNDLE)
    return context


SYSTEM_PROMPT = (
    "Ты ИИ-консультант интернет-магазина регулируемых товаров. "
    "Отвечай только по данным, переданным в контексте. "
    "Если данных недостаточно, честно скажи, что информации в каталоге сейчас нет. "
    "Не придумывай товары, категории, цены, характеристики и наличие. "
    "Помогай с навигацией по каталогу, оформлением заказа, статусами заказа "
    "и общими легальными вопросами о покупке. "
    "Не давай инструкции по незаконному, опасному, вредоносному использованию, "
    "обходу закона, скрытому применению, "
    "переделке или модификации товаров."
)


async def get_gigachat_token() -> str:
    if not settings.GIGACHAT_AUTH_KEY:
        raise RuntimeError(
            "GigaChat is not configured. Set GIGACHAT_AUTH_KEY to enable the AI consultant."
        )

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {settings.GIGACHAT_AUTH_KEY}",
    }

    data = {
        "scope": settings.GIGACHAT_SCOPE,
    }

    async with httpx.AsyncClient(
        timeout=30.0,
        verify=gigachat_tls_verify(),
    ) as client:
        response = await client.post(
            settings.GIGACHAT_AUTH_URL,
            headers=headers,
            data=data,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["access_token"]


async def build_catalog_context(db: AsyncSession) -> str:
    category_result = await db.execute(select(Category))
    categories = category_result.scalars().all()

    product_result = await db.execute(select(Product).where(Product.is_active))
    products = product_result.scalars().all()

    category_lines = []
    for category in categories:
        desc = category.description if category.description else "без описания"
        category_lines.append(f"- {category.name}: {desc}")

    category_map = {category.id: category.name for category in categories}

    product_lines = []
    for product in products:
        category_name = category_map.get(product.category_id, "Без категории")
        description = product.description if product.description else "без описания"
        attributes = "; ".join(f"{key}: {value}" for key, value in product.attributes.items())
        product_lines.append(
            f"- {product.name} | цена: {product.price} | остаток: {product.stock} | "
            f"категория: {category_name} | описание: {description} | характеристики: {attributes}"
        )

    categories_text = "\n".join(category_lines) if category_lines else "- Категории отсутствуют"
    products_text = "\n".join(product_lines) if product_lines else "- Товары отсутствуют"

    return f"Контекст каталога:\n\nКатегории:\n{categories_text}\n\nТовары:\n{products_text}\n"


async def get_recent_chat_history(db: AsyncSession, user_id: int, limit: int = 6) -> list[dict]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.id.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    messages = list(reversed(messages))

    return [{"role": msg.role, "content": msg.content} for msg in messages]


async def call_gigachat(
    message: str,
    db: AsyncSession,
    history: list[dict],
) -> str:
    access_token = await get_gigachat_token()
    catalog_context = await build_catalog_context(db)

    combined_system_prompt = f"{SYSTEM_PROMPT}\n\n{catalog_context}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    messages = [
        {"role": "system", "content": combined_system_prompt},
        *history,
        {"role": "user", "content": message},
    ]

    payload = {
        "model": settings.GIGACHAT_MODEL,
        "messages": messages,
        "n": 1,
        "stream": False,
        "max_tokens": 512,
        "repetition_penalty": 1,
    }

    async with httpx.AsyncClient(
        timeout=60.0,
        verify=gigachat_tls_verify(),
    ) as client:
        response = await client.post(
            settings.GIGACHAT_API_URL,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def generate_ai_response(message: str, db: AsyncSession, user_id: int) -> tuple[str, bool]:
    # Only short database operations hold this lock; the external API call does
    # not. Clearing in another tab cannot resurrect an old pending answer.
    await db.scalar(select(User.id).where(User.id == user_id).with_for_update())
    history = await get_recent_chat_history(db, user_id)
    request_message = ChatMessage(user_id=user_id, role="user", content=message)
    db.add(request_message)
    await db.commit()
    blocked = is_blocked_message(message)
    if blocked:
        answer = (
            "Извините, я не могу помогать с опасными, незаконными или вредоносными запросами. "
            "Я могу помочь только с легальными товарами, навигацией по каталогу "
            "и оформлением заказа."
        )
    else:
        try:
            answer = await call_gigachat(message, db, history)
        except Exception:
            logger.exception("GigaChat request failed")
            answer = "ИИ-консультант временно недоступен. Попробуйте отправить сообщение позже."

    await db.scalar(select(User.id).where(User.id == user_id).with_for_update())
    request_exists = await db.scalar(
        select(ChatMessage.id).where(
            ChatMessage.id == request_message.id,
            ChatMessage.user_id == user_id,
        )
    )
    if request_exists is None:
        await db.rollback()
        return "История этого диалога была очищена. Отправьте новый вопрос", False
    db.add(ChatMessage(user_id=user_id, role="assistant", content=answer))
    await db.commit()
    return answer, blocked
