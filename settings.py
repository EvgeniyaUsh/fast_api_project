from envparse import Env

env = Env()

PROJECT_DATABESE_URL = env.str(
    "PROJECT_DATABESE_URL",
    default="postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres",
)
