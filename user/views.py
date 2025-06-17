from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from user.schemas import CreateUser, ShowUser


from core.models import db_helper
from user import crud

user_router = APIRouter()


async def _create_user(body: CreateUser, session) -> ShowUser:
    user = await crud.create_user(
        name=body.name, surname=body.surname, email=body.email, session=session
    )
    return ShowUser(
        id=user.id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        is_active=user.is_active,
    )


async def _get_user_by_id(user_id: int, session) -> ShowUser | None:
    user = await crud.get_user_by_id(user_id=user_id, session=session)
    if user is not None:
        return ShowUser(
            id=user.id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


@user_router.post("/", response_model=ShowUser)
async def create_user(
    body: CreateUser,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> ShowUser:
    try:
        user = await _create_user(body, session)
    except:
        raise HTTPException(status_code=404, detail="User doesn't create.")
    return user


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
    user_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)
) -> ShowUser:
    user = await _get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(
            status_code=404, detail="User with id: {user_id} not found."
        )
    return user


# @user_router.delete("/", response_model=UserID)
# async def delete_user(user_id: UUID, session: AsyncSession = Depends(db_helper.scoped_session_dependency),) -> UserID:
#     result = await crud.delete_user(user_id, db)
#     if result is None:
#         raise HTTPException(
#             status_code=404, detail="User with id: {user_id} not found."
#         )
#     return UserID(user_id=user_id)


# @user_router.patch("/", response_model=UserID)
# async def update_user(
#     user_id: UUID, body: UpdateUser, session: AsyncSession = Depends(db_helper.scoped_session_dependency),
# ) -> UserID:
#     body = body.model_dump(exclude_none=True)
#     if not body:
#         raise HTTPException(status_code=404, detail="Fields for changes are empty.")

#     result = await await crud.update_user(user_id, session, **body)
#     if result is None:
#         raise HTTPException(
#             status_code=404, detail="User with id: {user_id} not found."
#         )
#     return UserID(user_id=user_id)
