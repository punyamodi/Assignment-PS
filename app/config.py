from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./paysaathi.db"
    EXTERNAL_API_BASE_URL: str = "http://localhost:8001"
    SYNC_TIMEOUT_SECONDS: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
