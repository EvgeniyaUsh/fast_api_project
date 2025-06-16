from typing import Union
import math
from sqlalchemy import and_, select, update, asc, desc, func
from api.models import Pagination
from db.models import User, Dishes, Tag
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger("uvicorn.error")


class UserDAL:
    def __init__(self, db_session):
        self.db_session = db_session

    async def create_user(self, name: str, surname: str, email: str) -> User:
        created_user = User(name=name, surname=surname, email=email)
        self.db_session.add(created_user)
        await self.db_session.flush()
        return created_user

    async def delete_user(self, user_id: int) -> User | None:
        query = (
            update(User)
            .where(and_(User.id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.id)
        )
        result = await self.db_session.execute(query)
        deleted_user_id = result.fetchone()
        if deleted_user_id is not None:
            return deleted_user_id[0]

    async def update_user(self, user_id: int, **kwargs) -> int | None:
        query = (
            update(User)
            .where(and_(User.id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User.id)
        )
        result = await self.db_session.execute(query)
        user_id = result.scalar_one_or_none()
        if user_id is not None:
            return user_id

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).where(and_(User.id == user_id, User.is_active == True))

        result = await self.db_session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            return user

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        user = result.scalar_one_or_none()
        if user is not None:
            return user


SORTABLE_FIELDS = {
    "CALORIES": Dishes.calories,
    "PROTEINS": Dishes.proteins,
    "FATS": Dishes.fats,
    "CARBOHYDRATES": Dishes.carbohydrates,
}


class DishDAL:
    def __init__(self, db_session):
        self.db_session = db_session

    async def create_dish(
        self,
        name: str,
        description: str,
        calories: float,
        proteins: float,
        fats: float,
        carbohydrates: float,
        type: str,
        tags: list[str] | None,
        user_id: int,
    ) -> Dishes:
        created_dish = Dishes(
            name=name,
            description=description,
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbohydrates=carbohydrates,
            type=type,
            tags=tags,
            user_id=user_id,
        )
        self.db_session.add(created_dish)
        await self.db_session.flush()
        logger.info(f"Created dish - {created_dish.name}")
        return created_dish

    async def get_dish_by_id(self, id: int) -> Union[int, None]:
        query = select(Dishes).where(Dishes.id == id)

        result = await self.db_session.execute(query)
        dish = result.fetchone()
        if dish:
            return dish[0]

    async def get_dish_by_name_and_calories(self, name, calories):
        query = select(Dishes).where(
            and_(Dishes.name == name, Dishes.calories == calories)
        )
        result = await self.db_session.execute(query)
        dish = result.fetchone()
        logger.info(f"{dish}")
        if dish:
            return True
        return False

    async def get_dishes_by_type(
        self, type, nutrition_sort, tags, sort_order, page, size
    ):
        offset = (page - 1) * size

        sort_column = SORTABLE_FIELDS.get(nutrition_sort, Dishes.calories)
        order_by = desc(sort_column) if sort_order == "DESCENDING" else asc(sort_column)

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
            # .join(Dishes.tags)  # Добавляем join по тегам для фильтра
            .options(joinedload(Dishes.tags))
            .where(Dishes.type == type)
        )

        if tags:
            query = (
                query.where(Dishes.tags.any(Tag.name.in_(tags)))
                .order_by(order_by)
                .offset(offset)
                .limit(size)
            )

        else:
            query = query.order_by(order_by).offset(offset).limit(size)

        # query = (
        #     select(Dishes)
        #     # .join(Dishes.tags)  # Добавляем join по тегам для фильтра
        #     .options(joinedload(Dishes.tags))
        #     .where(Dishes.type == type)
        #     .where(Dishes.tags.any(Tag.name.in_(tags)))  # фильтр по тегам
        #     .order_by(order_by)
        #     .offset(offset)
        #     .limit(size)
        # )

        # отдельный подсчёт общего количества
        count_query = select(func.count()).select_from(
            select(Dishes).where(Dishes.type == type).subquery()
        )

        query = await self.db_session.execute(query)
        dishes = query.unique().scalars().all()

        count_result = await self.db_session.execute(count_query)
        total = count_result.scalar_one()

        total_pages = math.ceil(total / size)

        pagination = Pagination(
            currentPage=page, totalPages=total_pages, totalEntries=total
        )

        return pagination, dishes


class TagDAL:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_tags_by_ids(self, tags: list[str]) -> list[str] | None:
        # Получаем теги по id
        _tags = select(Tag).where(Tag.name.in_(tags))
        result = await self.db_session.execute(_tags)
        return result.scalars().all()
