from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "JEJAK Application Backend"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./jejak_backend.db"
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)



settings = Settings()
