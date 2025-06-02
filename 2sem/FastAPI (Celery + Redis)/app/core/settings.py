from pydantic_settings import BaseSettings, SettingsConfigDict

# НАСТРОЙКИ ПРОЕКТА КОТОРЫЕ СЧИТЫВ ИЗ .ENV

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:9052@localhost:5432/practicum"
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
