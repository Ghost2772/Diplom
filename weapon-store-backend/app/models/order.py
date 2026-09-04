import uuid

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


def generate_order_number() -> str:
    return f"MF-{uuid.uuid4().hex[:10].upper()}"


class Order(TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (CheckConstraint("total_amount >= 0", name="ck_orders_total_nonnegative"),)

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
        default=generate_order_number,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(32), nullable=False, default="created", index=True)
    contact_name = Column(String(120), nullable=True)
    contact_phone = Column(String(32), nullable=True)
    delivery_address = Column(Text, nullable=True)
    customer_comment = Column(Text, nullable=True)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
