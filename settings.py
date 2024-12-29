from pydantic_settings import BaseSettings
from decouple import config as decouple_config

class Settings(BaseSettings):
    database_url: str = decouple_config("DATABASE_URI", cast=str)  # default="postgresql+asyncpg://postgres:password@localhost:5432/ihra
    echo_sql: bool = False
    test: bool = False
    project_name: str = "iHr"
    oauth_token_secret: str = "my_dev_secret_token"   # decouple_config("oauth_token_secret", cast=str)


settings = Settings()  # type: ignore