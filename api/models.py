import re
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, field_validator

LETTER_MATCH = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class ORNModeModel(BaseModel):
    class Config:
        """Converts orm objects to dictionaries or json."""

        orm_mode = True


class ShowUser(ORNModeModel):
    user_id: uuid.UUID
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
