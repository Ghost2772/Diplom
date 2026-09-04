from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Cart(TimestampMixin, Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
