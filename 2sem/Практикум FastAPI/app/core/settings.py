from pydantic_settings import BaseSettings, SettingsConfigDict

# НАСТРОЙКИ ПРОЕКТА КОТОРЫЕ СЧИТЫВ ИЗ .ENV

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:9052@localhost:5432/practicum"
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
