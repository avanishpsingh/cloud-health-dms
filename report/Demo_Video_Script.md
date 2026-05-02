# Phase 2 — Demo Video Script (≤ 8 minutes)

> **Purpose:** Replace narrative with on-screen action so the rubric line
> *"Project Recording Submission — Demonstrates a fully functional
> implementation … Showcases cloud integration, deployments, and key features"*
> is satisfied end-to-end.

> **Recording tool:** OBS Studio (or built-in Windows Game Bar). 1080p, 30 fps,
> microphone narration. Save as `.mp4`, ≤ 200 MB. Filename:
> `CC_Project_Demo_Group23.mp4`.

---

## Pre-flight (do BEFORE recording)

```bash
# 0. AWS account ready, AWS CLI configured, ~$3 budget alarm set just in case
aws sts get-caller-identity   # confirm correct account

# 1. Provision the stack — DON'T record this; it takes ~12 min
cd cloud-health-dms/infra/terraform
terraform init
terraform apply -auto-approve \
  -var "db_password=DemoPass1!" \
  -var "key_pair_name=my-key" \
  -var "alarm_email=group23@example.com"

# 2. Note these for the demo
terraform output alb_url
terraform output s3_bucket
terraform output lambda_function

# 3. Confirm SNS email subscription is "Confirmed" (click link in inbox)

# 4. Seed the cloud DB once (uses RDS through the EC2 box)
ssh -i my-key.pem ec2-user@<one-of-the-asg-ips>
sudo -u root /opt/app/venv/bin/python /opt/app/scripts/seed.py
exit
```

---

## Scene 1 (0:00 – 0:30) — Title card + agenda

- Open with a static slide: project title, team, course.
- Voice: *"This is the Phase 2 demo for Group 23. In the next eight
  minutes we'll show the live cloud-deployed app, walk through the
  AWS console, demonstrate auto-scaling, and trigger the serverless
  reminder Lambda."*

## Scene 2 (0:30 – 1:00) — Repo + tests

- Open VS Code, show project tree (highlight `app/`, `infra/terraform/`, `tests/`).
- Run `python -m pytest tests/ -q`. Voice over: *"29 tests, all green,
  using `moto` to mock AWS — no real credentials are needed for CI."*

## Scene 3 (1:00 – 2:00) — Terraform IaC

- Open `infra/terraform/` and scroll through `main.tf`, `network.tf`,
  `compute_ec2.tf`, `lambda_reminder.tf`, `observability.tf`.
- Switch to terminal: `terraform output`. Read out ALB URL, S3 bucket,
  Lambda function name.
- Voice: *"One `terraform apply` brings up VPC, KMS, S3, RDS Multi-AZ,
  ALB, EC2 ASG, Lambda, EventBridge, SNS, CloudTrail and CloudWatch
  alarms."*

## Scene 4 (2:00 – 3:30) — Browser demo through the ALB

1. Open the ALB URL → dashboard.
2. Login as `admin / admin123`.
3. Overview tab → show stats cards & charts.
4. Patients tab → search, then **Add Patient**: "Demo Recording", age 35.
5. Appointments tab → **Add Appointment** for the new patient.
6. Patient detail → **Add Medical Record** → **Upload** a PDF.
7. Voice: *"That upload just landed in S3. Let's confirm."*

## Scene 5 (3:30 – 4:30) — AWS Console proofs

- **S3** → open bucket → show the new object → click **Properties** →
  highlight **Server-side encryption: AWS-KMS** with our CMK alias.
- **RDS** → instance → **Performance Insights** → show the SQL
  hitting `patients` and `appointments` tables.
- **CloudWatch Logs Insights**, log group `/aws/ec2/healthdms`, paste:

```
fields @timestamp, request_id, method, path, status, duration_ms
| filter status >= 400
| sort @timestamp desc
| limit 20
```

- Voice: *"All requests are JSON-structured with a request ID — exactly
  what CloudWatch Logs Insights needs."*

## Scene 6 (4:30 – 5:30) — Serverless reminder Lambda

- **Lambda console** → open `healthdms-dev-reminder`.
- Click **Test** with an empty event → show the Execution Result:
  `{ "published": N, "skipped": 0, "ids": [...] }`.
- Switch to inbox → show the SNS reminder email that just arrived.
- Voice: *"EventBridge triggers this every 15 minutes in production;
  here we invoked it manually."*

## Scene 7 (5:30 – 6:30) — Auto-scaling under load

- Terminal: `ab -n 5000 -c 50 http://<alb-dns>/dashboard` (Apache Bench).
- AWS Console → **EC2 → Auto Scaling Groups** → watch desired/instance
  count climb from 2 to 3.
- CloudWatch metrics: CPU avg crossing 60 %.
- Voice: *"Target Tracking on 60% CPU pulls in a third instance; this
  satisfies Objective O1 — auto-scale to 3× peak traffic."*

## Scene 8 (6:30 – 7:30) — Audit & alarms

- **CloudTrail** → Event History → filter by `EventSource=s3.amazonaws.com`
  → show the `PutObject` event from the upload demo.
- **CloudWatch Alarms** → show the two configured alarms.
- Voice: *"Every API call is auditable; alarms fan out via the same SNS
  topic the reminders use."*

## Scene 9 (7:30 – 8:00) — Tear-down + closing

- Switch to terminal: `terraform destroy -auto-approve …` (cut after the
  destroy plan is shown — don't wait for completion in the recording).
- Voice: *"`terraform destroy` returns the account to zero spend.
  Thanks for watching — see the report PDF for the full architectural
  rationale and reflection."*

---

## Editing checklist

- [ ] Add captions for AWS Console tabs you click on.
- [ ] Mute terminal bell sounds.
- [ ] Cut any 5+ second waits (Terraform progress bars, browser refreshes).
- [ ] Final length 6–8 minutes; rubric only requires "demonstrates a fully
      functional implementation — no minimum length."
- [ ] Export H.264 MP4, 1920×1080, audio AAC 128 kbps.
