from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from collections.abc import AsyncGenerator

import settings

# create async engine for interaction with database
engine = create_async_engine(settings.PROJECT_DATABESE_URL, future=True, echo=True)


# create session for the interaction with database
async_session = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
