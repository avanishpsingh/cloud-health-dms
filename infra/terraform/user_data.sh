#!/usr/bin/env bash
# EC2 user-data — bootstraps the FastAPI app on Amazon Linux 2023.
# Variables in ${...} are interpolated by Terraform's templatefile().
set -euxo pipefail

# 1. Base packages
dnf install -y python3.11 python3.11-pip git amazon-cloudwatch-agent

# 2. Clone the application repo
mkdir -p /opt/app
git clone --depth 1 --branch ${repo_ref} ${repo_url} /opt/app

# 3. Python venv + deps (boto3 added for S3/SNS, psycopg2-binary for RDS)
python3.11 -m venv /opt/app/venv
/opt/app/venv/bin/pip install --upgrade pip
/opt/app/venv/bin/pip install -r /opt/app/requirements.txt
/opt/app/venv/bin/pip install boto3 psycopg2-binary

# 4. Environment file consumed by app/config.py via pydantic-settings
cat > /opt/app/.env <<EOF
DATABASE_URL=postgresql+psycopg2://${db_username}:${db_password}@${db_host}:${db_port}/${db_name}
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=false
STORAGE_BACKEND=s3
S3_BUCKET=${s3_bucket}
S3_KMS_KEY_ID=${kms_key_arn}
AWS_REGION=${aws_region}
SNS_TOPIC_ARN=${sns_topic_arn}
JSON_LOGS=true
LOG_LEVEL=INFO
EOF
chmod 600 /opt/app/.env

# 5. Seed the DB on the first instance only (idempotent — guards on existing rows)
/opt/app/venv/bin/python -c "
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
" || true

# 6. systemd unit for uvicorn
cat > /etc/systemd/system/healthdms.service <<'UNIT'
[Unit]
Description=Healthcare DMS FastAPI app
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/app
EnvironmentFile=/opt/app/.env
ExecStart=/opt/app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5
StandardOutput=append:/var/log/healthdms.log
StandardError=append:/var/log/healthdms.log

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now healthdms.service

# 7. CloudWatch agent — ship /var/log/healthdms.log to /aws/ec2/healthdms
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json <<'CWA'
{
  "agent": { "metrics_collection_interval": 60 },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/healthdms.log",
            "log_group_name": "/aws/ec2/healthdms",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          }
        ]
      }
    }
  },
  "metrics": {
    "metrics_collected": {
      "mem":  { "measurement": ["mem_used_percent"] },
      "disk": { "measurement": ["used_percent"], "resources": ["/"] }
    },
    "append_dimensions": { "InstanceId": "$${aws:InstanceId}" }
  }
}
CWA

systemctl enable --now amazon-cloudwatch-agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
