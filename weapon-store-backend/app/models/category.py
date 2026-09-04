from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Category(TimestampMixin, Base):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint("display_order >= 0", name="ck_categories_display_order_nonnegative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)

    products = relationship("Product", back_populates="category")
