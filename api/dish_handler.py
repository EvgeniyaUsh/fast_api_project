from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import CreateDish, ShowDishes, PaginatedDishes, Pagination
from db.dals import DishDAL, TagDAL
from db.session import get_db
from fastapi.exceptions import RequestValidationError
from typing import Union
from uuid import UUID

dish_router = APIRouter()


async def _get_dish_by_name_and_calories(name, calories, db):
    async with db as session:
        async with session.begin():
            dish_dal = DishDAL(session)
            create_dish = await dish_dal.get_dish_by_name_and_calories(name, calories)
            return create_dish


async def _create_dish(body: CreateDish, db) -> ShowDishes | None:
    async with db as session:
        async with session.begin():
            dish_dal = DishDAL(session)
            create_dish = await dish_dal.get_dish_by_name_and_calories(
                body.name, body.calories
            )

            if create_dish:
                return

            # Получаем теги по id
            tag_objs = TagDAL(session)

            tags = await tag_objs.get_tags_by_ids(body.tags) if body.tags else body.tags

            dish = await dish_dal.create_dish(
                name=body.name,
                description=body.description,
                calories=body.calories,
                proteins=body.proteins,
                fats=body.fats,
                carbohydrates=body.carbohydrates,
                type=body.type,
                tags=tags,
            )
            return ShowDishes(
                id=dish.id,
                name=dish.name,
                description=dish.description,
                calories=dish.calories,
                proteins=dish.proteins,
                fats=dish.fats,
                carbohydrates=dish.carbohydrates,
                type=dish.type,
                created_at=dish.created_at,
                tags=[tag.name for tag in tags],
            )


async def _get_dish_by_id(id: int, db) -> ShowDishes | None:
    async with db as session:
        async with session.begin():
            dish_dal = DishDAL(session)
            # Получаем теги по id
            tag_objs = TagDAL(session)
            dish = await dish_dal.get_dish_by_id(id=id)
            if dish is not None:
                return ShowDishes(
                    id=dish.id,
                    name=dish.name,
                    description=dish.description,
                    calories=dish.calories,
                    proteins=dish.proteins,
                    fats=dish.fats,
                    carbohydrates=dish.carbohydrates,
                    type=dish.type,
                    created_at=dish.created_at,
                    tags=dish.tags,
                )


async def _get_dishes_by_type(
    type, nutrition_sort, tags, sort_order, page, page_size, db
) -> PaginatedDishes | None:
    async with db as session:
        async with session.begin():
            dish_dal = DishDAL(session)
            pagination, dishes = await dish_dal.get_dishes_by_type(
                type, nutrition_sort, tags, sort_order, page, page_size
            )
            if dishes is not None:
                return PaginatedDishes(
                    pagination=pagination,
                    dishes=[
                        ShowDishes.model_validate(
                            {**d.__dict__, "tags": [tag.name for tag in d.tags]},
                            from_attributes=True,
                        )
                        for d in dishes
                    ],
                )


@dish_router.post("/", response_model=ShowDishes)
async def create_user(
    body: CreateDish, db: AsyncSession = Depends(get_db)
) -> ShowDishes:
    # try:
    dish = await _create_dish(body, db)
    if not dish:
        raise HTTPException(status_code=404, detail="Such dish already exist.")
    return dish


# @dish_router.get("/", response_model=ShowDishes)
# async def get_user_by_id(id: int, db: AsyncSession = Depends(get_db)) -> ShowDishes:
#     dish = await _get_dish_by_id(id, db)
#     if dish is None:
#         raise HTTPException(status_code=404, detail="Dish with id: {id} not found.")
#     return dish


@dish_router.get("/", response_model=PaginatedDishes)
async def get_dishes_by_type(
    type: str,
    nutrition_sort: str,
    tags: list[str] = Query(default=[], style="form", explode=True),
    sort_order: str = Query("asc", regex="^(ASCENDING|DESCENDING)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedDishes:
    dish = await _get_dishes_by_type(
        type, nutrition_sort, tags, sort_order, page, page_size, db
    )
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish with id: {id} not found.")
    return dish
