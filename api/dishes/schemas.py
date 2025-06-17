from typing import Annotated, List
from datetime import datetime


from pydantic import (
    BaseModel,
    StringConstraints,
)


class CreateDish(BaseModel):
    name: str
    description: str
    calories: float
    proteins: float
    fats: float
    carbohydrates: float
    type: str
    tags: List[str] = []
    user_id: int


class ShowDishes(BaseModel):
    id: int | None
    name: Annotated[str, StringConstraints(min_length=2, max_length=50)]
    description: str
    calories: float
    proteins: float
    fats: float
    carbohydrates: float
    type: str
    created_at: datetime
    tags: List[str] = []
    user_id: int

    model_config = {"from_attributes": True}


class Pagination(BaseModel):
    currentPage: int
    totalPages: int
    totalEntries: int


class PaginatedDishes(BaseModel):
    pagination: Pagination
    dishes: List[ShowDishes]

    model_config = {"from_attributes": True}
