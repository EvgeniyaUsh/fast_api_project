import logging
from core.models import db_helper


from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession


from api.dishes import crud
from api.dishes.schemas import CreateDish, ShowDishes, PaginatedDishes

logger = logging.getLogger("uvicorn.error")

dish_router = APIRouter()


async def _create_dish(body: CreateDish, session) -> ShowDishes | None:
    created_dish = await crud.get_dish_by_name_and_calories(
        body.name, body.calories, session
    )

    if created_dish:
        return

    # Получаем теги по id
    tags = await crud.get_tags_by_ids(body.tags, session) if body.tags else body.tags

    # logger.info("tag!!!!!", tags)

    dish = await crud.create_dish(
        name=body.name,
        description=body.description,
        calories=body.calories,
        proteins=body.proteins,
        fats=body.fats,
        carbohydrates=body.carbohydrates,
        type=body.type,
        tags=tags,
        user_id=body.user_id,
        session=session,
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
        user_id=dish.user_id,
    )


async def _get_dishes_by_type(
    type, nutrition_sort, tags, sort_order, page, page_size, session
) -> PaginatedDishes | None:
    pagination, dishes = await crud.get_dishes_by_type(
        type, nutrition_sort, tags, sort_order, page, page_size, session
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


@dish_router.get("/", response_model=PaginatedDishes)
async def get_dishes_by_type(
    type: str,
    nutrition_sort: str,
    tags: list[str] = Query(default=[], style="form", explode=True),
    sort_order: str = Query("asc", regex="^(ASCENDING|DESCENDING)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> PaginatedDishes:
    logger.info(
        f"type, nutrition_sort, tags, sort_order, page, page_size, db - {type, nutrition_sort, tags, sort_order, page, page_size}"
    )
    dish = await _get_dishes_by_type(
        type, nutrition_sort, tags, sort_order, page, page_size, session
    )
    logger.info(f"dishdish - {dish}")
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish with id: {id} not found.")
    return dish


@dish_router.post("/", response_model=ShowDishes)
async def create_dish(
    body: CreateDish,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> ShowDishes:
    # try:
    dish = await _create_dish(body, session)
    if not dish:
        raise HTTPException(status_code=404, detail="Such dish already exist.")
    return dish
