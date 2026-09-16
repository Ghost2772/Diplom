from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import case, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.category import Category
from app.models.chat_message import ChatMessage
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User

# Serializes admission/cleanup across PostgreSQL workers, not normal user requests.
DEMO_ADMISSION_LOCK = 72490501
DEMO_CLEANUP_GRACE = timedelta(minutes=5)


async def purge_expired_demo_users(db: AsyncSession, now: datetime) -> None:
    # The grace period lets already-running requests (including AI) finish.
    user_ids = select(User.id).where(User.demo_expires_at <= now - DEMO_CLEANUP_GRACE)
    order_ids = select(Order.id).where(Order.user_id.in_(user_ids))
    cart_ids = select(Cart.id).where(Cart.user_id.in_(user_ids))
    # Explicit child deletes respect orders.user_id's RESTRICT foreign key.
    await db.execute(delete(OrderItem).where(OrderItem.order_id.in_(order_ids)))
    await db.execute(delete(CartItem).where(CartItem.cart_id.in_(cart_ids)))
    await db.execute(delete(ChatMessage).where(ChatMessage.user_id.in_(user_ids)))
    await db.execute(delete(Order).where(Order.user_id.in_(user_ids)))
    await db.execute(delete(Cart).where(Cart.user_id.in_(user_ids)))
    await db.execute(delete(User).where(User.id.in_(user_ids)))


async def create_demo_user(db: AsyncSession) -> User:
    if db.get_bind().dialect.name == "postgresql":
        await db.execute(select(func.pg_advisory_xact_lock(DEMO_ADMISSION_LOCK)))

    now = datetime.now(UTC)
    await purge_expired_demo_users(db, now)
    demo_count = await db.scalar(
        select(func.count(User.id)).where(User.demo_expires_at.is_not(None))
    )
    if demo_count >= settings.DEMO_MAX_SESSIONS:
        raise HTTPException(
            status_code=429,
            detail="Все демо-сессии сейчас заняты. Попробуйте войти немного позже",
            headers={"Retry-After": "300"},
        )

    products = list(
        await db.scalars(
            select(Product)
            .join(Category)
            .where(Product.is_active.is_(True), Category.is_active.is_(True), Product.stock > 0)
            .order_by(
                case((Product.sku == "MF-SMO-0001", 0), else_=1),
                Product.id,
            )
            .limit(2)
        )
    )
    if not products:
        raise HTTPException(
            status_code=503,
            detail="Демо-вход временно недоступен: каталог ещё не подготовлен",
        )

    user = User(
        email=f"guest-{uuid4().hex}@demo.mullers.local",
        # Demo users only authenticate through a short-lived token, never a password.
        hashed_password="!",
        full_name="Демо-посетитель",
        is_active=True,
        is_admin=False,
        demo_expires_at=now + timedelta(minutes=settings.DEMO_SESSION_MINUTES),
        created_at=now - timedelta(days=14),
    )
    db.add(user)
    await db.flush()

    cart = Cart(user_id=user.id)
    db.add(cart)
    await db.flush()
    db.add(CartItem(cart_id=cart.id, product_id=products[0].id, quantity=1))

    for index, (status, days_ago) in enumerate((("confirmed", 1), ("completed", 7))):
        product = products[index % len(products)]
        order = Order(
            user_id=user.id,
            total_amount=product.price,
            status=status,
            contact_name=user.full_name,
            customer_comment="Пример заказа для знакомства с проектом",
            created_at=now - timedelta(days=days_ago),
            updated_at=now - timedelta(hours=days_ago),
        )
        db.add(order)
        await db.flush()
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_sku=product.sku,
                price=product.price,
                quantity=1,
                total_price=product.price,
            )
        )

    await db.commit()
    return user
