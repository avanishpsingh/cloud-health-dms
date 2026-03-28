# Cloud-Native Healthcare Data Management System — Master Plan

## Project Summary
- **Course**: Cloud Computing (CSIZG527), BITS Pilani
- **Group**: 23 (Karan, Vikas, Kriti, Avanish)
- **Topic**: Cloud-Native Healthcare Data Management System
- **Scope**: Minimal viable assignment — NOT a production system

## Phase 1 — Local Working Software (Due: 03 May 2026)
Build a simple healthcare data management app that runs locally.

### Phase 1 Tasks
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
- [x] Add interactive HTML dashboard with CRUD forms (add/edit/delete patients, doctors, users, appointments)
- [x] Add 17 passing tests
- [x] Update all documentation (README, dev guide, requirements, structure)
- [ ] Record demo video
- [ ] Prepare Phase 2 PPT

## Phase 2 — AWS Cloud Migration (Due: 03 May 2026)
Migrate local app to AWS services.

### Phase 2 Tasks
- [ ] Setup AWS account & VPC
- [ ] Deploy backend on EC2 (with Auto Scaling Group)
- [ ] Migrate SQLite → RDS PostgreSQL
- [ ] Move file uploads to S3
- [ ] Configure IAM roles & policies
- [ ] Enable KMS encryption on RDS & S3
- [ ] Setup CloudWatch monitoring & alarms
- [ ] Setup CloudTrail for audit logging
- [ ] Configure ALB + Route 53 (if domain available)
- [ ] Basic Lambda function (e.g., appointment reminder/notification)
- [ ] Load test & demonstrate auto-scaling
- [ ] Record demo video of working cloud deployment
- [ ] Write final report (Abstract, Survey, Problem Statement, Objectives, Outcomes, Reflection)
- [ ] Submit deliverables (PPT, Recording, Code PDF, Report)

## Phase 3 — Final Presentation (04-10 May 2026)
- [ ] Refine presentation
- [ ] Prepare for Q&A / viva
