from pydantic_settings import BaseSettings
from functools import lru_cache

class GlobalConfig(BaseSettings):
    ENVT_STATE: str
    PROJECT_NAME: str
    DOMAIN: str
    OPENAI_API_KEY: str
    APP_SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = ".env"

class DevConfig(GlobalConfig):
    DATABASE_URL: str
    DB_FORCE_ROLLBACK: bool

    class Config:
        env_prefix: str = "DEV_"

class TestConfig(GlobalConfig):
    DATABASE_URL: str
    DB_FORCE_ROLLBACK: bool

    class Config:
        env_prefix: str = "TEST_"

class ProdConfig(GlobalConfig):
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_prefix: str = "PROD_"

@lru_cache()
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    if env_state not in configs:
        raise ValueError(f"Invalid ENVT_STATE: {env_state}")
    return configs[env_state]()

config = get_config(GlobalConfig().ENVT_STATE)