from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin_user
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.user import User
from app.schemas.order import (
    OrderResponse,
    OrderItemResponse,
    OrderStatusUpdate,
    ALLOWED_ORDER_STATUSES,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/create-from-cart", response_model=OrderResponse)
async def create_order_from_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == current_user.id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
    )
    cart = result.scalar_one_or_none()

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    total_amount = Decimal("0.00")

    order = Order(
        user_id=current_user.id,
        total_amount=Decimal("0.00"),
        status="created"
    )
    db.add(order)
    await db.flush()

    for item in cart.items:
        item_total = Decimal(item.product.price) * item.quantity
        total_amount += item_total

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product.name,
            price=Decimal(item.product.price),
            quantity=item.quantity,
            total_price=item_total
        )
        db.add(order_item)

    order.total_amount = total_amount

    for item in cart.items:
        await db.delete(item)

    await db.commit()

    result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.items))
    )
    created_order = result.scalar_one()

    return OrderResponse(
        id=created_order.id,
        user_id=created_order.user_id,
        total_amount=float(created_order.total_amount),
        status=created_order.status,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                price=float(item.price),
                quantity=item.quantity,
                total_price=float(item.total_price)
            )
            for item in created_order.items
        ]
    )


@router.get("/my", response_model=list[OrderResponse])
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .options(selectinload(Order.items))
    )
    orders = result.scalars().all()

    return [
        OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_amount=float(order.total_amount),
            status=order.status,
            items=[
                OrderItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    price=float(item.price),
                    quantity=item.quantity,
                    total_price=float(item.total_price)
                )
                for item in order.items
            ]
        )
        for order in orders
    ]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав доступа")

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        total_amount=float(order.total_amount),
        status=order.status,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                price=float(item.price),
                quantity=item.quantity,
                total_price=float(item.total_price)
            )
            for item in order.items
        ]
    )


@router.get("", response_model=list[OrderResponse])
async def get_all_orders(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    result = await db.execute(
        select(Order).options(selectinload(Order.items))
    )
    orders = result.scalars().all()

    return [
        OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_amount=float(order.total_amount),
            status=order.status,
            items=[
                OrderItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    price=float(item.price),
                    quantity=item.quantity,
                    total_price=float(item.total_price)
                )
                for item in order.items
            ]
        )
        for order in orders
    ]


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    if status_data.status not in ALLOWED_ORDER_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый статус. Разрешены: {', '.join(ALLOWED_ORDER_STATUSES)}"
        )

    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    order.status = status_data.status
    await db.commit()
    await db.refresh(order)

    result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.items))
    )
    updated_order = result.scalar_one()

    return OrderResponse(
        id=updated_order.id,
        user_id=updated_order.user_id,
        total_amount=float(updated_order.total_amount),
        status=updated_order.status,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                price=float(item.price),
                quantity=item.quantity,
                total_price=float(item.total_price)
            )
            for item in updated_order.items
        ]
    )