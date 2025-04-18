from typing import Union
from uuid import UUID

from sqlalchemy import and_, select, update

from db.models import User


class UserDAL:
    def __init__(self, db_session):
        self.db_session = db_session

    async def create_user(
        self, name: str, surname: str, email: str, hashed_password: str
    ) -> User:
        created_user = User(
            name=name, surname=surname, email=email, hashed_password=hashed_password
        )
        self.db_session.add(created_user)
        await self.db_session.flush()
        return created_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        result = await self.db_session.execute(query)
        deleted_user_id = result.fetchone()
        if deleted_user_id is not None:
            return deleted_user_id[0]

    async def update_user(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(user_id == User.user_id, User.is_active == True))
            .values(kwargs)
            .returning(User.user_id)
        )
        result = await self.db_session.execute(query)
        user_id = result.fetchone()
        if user_id is not None:
            return user_id[0]

    async def get_user_by_id(self, user_id: UUID) -> Union[UUID, None]:
        query = select(User).where(
            and_(User.user_id == user_id, User.is_active == True)
        )

        result = await self.db_session.execute(query)
        user = result.fetchone()
        if user:
            return user[0]

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]
