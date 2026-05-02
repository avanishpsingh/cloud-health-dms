# Cloud-Native Healthcare Data Management System — Master Plan

## Project Summary
- **Course**: Cloud Computing (CSIZG527), BITS Pilani
- **Group**: 23 (Karan, Vikas, Kriti, Avanish)
- **Topic**: Cloud-Native Healthcare Data Management System
- **Scope**: Minimal viable assignment — NOT a production system

## Phase 1 — Local Working Software (DONE)
- [x] Read assignment rubrics & Phase 1 PPT
- [x] Create project plan & requirements
- [x] Setup docs/ directory with documentation
- [x] Add .gitignore
- [x] Setup Python project (FastAPI + SQLite)
- [x] Implement database models (Patient, Doctor, Appointment, MedicalRecord)
- [x] Implement REST APIs — full CRUD (22 endpoints total)
- [x] Implement auth (JWT + RBAC: admin/doctor/receptionist)
- [x] Implement file upload for medical reports
- [x] Build analytics endpoint (counts, status breakdown, dept distribution)
- [x] Add seed data script (3 users, 10 doctors, 100 patients, 259 appointments, 104 records)
- [x] Add interactive HTML dashboard with CRUD forms
- [x] Add 17 passing tests
- [x] Update all documentation (README, dev guide, requirements, structure)

## Phase 2 — AWS Cloud Migration

### Code & local validation (DONE)
- [x] Pluggable storage backend (`app/storage.py`) — Local FS / S3 via env var
- [x] CloudWatch-style structured JSON logging (`app/logging_middleware.py`)
- [x] Appointment-reminder Lambda handler (`app/lambda_handlers/`)
- [x] `STORAGE_BACKEND`, `S3_BUCKET`, `S3_KMS_KEY_ID`, `SNS_TOPIC_ARN`, `JSON_LOGS` settings added
- [x] `boto3` + `psycopg2-binary` added to requirements; `moto[s3]` for tests
- [x] 12 new tests added — full suite **29 / 29 green**
- [x] Refactored `routers/records.py` to use the storage abstraction (zero call-site changes)

### Infrastructure-as-Code (DONE)
- [x] Terraform: `main.tf`, `variables.tf`, `outputs.tf`
- [x] `network.tf` — VPC, 2 public + 2 private subnets, IGW, NAT, route tables
- [x] `security.tf` — KMS CMK, IAM roles for EC2 + Lambda, SGs (alb / app / db / lambda)
- [x] `storage_s3.tf` — S3 bucket: SSE-KMS, versioned, public-block, 7-yr lifecycle
- [x] `database_rds.tf` — RDS PostgreSQL 15 Multi-AZ, KMS-encrypted
- [x] `compute_ec2.tf` — Launch template (IMDSv2-only), ASG, ALB, target group, TargetTracking 60% CPU
- [x] `lambda_reminder.tf` — Lambda + EventBridge cron + KMS-encrypted SNS topic
- [x] `observability.tf` — CloudTrail + log group + 2 alarms (5xx, CPU)
- [x] `user_data.sh` — bootstraps Python 3.11, clones repo, writes `.env`, starts uvicorn under systemd, configures CloudWatch agent
- [x] Dockerfile + `.dockerignore` (alternative deployment path)

### Deliverables for submission (DONE)
- [x] README updated with Phase 2 deployment, architecture, mapping table
- [x] `report/Phase2_Report.md` — Abstract → Survey → Problem → Objectives → Outcomes → References → Reflection
- [x] `report/Phase2_PPT_Outline.md` — 14-slide deck outline with speaker notes
- [x] `report/Demo_Video_Script.md` — recording playbook with timestamps
- [x] `report/CC_Project_Report_Group23.pdf` — generated via `scripts/generate_report_pdf.py`
- [x] `report/CC_Project_Code_Group23.pdf` — generated via `scripts/generate_code_pdf.py`
- [x] `tasks/lessons.md` updated with Phase 2 lessons

### Automated deliverables (DONE)
- [x] **Generated** `CC_Project_PPT_Group23.pptx` via `scripts/generate_pptx.py` (polished design)
- [x] **Bundled** `CC_Project_Implementation23.zip` (438 KB) at workspace root containing PPT, code PDF, report PDF, Phase 1 PDF, README, outline, demo script

### Remaining manual work (cannot be automated by the agent)
- [ ] **Run `terraform apply`** in a real AWS account (needs credentials + ~$3 budget alarm)
- [ ] **Confirm SNS email subscription** (click link in inbox)
- [ ] **Record the demo video** following `report/Demo_Video_Script.md`; export as `CC_Project_Demo_Group23.mp4`, drop into `CC_Project_Implementation23/`, delete the placeholder `.README.txt`, then re-zip
- [ ] **Upload** `CC_Project_Implementation23.zip` to Taxila LMS by 03-May-2026
- [ ] **Run `terraform destroy`** after the demo to stop AWS billing

## Phase 3 — Final Presentation (04-10 May 2026)
- [ ] Refine presentation
- [ ] Prepare for Q&A / viva
