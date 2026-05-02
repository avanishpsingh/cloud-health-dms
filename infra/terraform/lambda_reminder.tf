###############################################################################
# Lambda (appointment_reminder) + EventBridge schedule + SNS topic.
###############################################################################

resource "aws_sns_topic" "reminders" {
  name              = "${local.name}-reminders"
  kms_master_key_id = aws_kms_key.data.arn
}

# Optional email subscription so demo viewers see real notifications.
resource "aws_sns_topic_subscription" "alarm_email" {
  count     = var.alarm_email == "" ? 0 : 1
  topic_arn = aws_sns_topic.reminders.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# Package the app into a zip Lambda can run. We include the whole `app/`
# package so models + db code are importable inside the function.
data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../app"
  output_path = "${path.module}/build/appointment_reminder.zip"
}

resource "aws_lambda_function" "reminder" {
  function_name    = "${local.name}-reminder"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.11"
  handler          = "lambda_handlers.appointment_reminder.lambda_handler"
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  timeout          = 30
  memory_size      = 256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      DATABASE_URL          = "postgresql+psycopg2://${var.db_username}:${var.db_password}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${var.db_name}"
      SNS_TOPIC_ARN         = aws_sns_topic.reminders.arn
      REMINDER_WINDOW_HOURS = "24"
      JSON_LOGS             = "true"
      LOG_LEVEL             = "INFO"
    }
  }
}

# Trigger Lambda every 15 minutes via EventBridge.
resource "aws_cloudwatch_event_rule" "every_15_min" {
  name                = "${local.name}-reminder-schedule"
  schedule_expression = "rate(15 minutes)"
}

resource "aws_cloudwatch_event_target" "reminder" {
  rule      = aws_cloudwatch_event_rule.every_15_min.name
  target_id = "reminder-lambda"
  arn       = aws_lambda_function.reminder.arn
}

resource "aws_lambda_permission" "events" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reminder.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_15_min.arn
}
