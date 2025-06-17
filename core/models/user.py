from sqlalchemy import (
    String,
)

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from core.models.base import Base

if TYPE_CHECKING:
    from .dish import Dish


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    dishes: Mapped[list["Dish"]] = relationship(back_populates="user")
