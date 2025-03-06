import settings
from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from pydantic import BaseModel, EmailStr, field_validator
import re

# create async engine for interaction with database
engine = create_async_engine(settings.PROJECT_DATABESE_URL, future=True, echo=True)

# create session for the interaction with database
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)


class UserDAL:
    def __init__(self, db_session):
        self.db_session = db_session

    async def create_user(self, name, surname, email):
        created_user = User(name=name, surname=surname, email=email)
        self.db_session.add(created_user)
        await self.db_session.flush()
        return created_user


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


app = FastAPI(title="fastapi_project")

user_router = APIRouter()


async def _create_user(body: CreateUser) -> ShowUser:
    async with async_session() as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                name=body.name, surname=body.surname, email=body.email
            )
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )


@user_router.post("/", response_model=ShowUser)
async def create_user(body: CreateUser) -> ShowUser:
    return await _create_user(body)


main_router = APIRouter()
main_router.include_router(user_router, prefix="/user", tags=["user"])

app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
