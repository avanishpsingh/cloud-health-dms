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

    # Phase 2 - AWS storage backend
    # STORAGE_BACKEND: "local" (Phase 1) or "s3" (Phase 2)
    STORAGE_BACKEND: str = "local"
    S3_BUCKET: str = ""
    S3_PREFIX: str = "medical-records/"
    S3_KMS_KEY_ID: str = ""  # optional KMS CMK ARN for SSE-KMS
    AWS_REGION: str = "ap-south-1"

    # Phase 2 - SNS topic for appointment notifications (optional)
    SNS_TOPIC_ARN: str = ""

    # Phase 2 - structured (CloudWatch-friendly) JSON logging
    JSON_LOGS: bool = False
    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

# Ensure upload directory exists when running with the local backend
if settings.STORAGE_BACKEND.lower() == "local":
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
