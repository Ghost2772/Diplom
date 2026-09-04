from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class CartItem(TimestampMixin, Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_items_cart_product"),
        CheckConstraint("quantity > 0", name="ck_cart_items_quantity_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(
        Integer,
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
