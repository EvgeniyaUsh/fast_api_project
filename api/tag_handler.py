from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import CreateTag, ShowTag
from db.dals import DishDAL, TagDAL
from db.session import get_db

from typing import Union
from uuid import UUID

tag_router = APIRouter()


async def _create_tag(body: CreateTag, db) -> ShowTag:
    async with db as session:
        async with session.begin():
            dish_dal = DishDAL(session)
            # Получаем теги по id
            tag_objs = TagDAL(session)

            dish = await dish_dal.create_dish(
                name=body.name,
                description=body.description,
                calories=body.calories,
                proteins=body.proteins,
                fats=body.fats,
                carbohydrates=body.carbohydrates,
                type=body.type,
                tags=tag_objs,
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
                tags=[ShowTag.from_orm(tag) for tag in tag_objs],
            )


async def _get_dish_by_id(id: int, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            dish_dal = DishDAL(session)
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
                )


@dish_router.post("/", response_model=ShowDishes)
async def create_user(
    body: CreateDish, db: AsyncSession = Depends(get_db)
) -> ShowDishes:
    try:
        user = await _create_dish(body, db)
    except:
        raise HTTPException(status_code=404, detail="Dish doesn't create.")
    return user


@dish_router.get("/", response_model=ShowDishes)
async def get_user_by_id(id: int, db: AsyncSession = Depends(get_db)) -> ShowDishes:
    dish = await _get_dish_by_id(id, db)
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish with id: {id} not found.")
    return dish
