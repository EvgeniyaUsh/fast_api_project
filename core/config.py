from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url = "postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres"
    # db_echo = False
    db_echo = True


settings = Settings()
