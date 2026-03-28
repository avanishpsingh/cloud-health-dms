from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Healthcare DMS"
    DEBUG: bool = True

    # Database - SQLite for Phase 1, swap to PostgreSQL URL for Phase 2
    DATABASE_URL: str = "sqlite:///./health_dms.db"

    # JWT Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # File uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set = {".pdf", ".jpg", ".jpeg", ".png"}

    # Phase 2 - AWS (unused in Phase 1)
    S3_BUCKET: str = ""
    AWS_REGION: str = "ap-south-1"

    model_config = {"env_file": ".env"}


settings = Settings()

# Ensure upload directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
