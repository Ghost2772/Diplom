from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(120), nullable=True)
    phone = Column(String(32), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    cart = relationship(
        "Cart",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    orders = relationship("Order", back_populates="user")
    chat_messages = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan",
    )
