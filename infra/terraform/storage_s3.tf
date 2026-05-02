###############################################################################
# S3 bucket for medical files (Phase 2 replacement for ./uploads).
#
# - SSE-KMS using the shared CMK (Objective O3).
# - Versioning ON for tamper-evidence.
# - Public access blocked at the account level.
# - Lifecycle rule: transition to IA after 30d, Glacier after 90d, expire after 7y
#   (HIPAA minimum retention).
###############################################################################

resource "aws_s3_bucket" "files" {
  bucket        = local.s3_bucket
  force_destroy = true   # academic project — destroy on `terraform destroy`
  tags          = { Name = "${local.name}-medical-files" }
}

resource "aws_s3_bucket_public_access_block" "files" {
  bucket                  = aws_s3_bucket.files.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "files" {
  bucket = aws_s3_bucket.files.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "files" {
  bucket = aws_s3_bucket.files.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.data.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "files" {
  bucket = aws_s3_bucket.files.id
  rule {
    id     = "phi-retention"
    status = "Enabled"
    filter {}
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    expiration {
      days = 2555   # 7 years (HIPAA / DISHA minimum retention)
    }
  }
}
