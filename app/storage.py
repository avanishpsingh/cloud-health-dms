from pathlib import Path
import uuid

from app.config import settings


def save_medical_record_file(contents: bytes, original_filename: str) -> str:
    """Save an uploaded file either locally or to S3.

    Local storage remains the default so the project works before AWS resources exist.
    Once the S3 bucket and IAM permissions are ready, set USE_S3_UPLOADS=true and
    provide a real S3 bucket name in the environment.
    """
    suffix = Path(original_filename).suffix.lower()
    generated_name = f"{uuid.uuid4().hex}{suffix}"

    if settings.USE_S3_UPLOADS:
        return _save_to_s3(contents, generated_name)

    return _save_to_local_disk(contents, generated_name)


def _save_to_local_disk(contents: bytes, generated_name: str) -> str:
    """Phase 1 / fallback path used before S3 is provisioned."""
    destination = Path(settings.UPLOAD_DIR) / generated_name
    destination.write_bytes(contents)
    return str(destination)


def _save_to_s3(contents: bytes, generated_name: str) -> str:
    """Phase 2 path used after the S3 bucket exists.

    The returned value is the S3 object key, which is what we store in the database.
    """
    import boto3

    s3_client = boto3.client("s3", region_name=settings.AWS_REGION)
    object_key = f"{settings.S3_KEY_PREFIX}/{generated_name}"

    s3_client.put_object(
        Bucket=settings.S3_BUCKET,
        Key=object_key,
        Body=contents,
    )
    return object_key
