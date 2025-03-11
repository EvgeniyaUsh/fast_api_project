from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import settings

# create async engine for interaction with database
engine = create_async_engine(settings.PROJECT_DATABESE_URL, future=True, echo=True)

# create session for the interaction with database
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    """Dependency for getting async session."""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
