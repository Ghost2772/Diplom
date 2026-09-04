from datetime import datetime

from pydantic import BaseModel, ConfigDict

ALLOWED_ORDER_STATUSES = {
    "created",
    "confirmed",
    "processing",
    "shipped",
    "completed",
    "cancelled",
}


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int | None
    product_name: str
    product_sku: str | None = None
    price: float
    quantity: int
    total_price: float
    created_at: datetime


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    user_id: int
    total_amount: float
    status: str
    contact_name: str | None = None
    contact_phone: str | None = None
    delivery_address: str | None = None
    customer_comment: str | None = None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]


class OrderStatusUpdate(BaseModel):
    status: str
