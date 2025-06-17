from sqlalchemy.orm import joinedload, selectinload
import math
from sqlalchemy import and_, select, asc, desc, func
from api.dishes.schemas import Pagination
from core.models import Dish, Tag


import logging

logger = logging.getLogger("uvicorn.error")


SORTABLE_FIELDS = {
    "CALORIES": Dish.calories,
    "PROTEINS": Dish.proteins,
    "FATS": Dish.fats,
    "CARBOHYDRATES": Dish.carbohydrates,
}


async def get_dish_by_name_and_calories(name, calories, session):
    query = select(Dish).where(and_(Dish.name == name, Dish.calories == calories))
    result = await session.execute(query)
    dish = result.fetchone()
    logger.info(f"{dish}")
    if dish:
        return True
    return False


async def get_tags_by_ids(tags: list[str], session) -> list[Tag] | None:
    # Получаем теги по id
    _tags = select(Tag).where(Tag.name.in_(tags))
    result = await session.execute(_tags)
    return result.scalars().all()


async def create_dish(
    name: str,
    description: str,
    calories: float,
    proteins: float,
    fats: float,
    carbohydrates: float,
    type: str,
    tags: list[Tag] | None,
    user_id: int,
    session,
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
        user_id=user_id,
    )
    session.add(created_dish)
    await session.commit()
    logger.info(f"Created dish - {created_dish.name}")
    return created_dish


async def get_dishes_by_type(
    type, nutrition_sort, tags, sort_order, page, size, session
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

    dishes_result = await session.scalars(query)
    dishes = dishes_result.all()

    count_query = select(func.count()).select_from(count_query.subquery())

    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    total_pages = math.ceil(total / size)

    pagination = Pagination(
        currentPage=page, totalPages=total_pages, totalEntries=total
    )

    return pagination, dishes
