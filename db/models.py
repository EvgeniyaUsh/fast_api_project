from sqlalchemy import (
    Boolean,
    Column,
    String,
    Integer,
    Text,
    Float,
    DateTime,
    func,
    Table,
    ForeignKey,
)
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
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


class Dishes(Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
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
