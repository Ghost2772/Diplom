from pydantic import BaseModel


ALLOWED_ORDER_STATUSES = {
    "created",
    "confirmed",
    "processing",
    "shipped",
    "completed",
    "cancelled",
}


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
    total_price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str