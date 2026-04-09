from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./archive.db"
    SECRET_KEY: str = "change-me-to-a-random-secret"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_DEFAULT_PASSWORD: str = "admin123"
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
