from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    slug: str | None = Field(default=None, min_length=2, max_length=180)
    sku: str = Field(..., min_length=2, max_length=64)
    brand: str | None = Field(default=None, max_length=100)
    short_description: str | None = Field(default=None, max_length=300)
    description: str | None = Field(default=None, max_length=5000)
    image_url: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(..., gt=0)
    old_price: Decimal | None = Field(default=None, gt=0)
    stock: int = Field(..., ge=0)
    category_id: int
    attributes: dict[str, str] = Field(default_factory=dict)
    is_active: bool = True
    is_featured: bool = False
    is_regulated: bool = False

    @model_validator(mode="after")
    def validate_old_price(self):
        if self.old_price is not None and self.old_price <= self.price:
            raise ValueError("old_price must be greater than price")
        return self


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    sku: str
    brand: str | None = None
    short_description: str | None = None
    description: str | None = None
    image_url: str | None = None
    price: Decimal
    old_price: Decimal | None = None
    stock: int
    attributes: dict[str, str]
    is_active: bool
    is_featured: bool
    is_regulated: bool
    category_id: int
    created_at: datetime
