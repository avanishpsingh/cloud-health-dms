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
