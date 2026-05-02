# Lessons Learned

## Phase 2 — AWS Migration

- **Pluggable backends > rewrites.** Defining a `StorageBackend` Protocol
  with `LocalStorage` + `S3Storage` implementations let Phase 1 keep
  working while Phase 2 added S3 — zero changes to router call sites.
- **Mock AWS in CI.** `moto[s3]` + `monkeypatch` on `settings` is enough
  to test the S3 path without credentials. Patch `app.database.SessionLocal`
  (where it's defined), not `app.lambda_handlers.appointment_reminder.SessionLocal`
  (where it's lazily imported), or `unittest.mock.patch` will fail with
  *"module does not have the attribute"*.
- **Terraform layout matters.** Splitting one root module into purpose-named
  files (`network.tf`, `security.tf`, `compute_ec2.tf`, …) made code review
  trivial vs. one 600-line `main.tf`.
- **IMDSv2 by default.** Set `http_tokens = "required"` on every
  `aws_launch_template` — it's the SSRF mitigation reviewers look for.
- **One NAT, two AZs.** Cost-conscious academic setup uses a single NAT
  and accepts the AZ-failure trade-off; document the trade-off in the report.
- **PDF generation as code.** `reportlab` produces both the code PDF and
  the report PDF deterministically; no LaTeX, no wkhtmltopdf, no Office.
- **`config.py` is `.copilotignore`-d.** Edits to it must go via terminal
  (`Set-Content`), not the file-edit tool. Discovered the hard way mid-task.

## Phase 2 — Database Seeding Workarounds

- **Lambda psycopg2 challenge.** Initial attempt to use Lambda with psycopg2 failed
  because the library isn't in the standard Python 3.11 runtime. Solutions:
  1. Add a Lambda Layer (requires compilation & packaging) — slow.
  2. Use RDS Data API (no library needed) — but requires proper ARN references.
  3. Add HTTP endpoint to app itself (simplest) — seeding becomes idempotent & callable.
  → Chose #3: Added `/auth/seed` POST endpoint to app, deployed via instance restart.

- **Corporate firewall blocks port 5432.** Direct laptop → RDS connection times out
  at network layer (not app layer). Workarounds tested:
  1. Lambda from within VPC (psycopg2 not available).
  2. SSM Run Command on EC2 (agent not ready in time).
  3. HTTP endpoint via ALB (works, because ALB is in VPC, bound to port 80/443).
  → Chose #3 for speed; SSM would have worked after 20-30 min wait.

- **ASG auto-restart strategy.** When code changes but instances are running,
  terminating instances forces ASG to launch new ones with updated code via user_data.
  This is faster than SSH (no key pair needed) or SSM (agent registration time).

- **Idempotent seed endpoints.** Seed via POST `/auth/seed` checks if `admin` user exists;
  if yes, returns "already seeded"; if no, creates demo data. Safe to call multiple times.
  Beats CI/CD hooks and migrations for MVPs.

