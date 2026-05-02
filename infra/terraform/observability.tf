###############################################################################
# CloudTrail (audit) + CloudWatch alarms.
###############################################################################

# ---- Dedicated bucket for CloudTrail logs ----------------------------------
resource "aws_s3_bucket" "trail" {
  bucket        = "${local.name}-cloudtrail-${random_id.suffix.hex}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "trail" {
  bucket                  = aws_s3_bucket.trail.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_caller_identity" "me" {}

data "aws_iam_policy_document" "trail_bucket" {
  statement {
    sid     = "AWSCloudTrailAclCheck"
    actions = ["s3:GetBucketAcl"]
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    resources = [aws_s3_bucket.trail.arn]
  }
  statement {
    sid     = "AWSCloudTrailWrite"
    actions = ["s3:PutObject"]
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    resources = ["${aws_s3_bucket.trail.arn}/AWSLogs/${data.aws_caller_identity.me.account_id}/*"]
    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}

resource "aws_s3_bucket_policy" "trail" {
  bucket = aws_s3_bucket.trail.id
  policy = data.aws_iam_policy_document.trail_bucket.json
}

resource "aws_cloudtrail" "main" {
  name                          = "${local.name}-trail"
  s3_bucket_name                = aws_s3_bucket.trail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  kms_key_id                    = aws_kms_key.data.arn
  depends_on                    = [aws_s3_bucket_policy.trail]
}

# ---- CloudWatch log group for the app --------------------------------------
resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/ec2/healthdms"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.data.arn
}

# ---- Alarms ----------------------------------------------------------------
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${local.name}-alb-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "More than 5 5xx responses per minute from the app target group"
  dimensions          = { LoadBalancer = aws_lb.app.arn_suffix }
  alarm_actions       = [aws_sns_topic.reminders.arn]
  treat_missing_data  = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "asg_high_cpu" {
  alarm_name          = "${local.name}-asg-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ASG average CPU > 80% for 3 consecutive minutes"
  dimensions          = { AutoScalingGroupName = aws_autoscaling_group.app.name }
  alarm_actions       = [aws_sns_topic.reminders.arn]
}
