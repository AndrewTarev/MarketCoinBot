import os
from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env")
else:
    load_dotenv()

DB_PATH = "user.db"
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATE_FORMAT = "%d.%m.%Y"


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    BOT_TOKEN: str

    @property
    def DATABASE_URL_psycopg(self):
        # postgresql+psycopg://postgres:postgres@localhost:5432/TG_Bot_MarketCoinBot
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
