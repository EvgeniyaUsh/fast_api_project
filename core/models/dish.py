from models.base import Base
from sqlalchemy import (
    Column,
    Text,
    Float,
    Table,
    ForeignKey,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
import sqlalchemy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user import User


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

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Text] = mapped_column(nullable=False)

    calories: Mapped[Float] = mapped_column(nullable=False)

    proteins: Mapped[Float] = mapped_column(nullable=False)
    fats: Mapped[Float] = mapped_column(nullable=False)
    carbohydrates: Mapped[Float] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)

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
