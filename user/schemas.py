import re

from typing import Annotated
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
