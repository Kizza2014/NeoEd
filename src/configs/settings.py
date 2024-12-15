from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # # Project Config
    # PROJECT_NAME: str = "NeoEd"
    # VERSION: str = "1.0.0"
    # API_PREFIX: str = "/api"
    # DEBUG: bool = True

    # JWT Config
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # # Redis Config
    # REDIS_HOST: str
    # REDIS_PORT: int
    # REDIS_PASSWORD: str
    # REDIS_DB: int = 0
    # REDIS_TIMEOUT: int = 5

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()