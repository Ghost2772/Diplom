from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemResponse, CartResponse

router = APIRouter(prefix="/cart", tags=["Cart"])


async def get_or_create_cart(db: AsyncSession, user_id: int) -> Cart:
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items))
    )
    cart = result.scalar_one_or_none()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    return cart


@router.post("/items")
async def add_to_cart(
    item_data: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if item_data.quantity < 1:
        raise HTTPException(status_code=400, detail="Количество должно быть больше 0")

    result = await db.execute(select(Product).where(Product.id == item_data.product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    if not product.is_active:
        raise HTTPException(status_code=400, detail="Товар недоступен")

    cart = await get_or_create_cart(db, current_user.id)

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item_data.product_id
        )
    )
    existing_item = result.scalar_one_or_none()

    if existing_item:
        existing_item.quantity += item_data.quantity
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        db.add(new_item)

    await db.commit()

    return {"message": "Товар добавлен в корзину"}
    

@router.get("", response_model=CartResponse)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == current_user.id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
    )
    cart = result.scalar_one_or_none()

    if not cart:
        return CartResponse(
            id=0,
            user_id=current_user.id,
            items=[],
            total_amount=Decimal("0.00")
        )

    items_response = []
    total_amount = Decimal("0.00")

    for item in cart.items:
        item_total = Decimal(item.product.price) * item.quantity
        total_amount += item_total

        items_response.append(
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                price=Decimal(item.product.price),
                quantity=item.quantity,
                total_price=item_total
            )
        )

    return CartResponse(
        id=cart.id,
        user_id=current_user.id,
        items=items_response,
        total_amount=total_amount
    )


@router.delete("/items/{item_id}")
async def remove_cart_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CartItem)
        .join(Cart, Cart.id == CartItem.cart_id)
        .where(CartItem.id == item_id, Cart.user_id == current_user.id)
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Позиция корзины не найдена")

    await db.delete(cart_item)
    await db.commit()

    return {"message": "Позиция удалена из корзины"}


@router.delete("")
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()

    if not cart:
        return {"message": "Корзина уже пуста"}

    result = await db.execute(select(CartItem).where(CartItem.cart_id == cart.id))
    items = result.scalars().all()

    for item in items:
        await db.delete(item)

    await db.commit()

    return {"message": "Корзина очищена"}