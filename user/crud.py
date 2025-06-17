from typing import Union
import math
from sqlalchemy import and_, select, update, asc, desc, func
from api.models import Pagination
from db.models import User, Dishes, Tag
from sqlalchemy.orm import joinedload, selectinload
import logging

logger = logging.getLogger("uvicorn.error")


async def create_user(name: str, surname: str, email: str, session) -> User:
    created_user = User(name=name, surname=surname, email=email)
    session.add(created_user)
    await session.commit()
    return created_user


async def delete_user(user_id: int, session) -> User | None:
    query = (
        update(User)
        .where(and_(User.id == user_id, User.is_active == True))
        .values(is_active=False)
        .returning(User.id)
    )
    result = await session.execute(query)
    deleted_user_id = result.fetchone()
    if deleted_user_id is not None:
        return deleted_user_id[0]


async def update_user(user_id: int, session, **kwargs) -> int | None:
    query = (
        update(User)
        .where(and_(User.id == user_id, User.is_active == True))
        .values(kwargs)
        .returning(User.id)
    )
    result = await session.execute(query)
    user_id = result.scalar_one_or_none()
    if user_id is not None:
        return user_id


async def get_user_by_id(user_id: int, session) -> User | None:
    query = select(User).where(and_(User.id == user_id, User.is_active == True))

    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user:
        return user


async def get_user_by_email(self, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await self.db_session.execute(query)
    user = result.scalar_one_or_none()
    if user is not None:
        return user
