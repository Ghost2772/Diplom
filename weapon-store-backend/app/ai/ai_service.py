import uuid

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.guard import is_blocked_message
from app.core.config import settings
from app.models.category import Category
from app.models.product import Product
from app.models.chat_message import ChatMessage


SYSTEM_PROMPT = (
    "Ты ИИ-консультант интернет-магазина регулируемых товаров. "
    "Отвечай только по данным, переданным в контексте. "
    "Если данных недостаточно, честно скажи, что информации в каталоге сейчас нет. "
    "Не придумывай товары, категории, цены, характеристики и наличие. "
    "Помогай с навигацией по каталогу, оформлением заказа, статусами заказа и общими легальными вопросами о покупке. "
    "Не давай инструкции по незаконному, опасному, вредоносному использованию, обходу закона, скрытому применению, "
    "переделке или модификации товаров."
)


async def get_gigachat_token() -> str:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {settings.GIGACHAT_AUTH_KEY}",
    }

    data = {
        "scope": settings.GIGACHAT_SCOPE,
    }

    async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
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

    product_result = await db.execute(select(Product).where(Product.is_active == True))
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
        product_lines.append(
            f"- {product.name} | цена: {product.price} | остаток: {product.stock} | "
            f"категория: {category_name} | описание: {description}"
        )

    categories_text = "\n".join(category_lines) if category_lines else "- Категории отсутствуют"
    products_text = "\n".join(product_lines) if product_lines else "- Товары отсутствуют"

    return (
        "Контекст каталога:\n\n"
        "Категории:\n"
        f"{categories_text}\n\n"
        "Товары:\n"
        f"{products_text}\n"
    )


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


async def save_chat_message(db: AsyncSession, user_id: int, role: str, content: str):
    message = ChatMessage(
        user_id=user_id,
        role=role,
        content=content
    )
    db.add(message)
    await db.commit()


async def call_gigachat(message: str, db: AsyncSession, user_id: int) -> str:
    access_token = await get_gigachat_token()
    catalog_context = await build_catalog_context(db)
    history = await get_recent_chat_history(db, user_id)

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

    async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
        response = await client.post(
            settings.GIGACHAT_API_URL,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def generate_ai_response(message: str, db: AsyncSession, user_id: int) -> tuple[str, bool]:
    if is_blocked_message(message):
        blocked_answer = (
            "Извините, я не могу помогать с опасными, незаконными или вредоносными запросами. "
            "Я могу помочь только с легальными товарами, навигацией по каталогу и оформлением заказа."
        )
        await save_chat_message(db, user_id, "user", message)
        await save_chat_message(db, user_id, "assistant", blocked_answer)
        return blocked_answer, True

    try:
        await save_chat_message(db, user_id, "user", message)
        answer = await call_gigachat(message, db, user_id)
        await save_chat_message(db, user_id, "assistant", answer)
        return answer, False
    except Exception as e:
        error_answer = f"Ошибка AI-сервиса: {str(e)}"
        await save_chat_message(db, user_id, "assistant", error_answer)
        return error_answer, False