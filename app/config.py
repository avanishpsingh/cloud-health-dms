from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Healthcare DMS"
    DEBUG: bool = True
    AUTO_CREATE_TABLES: bool = True

    # Database
    # Local SQLite is the safe default for development and demo videos.
    # Replace this with the RDS/Aurora PostgreSQL URL when the AWS DB is ready.
    DATABASE_URL: str = "sqlite:///./health_dms.db"

    # JWT Auth
    # Use a strong secret in AWS Lambda environment variables or Secrets Manager.
    SECRET_KEY: str = "CHANGE_ME_IN_AWS_PHASE_2"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # File uploads
    # Keep local uploads enabled until the S3 bucket is created.
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set = {".pdf", ".jpg", ".jpeg", ".png"}

    # AWS (Phase 2 placeholders)
    # Switch USE_S3_UPLOADS to true only after the bucket and IAM permissions exist.
    USE_S3_UPLOADS: bool = False
    S3_BUCKET: str = "REPLACE_WITH_YOUR_S3_BUCKET"
    AWS_REGION: str = "ap-south-1"
    S3_KEY_PREFIX: str = "medical-records"

    # Lambda/API Gateway placeholders for Phase 2.
    # These do not change local behavior, but they document the intended deployment target.
    DEPLOYMENT_TARGET: str = "local"
    API_BASE_URL: str = "http://localhost:8000"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()

# AWS Lambda uses a read-only deployment filesystem, so we must not create local
# directories there when S3-backed uploads are enabled.
if not settings.USE_S3_UPLOADS:
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
