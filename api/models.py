import re
from typing import Annotated, List
from datetime import datetime

from fastapi import HTTPException
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
    ConfigDict,
)

LETTER_MATCH = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class ORNModeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ShowUser(ORNModeModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class CreateUser(BaseModel):
    name: str
    surname: str
    email: EmailStr

    @field_validator("name")
    def validate_name(cls, val):
        if not LETTER_MATCH.match(val):
            raise HTTPException(
                status_code=422, detail="Name contains invalid characters."
            )
        return val

    @field_validator("surname")
    def validate_surname(cls, val):
        if not LETTER_MATCH.match(val):
            raise HTTPException(
                status_code=422, detail="Surname contains invalid characters."
            )
        return val


class CreateTag(ORNModeModel):
    name: str


class ShowTag(ORNModeModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


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


class Token(BaseModel):
    access_token: str
    token_type: str


class UpdateUser(BaseModel):
    name: Annotated[str | None, StringConstraints(min_length=2), Field(None)]
    surname: Annotated[str | None, StringConstraints(min_length=2), Field(None)]
    email: Annotated[EmailStr | None, Field(None)]

    @field_validator("name")
    def validate_name(cls, val):
        if not LETTER_MATCH.match(val):
            raise HTTPException(
                status_code=422, detail="Name contains invalid characters."
            )
        return val

    @field_validator("surname")
    def validate_surname(cls, val):
        if not LETTER_MATCH.match(val):
            raise HTTPException(
                status_code=422, detail="Surname contains invalid characters."
            )
        return val
