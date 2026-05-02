output "alb_url" {
  description = "Open this URL in a browser for the live dashboard."
  value       = "http://${aws_lb.app.dns_name}/dashboard"
}

output "alb_dns" {
  value = aws_lb.app.dns_name
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint (host:port)."
  value       = "${aws_db_instance.main.address}:${aws_db_instance.main.port}"
  sensitive   = true
}

output "s3_bucket" {
  value = aws_s3_bucket.files.bucket
}

output "kms_key_arn" {
  value = aws_kms_key.data.arn
}

output "sns_topic_arn" {
  value = aws_sns_topic.reminders.arn
}

output "lambda_function" {
  value = aws_lambda_function.reminder.function_name
}

output "cloudtrail_bucket" {
  value = aws_s3_bucket.trail.bucket
}

output "log_group" {
  value = aws_cloudwatch_log_group.app.name
}
