from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price > 0", name="ck_products_price_positive"),
        CheckConstraint("old_price IS NULL OR old_price > price", name="ck_products_old_price"),
        CheckConstraint("stock >= 0", name="ck_products_stock_nonnegative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    slug = Column(String(180), unique=True, nullable=False, index=True)
    sku = Column(String(64), unique=True, nullable=False, index=True)
    brand = Column(String(100), nullable=True, index=True)
    short_description = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    old_price = Column(Numeric(10, 2), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    attributes = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    is_regulated = Column(Boolean, nullable=False, default=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    category = relationship("Category", back_populates="products")
