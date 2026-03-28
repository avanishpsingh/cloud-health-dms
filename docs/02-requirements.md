# Requirements Specification

## Functional Requirements

### FR1: Patient Management
- FR1.1: Register a new patient (name, age, gender, contact, address, blood group)
- FR1.2: View patient list with search/filter
- FR1.3: View individual patient details
- FR1.4: Update patient information
- FR1.5: Delete patient record (soft delete)

### FR2: Doctor Management
- FR2.1: Register a doctor (name, specialization, contact, department)
- FR2.2: View doctor list
- FR2.3: Update doctor profile

### FR3: Appointment Management
- FR3.1: Book an appointment (patient, doctor, date, time, reason)
- FR3.2: View appointments (by date, doctor, patient)
- FR3.3: Update appointment status (scheduled, completed, cancelled)

### FR4: Medical Records
- FR4.1: Create a medical record for a patient (diagnosis, prescription, notes)
- FR4.2: Upload medical files (PDF reports, images) — stored locally in Phase 1, S3 in Phase 2
- FR4.3: View medical history for a patient

### FR5: Authentication & Authorization
- FR5.1: User login with username/password (JWT tokens)
- FR5.2: Role-based access (admin, doctor, receptionist)
- FR5.3: Admin can manage users; doctors can view/edit medical records; receptionists manage appointments

### FR6: Analytics Dashboard
- FR6.1: Total patients, doctors, appointments count
- FR6.2: Appointments per day/week chart data
- FR6.3: Department-wise patient distribution

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
