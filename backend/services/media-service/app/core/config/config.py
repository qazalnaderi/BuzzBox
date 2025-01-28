from functools import lru_cache
from pathlib import Path
from loguru import logger

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str =  "mongodb://mongo:27017"   #"mongodb://mongo:27017"
    DATABASE_NAME: str = "emailserviceMediaDB"
    FILE_STORAGE_PATH: str = "app/media"
    IAM_URL: str = "http://iam.localhost:9000"
    GRPC_PORT: int = 50051

    # model_config = SettingsConfigDict(env_file=str(Path(__file__).resolve().parent / ".env"))


#@lru_cache
@logger.catch
def get_settings():
    settings = Settings()
    logger.info(f"Loaded settings: {settings.dict()}")
    return settings