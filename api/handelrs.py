from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import CreateUser, ShowUser, UpdateUser, UserID
from db.dals import UserDAL
from db.session import get_db
from hashing import Hasher

user_router = APIRouter()


async def _create_user(body: CreateUser, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
                hashed_password=Hasher.get_password_hash(body.password),
            )
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )


async def _delete_user(user_id: UUID, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user_id = await user_dal.delete_user(user_id=user_id)
            return user_id


async def _update_user(user_id: UUID, body: UUID, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user_id = await user_dal.update_user(user_id, **body)
            return user_id


async def _get_user_by_id(user_id: UUID, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.get_user_by_id(user_id=user_id)
            if user is not None:
                return ShowUser(
                    user_id=user.user_id,
                    name=user.name,
                    surname=user.surname,
                    email=user.email,
                    is_active=user.is_active,
                )


@user_router.post("/", response_model=ShowUser)
async def create_user(body: CreateUser, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        user = await _create_user(body, db)
    except:
        raise HTTPException(status_code=404, detail="User doesn't create.")
    return user


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)) -> ShowUser:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail="User with id: {user_id} not found."
        )
    return user


@user_router.delete("/", response_model=UserID)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> UserID:
    result = await _delete_user(user_id, db)
    if result is None:
        raise HTTPException(
            status_code=404, detail="User with id: {user_id} not found."
        )
    return UserID(user_id=user_id)


@user_router.patch("/", response_model=UserID)
async def update_user(
    user_id: UUID, body: UpdateUser, db: AsyncSession = Depends(get_db)
) -> UserID:
    body = body.model_dump(exclude_none=True)
    if not body:
        raise HTTPException(status_code=404, detail="Fields for changes are empty.")

    result = await _update_user(user_id, body, db)
    if result is None:
        raise HTTPException(
            status_code=404, detail="User with id: {user_id} not found."
        )
    return UserID(user_id=user_id)
