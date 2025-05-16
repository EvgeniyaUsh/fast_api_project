from typing import Union
from uuid import UUID

from sqlalchemy import and_, select, update

from db.models import User, Dishes, Tag


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


class DishDAL:
    def __init__(self, db_session):
        self.db_session = db_session

    async def create_dish(
        self,
        name_dish: str,
        description: str,
        calories: float,
        proteins: float,
        fats: float,
        carbohydrates: float,
        type: str,
        tags: list[str],
    ) -> Dishes:
        created_dish = Dishes(
            name_dish=name_dish,
            description=description,
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbohydrates=carbohydrates,
            type=type,
            tags=tags,
        )
        self.db_session.add(created_dish)
        await self.db_session.flush()
        return created_dish

    async def get_dish_by_id(self, id: int) -> Union[int, None]:
        query = select(Dishes).where(Dishes.id == id)

        result = await self.db_session.execute(query)
        dish = result.fetchone()
        if dish:
            return dish[0]


class TagDAL:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_tags_by_ids(self, tags: list[str]) -> Union[int, None]:
        # Получаем теги по id
        tags = select(Tag).where(Tag.name.in_(tags))
        result = await self.db_session.execute(tags)
        return result.scalars().all()
