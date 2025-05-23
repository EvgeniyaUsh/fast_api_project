from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import CreateDish, ShowDishes, ShowTag, PaginatedDishes
from db.dals import DishDAL, TagDAL
from db.session import get_db
from db.models import Dishes

from typing import Union
from uuid import UUID

dish_router = APIRouter()


async def _create_dish(body: CreateDish, db) -> ShowDishes:
    async with db as session:
        async with session.begin():
            dish_dal = DishDAL(session)
            # Получаем теги по id
            tag_objs = TagDAL(session)
            tags = await tag_objs.get_tags_by_ids(body.tags)

            dish = await dish_dal.create_dish(
                name_dish=body.name_dish,
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
                name_dish=dish.name_dish,
                description=dish.description,
                calories=dish.calories,
                proteins=dish.proteins,
                fats=dish.fats,
                carbohydrates=dish.carbohydrates,
                type=dish.type,
                tags=[tag.name for tag in dish.tags],
            )


async def _get_dish_by_id(id: int, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            dish_dal = DishDAL(session)
            # Получаем теги по id
            tag_objs = TagDAL(session)
            dish = await dish_dal.get_dish_by_id(id=id)
            if dish is not None:
                return ShowDishes(
                    id=dish.id,
                    name_dish=dish.name_dish,
                    description=dish.description,
                    calories=dish.calories,
                    proteins=dish.proteins,
                    fats=dish.fats,
                    carbohydrates=dish.carbohydrates,
                    type=dish.type,
                    tags=dish.tags,
                )


async def _get_dishes_by_type(
    type, sort_by, tags, sort_order, page, size, db
) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            dish_dal = DishDAL(session)
            total, page, size, dishes = await dish_dal.get_dishes_by_type(
                type, sort_by, tags, sort_order, page, size
            )
            if dishes is not None:
                return PaginatedDishes(
                    total=total,
                    page=page,
                    size=size,
                    dishes=[
                        ShowDishes.model_validate(d, from_attributes=True)
                        for d in dishes
                    ],
                )


@dish_router.post("/", response_model=ShowDishes)
async def create_user(
    body: CreateDish, db: AsyncSession = Depends(get_db)
) -> ShowDishes:
    # try:
    user = await _create_dish(body, db)
    print(f"bodybody - {body}")
    # except:
    #     raise HTTPException(status_code=404, detail="Dish doesn't create.")
    return user


# @dish_router.get("/", response_model=ShowDishes)
# async def get_user_by_id(id: int, db: AsyncSession = Depends(get_db)) -> ShowDishes:
#     dish = await _get_dish_by_id(id, db)
#     if dish is None:
#         raise HTTPException(status_code=404, detail="Dish with id: {id} not found.")
#     return dish


@dish_router.get("/", response_model=PaginatedDishes)
async def get_dishes_by_type(
    type: str,
    sort_by: str,
    tags: list[str] = Query(default=[], style="form", explode=True),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedDishes:
    dish = await _get_dishes_by_type(type, sort_by, tags, sort_order, page, size, db)
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish with id: {id} not found.")
    return dish
