from core.models.base import Base
from sqlalchemy import Column, Text, Float, Table, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
import sqlalchemy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Tag(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at = mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.sql.func.now(),
    )


dishes_tags = Table(
    "dishes_tags",
    Base.metadata,
    Column("dish_id", ForeignKey("dishes.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Dish(Base):
    __tablename__ = "dishes"

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)

    calories: Mapped[float] = mapped_column(Float(precision=2))
    proteins: Mapped[float] = mapped_column(Float(precision=2))
    fats: Mapped[float] = mapped_column(Float(precision=2))
    carbohydrates: Mapped[float] = mapped_column(Float(precision=2))
    type: Mapped[str]

    created_at = mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.sql.func.now(),
        index=True,
    )
    updated_at = mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.sql.func.now(),
    )

    tags = relationship("Tag", secondary=dishes_tags, backref="dishes")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="dishes") 
