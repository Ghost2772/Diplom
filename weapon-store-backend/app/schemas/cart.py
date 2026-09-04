from pydantic import BaseModel, ConfigDict, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=100)


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
    total_price: float


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse]
    total_amount: float
