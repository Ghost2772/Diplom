from decimal import Decimal
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category_id: int
    is_active: bool = True


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: Decimal
    stock: int
    is_active: bool
    category_id: int

    class Config:
        from_attributes = True