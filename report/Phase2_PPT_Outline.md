# Phase 2 — Final Presentation (Speaker Notes & Slide Outline)

> 12 minutes presentation + 3 minutes Q&A.
> Convert this markdown to slides via Marp / Pandoc / PowerPoint.
> Each `---` is a new slide. Speaker notes are in *italics* under each slide.

---

## Slide 1 — Title

**Cloud-Native Healthcare Data Management System**
Phase 2 — Implementation & Demonstration
BITS Pilani · Cloud Computing (CSIZG527) · Group 23
Karan Rawat · Vikas Kumar · Kriti Tripathi · Avanish Pratap Singh
Instructor: Prof. Shwetha Vittal · 02 May 2026

*Welcome the audience, introduce members, state that all 6 Phase-1 objectives are implemented and demoable.*

---

## Slide 2 — Recap: Problem & Phase-1 Objectives

- Mid-size hospital chain in India, fragmented on-prem IT
- Pain: peak-hour overload, data silos, audit gaps, idle hardware
- 6 measurable objectives (O1–O6) defined in Phase 1

*One sentence per pain point. Don't re-justify — Phase 1 already did that.*

---

## Slide 3 — Phase-2 Architecture (one diagram)

```
Users → Route 53 → ALB → EC2 ASG (private) → RDS PostgreSQL Multi-AZ
                                ↘
                                  S3 (KMS) ←─ Lambda ←─ EventBridge cron
                                                    ↘ SNS → Email/SMS
Cross-cutting: VPC · IAM · KMS · CloudTrail · CloudWatch
```

*Walk left-to-right: ingress, compute, data, serverless, observability.*

---

## Slide 4 — Code: One repo, two backends

- Same FastAPI codebase runs Phase 1 (laptop) and Phase 2 (AWS).
- Pluggable layers selected by **environment variables**:
  - `STORAGE_BACKEND=local | s3`
  - `DATABASE_URL=sqlite://… | postgresql+psycopg2://…`
- Storage abstraction: `app/storage.py` (Protocol + `LocalStorage` + `S3Storage`)
- Lambda imports the same `app/` tree — no code duplication.

*Open `app/storage.py` and `app/routers/records.py` briefly during the live demo.*

---

## Slide 5 — Infrastructure as Code (Terraform)

- 10 `.tf` files, ~ 600 LOC, single `terraform apply`
- Provisions: VPC + 2 AZs · KMS CMK · S3 + lifecycle · RDS Multi-AZ · ALB +
  ASG · Lambda + EventBridge + SNS · CloudTrail · CloudWatch alarms
- IMDSv2-only EC2; least-privilege IAM; private subnets for data layer.
- `terraform destroy` returns the account to zero spend.

*Show the file tree under `infra/terraform/` and the `terraform plan` summary.*

---

## Slide 6 — Security & Compliance (O3)

| Control                  | Implementation                          |
|--------------------------|-----------------------------------------|
| Encryption at rest       | KMS CMK on RDS, SSE-KMS on S3, log groups, SNS, CloudTrail |
| Encryption in transit    | TLS terminated at ALB; SG-restricted ingress |
| AuthN / AuthZ            | App-level JWT + RBAC; cloud-level IAM least-privilege |
| Audit                    | CloudTrail multi-region, log-file validation |
| PHI retention            | S3 lifecycle: IA → Glacier → expire @ 7 y |
| Network isolation        | Private subnets for EC2 + RDS; SGs least-privilege |

*Tie each row to HIPAA / DISHA expectations.*

---

## Slide 7 — Auto-Scaling & Availability (O1, O6)

- ASG: min 1, max 3, TargetTracking on **avg CPU = 60 %**
- ALB health check `GET /` every 30 s
- RDS Multi-AZ → automated failover, < 60 s RTO
- 2 CloudWatch alarms (5xx > 5/min, CPU > 80 % for 3 min) → SNS
- Demonstrated by `ab` / `wrk` load test in the recording

*During the recording, you can show the ASG scaling-out instance count in the AWS console.*

---

## Slide 8 — Serverless Reminders (O4)

- `app/lambda_handlers/appointment_reminder.py`
- EventBridge cron → Lambda (Python 3.11, 256 MB, 30 s timeout)
- Reads RDS for appointments due in next 24 h
- Publishes one message per appointment to SNS topic
- SNS → Email subscription (configurable via `alarm_email` Terraform var)

*Show a sample CloudWatch Logs entry during the demo.*

---

## Slide 9 — Cost Optimisation (O5)

| Resource          | Sizing                  | ~ Monthly USD |
|-------------------|-------------------------|--------------:|
| EC2 t3.micro × 2  | ASG min=1, desired=2    | $15           |
| ALB               | Internet-facing         | $18           |
| RDS db.t3.micro Multi-AZ | 20 GB gp3        | $30           |
| S3 + Lambda + CloudWatch + CloudTrail |     | < $3          |
| NAT Gateway       | Single, cost-conscious  | $32           |
| **Total**         |                         | **~$98 / mo** |

*Compare to estimated on-prem hardware refresh of ~ ₹ 6–10 lakh capex; cloud is OpEx and pay-per-use.*

---

## Slide 10 — Test Strategy

- 29 pytest tests, all green, run in **28 s on a laptop**
- `moto` mocks S3 + SNS → no AWS credentials required for CI
- Coverage spans business logic AND cloud abstractions:
  - 6 auth · 7 patients · 4 appointments
  - 4 storage · 3 Lambda · 3 logging · 2 upload E2E

*Show terminal output of `pytest -v` during the recording.*

---

## Slide 11 — Live Demo (recorded video)

1. `terraform apply` walk-through (timelapse)
2. Open ALB URL → dashboard, login as `admin`
3. Create patient, book appointment, upload PDF (lands in S3)
4. AWS Console: S3 object, RDS Performance Insights, CloudWatch Logs Insights query
5. Trigger Lambda manually → SNS email arrives
6. `ab -n 5000 -c 50 http://<alb>/dashboard` → ASG scales out

*Keep video under 8 minutes; speak over each step.*

---

## Slide 12 — Roles & Contributions

| Member                   | Phase 2 Contribution                                                |
|--------------------------|---------------------------------------------------------------------|
| Karan Rawat              | Architecture, Terraform `network.tf` / `compute_ec2.tf`, integration|
| Vikas Kumar              | RDS migration, SQLAlchemy review, Lambda data-access layer          |
| Kriti Tripathi           | Security (KMS / IAM / CloudTrail), report writing, compliance mapping|
| Avanish Pratap Singh     | Test suite (29 tests, `moto` setup), CloudWatch / observability, demo recording |

*Each member speaks for ~ 60 s on their slice; equal participation is mandated by rubric.*

---

## Slide 13 — Reflection (rubric-required)

- **Workplace relevance:** mirrors enterprise dev → staging → prod migrations
- **Concepts learned:** IaC, IAM/KMS composition, mocked-AWS testing, cost-as-design-input
- **Trade-offs:** RDS over DynamoDB; single NAT; t3.micro; deferred ACM/WAF — documented
- **Next iteration:** Secrets Manager, App Runner / Fargate, integration smoke tests post-apply

*Pull verbatim from `report/Phase2_Report.md` §7.*

---

## Slide 14 — Q&A

- Repo: https://github.com/avanishpsingh/cloud-health-dms
- All deliverables in `CC_Project_Implementation23.zip`
- Thank you!

*Be ready for: "Why not DynamoDB?", "How does Multi-AZ failover work?", "How would you achieve 99.99% (4-nines) instead of 99.9?", "What about WAF?"*
