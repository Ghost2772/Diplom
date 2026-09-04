from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class OrderItem(TimestampMixin, Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_order_items_price_nonnegative"),
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint("total_price >= 0", name="ck_order_items_total_nonnegative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )

    product_name = Column(String(150), nullable=False)
    product_sku = Column(String(64), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
