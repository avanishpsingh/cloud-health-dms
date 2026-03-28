# Requirements Specification

## Functional Requirements — Implementation Status

### FR1: Patient Management ✅ Complete
- FR1.1: ✅ Register a new patient (name, age, gender, contact, address, blood group) — API + Dashboard form
- FR1.2: ✅ View patient list with search/filter — API + Dashboard with pagination
- FR1.3: ✅ View individual patient details — API + Dashboard detail view with records & appointments
- FR1.4: ✅ Update patient information — API + Dashboard edit form
- FR1.5: ✅ Delete patient record (soft delete) — API + Dashboard delete button

### FR2: Doctor Management ✅ Complete
- FR2.1: ✅ Register a doctor (name, specialization, contact, department) — API + Dashboard form
- FR2.2: ✅ View doctor list with search and department filter — API + Dashboard
- FR2.3: ✅ Update doctor profile — API + Dashboard edit form
- FR2.4: ✅ Delete doctor — API + Dashboard delete button

### FR3: Appointment Management ✅ Complete
- FR3.1: ✅ Book an appointment (patient, doctor, date, time, reason) — API + Dashboard form
- FR3.2: ✅ View appointments with filters (by status, patient, doctor) — API + Dashboard
- FR3.3: ✅ Update appointment status (scheduled, completed, cancelled) — API + Dashboard click-to-change
- FR3.4: ✅ Delete appointment — API + Dashboard delete button

### FR4: Medical Records ✅ Complete
- FR4.1: ✅ Create a medical record for a patient (diagnosis, prescription, notes) — API (Doctor role)
- FR4.2: ✅ Upload medical files (PDF, JPEG, PNG) — API with extension & size validation
- FR4.3: ✅ View medical history for a patient — API + Dashboard patient detail view

### FR5: Authentication & Authorization ✅ Complete
- FR5.1: ✅ User login with username/password (JWT tokens) — API + Dashboard login screen
- FR5.2: ✅ Role-based access (admin, doctor, receptionist) — enforced on all endpoints
- FR5.3: ✅ Admin can manage users (list, register) — API + Dashboard Users tab
- FR5.4: ✅ Doctors can view patients/records, manage appointment status
- FR5.5: ✅ Receptionists can manage patients and schedule appointments

### FR6: Analytics Dashboard ✅ Complete
- FR6.1: ✅ Total patients, doctors, appointments count — Dashboard overview cards
- FR6.2: ✅ Appointment status distribution (bar chart) — Dashboard overview
- FR6.3: ✅ Department-wise patient distribution (bar chart) — Dashboard overview

---

## Non-Functional Requirements

### NFR1: Performance
- API response time < 200ms for CRUD operations (local)
- Support 50 concurrent users (simulated for demo)

### NFR2: Security
- Passwords hashed with bcrypt
- JWT token-based auth with expiry
- Role-based access control on all endpoints
- File uploads validated (type, size limits)
- SQL injection protection (ORM-based queries)

### NFR3: Data Integrity
- Foreign key constraints on all relationships
- Input validation on all API endpoints

### NFR4: Availability (Phase 2)
- Multi-AZ RDS deployment
- EC2 Auto Scaling (min 1, max 3 instances)
- Health checks via ALB

### NFR5: Compliance Readiness (Phase 2)
- KMS encryption at rest (RDS, S3)
- TLS in transit
- CloudTrail audit logging
- IAM least-privilege policies

### NFR6: Monitoring (Phase 2)
- CloudWatch metrics for CPU, memory, request count
- CloudWatch alarms for high CPU (>80%)
- SNS notifications for critical events
