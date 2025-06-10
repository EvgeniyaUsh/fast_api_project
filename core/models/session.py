from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import settings


class AsyncDBConnection:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )


async_db_connection = AsyncDBConnection(
    settings.db_url,
    settings.db_echo,
)
