from pydantic import BaseSettings

from app.constants import (
    DEFAULT_APP_TITLE, DEFAULT_APP_DESCRIPTION, DEFAULT_DATABASE_URL,
    DEFAULT_SECRET
)


class Settings(BaseSettings):
    app_title: str = DEFAULT_APP_TITLE
    app_description: str = DEFAULT_APP_DESCRIPTION
    database_url: str = DEFAULT_DATABASE_URL
    secret: str = DEFAULT_SECRET

    class Config:
        env_file = '.env'


settings = Settings()
