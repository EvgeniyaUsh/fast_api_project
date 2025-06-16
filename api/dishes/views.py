from typing import Union
import math
from sqlalchemy import and_, select, asc, desc, func
from dishes.schemas import Pagination
from core.models import Dish, Tag
from sqlalchemy.orm import joinedload, selectinload
import logging

logger = logging.getLogger("uvicorn.error")


SORTABLE_FIELDS = {
    "CALORIES": Dish.calories,
    "PROTEINS": Dish.proteins,
    "FATS": Dish.fats,
    "CARBOHYDRATES": Dish.carbohydrates,
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
    ) -> Dish:
        created_dish = Dish(
            name=name,
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
        logger.info(f"Created dish - {created_dish.name}")
        return created_dish

    async def get_dish_by_id(self, id: int) -> Union[int, None]:
        query = select(Dish).where(Dish.id == id)

        result = await self.db_session.execute(query)
        dish = result.fetchone()
        if dish:
            return dish[0]

    async def get_dish_by_name_and_calories(self, name, calories):
        query = select(Dish).where(and_(Dish.name == name, Dish.calories == calories))
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

        sort_column = SORTABLE_FIELDS.get(nutrition_sort, Dish.calories)
        order_by = desc(sort_column) if sort_order == "DESCENDING" else asc(sort_column)

        query = (
            select(Dish)
            .options(selectinload(Dish.tags))
            .where(Dish.type == type)
            .order_by(order_by)
            .offset(offset)
            .limit(size)
        )

        # Подсчёт общего количества блюд по запросу
        count_query = select(Dish.id).where(Dish.type == type)

        if tags:
            query = query.where(Dish.tags.any(Tag.name.in_(tags)))

            count_query = count_query.where(Dish.tags.any(Tag.name.in_(tags)))

        dishes_result = await self.db_session.scalars(query)
        dishes = dishes_result.all()

        count_query = select(func.count()).select_from(count_query.subquery())

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
