import uuid

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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)
    hashed_password = Column(String, nullable=False)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


dishes_tags = Table(
    "dishes_tags",
    Base.metadata,
    Column("dish_id", ForeignKey("dishes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Dishes(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    calories = Column(Float, nullable=False)

    proteins = Column(Float, nullable=False)
    fats = Column(Float, nullable=False)
    carbohydrates = Column(Float, nullable=False)
    type = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    tags = relationship("Tag", secondary=dishes_tags, backref="dishes")
