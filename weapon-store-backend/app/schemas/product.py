from datetime import datetime
from decimal import Decimal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ProductCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=2, max_length=150)
    slug: str | None = Field(default=None, min_length=2, max_length=180)
    sku: str = Field(..., min_length=2, max_length=64)
    brand: str | None = Field(default=None, max_length=100)
    short_description: str | None = Field(default=None, max_length=300)
    description: str | None = Field(default=None, max_length=5000)
    image_url: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    old_price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(..., ge=0, le=2147483647)
    category_id: int = Field(..., gt=0)
    attributes: dict[str, str] = Field(default_factory=dict)
    is_active: bool = True
    is_featured: bool = False
    is_regulated: bool = False

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, value: str | None) -> str | None:
        if not value:
            return None
        parsed = urlsplit(value)
        local_path = value.startswith("/") and not value.startswith("//")
        web_url = parsed.scheme in {"http", "https"} and bool(parsed.hostname)
        if "\\" in value or any(char.isspace() for char in value) or not (local_path or web_url):
            raise ValueError("Укажите ссылку http(s) или путь к изображению на сайте")
        return value

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, value: dict[str, str]) -> dict[str, str]:
        if len(value) > 40:
            raise ValueError("Допускается не более 40 характеристик")
        cleaned = {}
        for key, item in value.items():
            key, item = key.strip(), item.strip()
            if not key or not item or len(key) > 80 or len(item) > 240:
                raise ValueError("Заполните название (до 80 символов) и значение (до 240)")
            if key.casefold() in {existing.casefold() for existing in cleaned}:
                raise ValueError("Названия характеристик не должны повторяться")
            cleaned[key] = item
        return cleaned

    @model_validator(mode="after")
    def validate_old_price(self):
        if self.old_price is not None and self.old_price <= self.price:
            raise ValueError("Старая цена должна быть больше текущей")
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
