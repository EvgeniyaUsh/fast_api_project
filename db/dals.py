from typing import Union
from uuid import UUID

from sqlalchemy import and_, select, update, asc, desc, func

from db.models import User, Dishes, Tag
from sqlalchemy.orm import joinedload


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


SORTABLE_FIELDS = {
    "calories": Dishes.calories,
    "protein": Dishes.proteins,
    "fat": Dishes.fats,
    "carbs": Dishes.carbohydrates,
}


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

    async def get_dishes_by_type(
        self, type, sort_by, tags, sort_order, page, size
    ) -> Union[int, None]:
        offset = (page - 1) * size

        sort_column = SORTABLE_FIELDS.get(sort_by, Dishes.calories)
        order_by = desc(sort_column) if sort_order == "desc" else asc(sort_column)

        # # базовый select
        # query = (
        #     select(Dishes)
        #     .options(joinedload(Dishes.tags))
        #     .where(Dishes.type == type)
        #     .order_by(order_by)
        #     .offset(offset)
        #     .limit(size)
        # )

        query = (
            select(Dishes)
            .join(Dishes.tags)  # Добавляем join по тегам для фильтра
            .options(joinedload(Dishes.tags))
            .where(Dishes.type == type)
            .where(Dishes.tags.any(Tag.name.in_(tags)))  # фильтр по тегам
            .order_by(order_by)
            .offset(offset)
            .limit(size)
        )

        # отдельный подсчёт общего количества
        count_query = select(func.count()).select_from(
            select(Dishes).where(Dishes.type == type).subquery()
        )

        query = await self.db_session.execute(query)
        dishes = query.unique().scalars().all()

        count_result = await self.db_session.execute(count_query)
        total = count_result.scalar_one()

        return total, page, size, dishes


class TagDAL:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_tags_by_ids(self, tags: list[str]) -> Union[int, None]:
        # Получаем теги по id
        tags = select(Tag).where(Tag.name.in_(tags))
        result = await self.db_session.execute(tags)
        return result.scalars().all()
