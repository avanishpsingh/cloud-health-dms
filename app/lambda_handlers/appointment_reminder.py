"""AWS Lambda handler — appointment reminders.

Architecture (Phase 2):
  CloudWatch Events (cron, every 15 min)
        │
        ▼
  AWS Lambda (this module)
        │── reads appointments due in the next 24h from RDS PostgreSQL
        │── publishes one message per appointment to SNS topic
        ▼
  SNS Topic ──► Email / SMS subscribers (patient contacts, hospital staff)

Why Lambda?
  * Serverless — no idle cost, scales to N concurrent invocations.
  * Event-driven — fires only when CloudWatch Events triggers it.
  * Aligns with Project Objective O1 (cloud-native serverless compute).

Local execution:
  python -m app.lambda_handlers.appointment_reminder
  (uses settings.DATABASE_URL, defaults to local SQLite)
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger("lambda.appointment_reminder")
logger.setLevel(logging.INFO)


def _build_message(appointment: Any) -> dict:
    """Build the SNS message payload for one appointment."""
    return {
        "appointment_id": appointment.id,
        "patient_id": appointment.patient_id,
        "doctor_id": appointment.doctor_id,
        "scheduled_for": appointment.date_time.isoformat(),
        "reason": appointment.reason,
        "channel": "reminder",
    }


def _publish_to_sns(sns_client, topic_arn: str, message: dict) -> str | None:
    """Publish to SNS; returns MessageId or None if no topic configured."""
    if not topic_arn:
        logger.info("SNS topic not configured — skipping publish (dry run)")
        return None
    resp = sns_client.publish(
        TopicArn=topic_arn,
        Subject="Healthcare DMS — Appointment Reminder",
        Message=json.dumps(message),
    )
    return resp.get("MessageId")


def find_due_appointments(db, hours_ahead: int = 24) -> list:
    """Query RDS for scheduled appointments inside the reminder window."""
    # Imported here so unit tests can stub the DB without importing the whole app.
    from app.models.appointment import Appointment

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    window_end = now + timedelta(hours=hours_ahead)
    return (
        db.query(Appointment)
        .filter(
            Appointment.status == "scheduled",
            Appointment.date_time >= now,
            Appointment.date_time <= window_end,
        )
        .all()
    )


def lambda_handler(event: dict, context: Any) -> dict:
    """AWS Lambda entry point.

    Returns:
        {"published": int, "skipped": int, "ids": [...]}.
    """
    # Lazy imports keep cold-start small if some deps are missing in tests.
    from app.database import SessionLocal

    topic_arn = os.environ.get("SNS_TOPIC_ARN", "")
    hours_ahead = int(os.environ.get("REMINDER_WINDOW_HOURS", "24"))

    sns = None
    if topic_arn:
        import boto3  # type: ignore

        sns = boto3.client("sns")

    db = SessionLocal()
    published, skipped, ids = 0, 0, []
    try:
        appointments = find_due_appointments(db, hours_ahead=hours_ahead)
        logger.info("found %d appointments in next %dh", len(appointments), hours_ahead)
        for appt in appointments:
            msg = _build_message(appt)
            mid = _publish_to_sns(sns, topic_arn, msg)
            if mid is None:
                skipped += 1
            else:
                published += 1
                ids.append(mid)
    finally:
        db.close()

    return {"published": published, "skipped": skipped, "ids": ids}


if __name__ == "__main__":  # pragma: no cover - manual execution
    print(json.dumps(lambda_handler({}, None), indent=2))
