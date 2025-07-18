import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional



class Settings(BaseSettings):
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None
    COOKIE_NAME: Optional[str] = None

    @property
    def DATABASE_URL_asyncpg(self):
        return (f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@'
                f'{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    @property
    def DATABASE_URL_psycopg(self):
        return (f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@'
                f'{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), extra='allow'
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
    
def get_auth_data():
    return {"secret_key": get_settings().SECRET_KEY, "algorithm": get_settings().ALGORITHM}