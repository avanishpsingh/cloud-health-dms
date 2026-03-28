# Project Overview

## Cloud-Native Healthcare Data Management System

**Course**: Cloud Computing (CSIZG527/SEZG527/SSZG527) — BITS Pilani  
**Instructor**: Dr. Shwetha Vittal  
**LF**: Dr. Sumanth Reddy  
**Group**: 23  

### Team Members
| Name | Role |
|------|------|
| Karan Rawat | System Design & Coordination |
| Vikas Kumar | Data & Backend Handling |
| Kriti Tripathi | Security & Documentation |
| Avanish Pratap Singh | Testing & Monitoring |

---

## Problem Statement

> A mid-size hospital chain in India operates on fragmented, on-premise IT infrastructure with partial cloud adoption. The system struggles with scalability during peak hours, data silos across branches, inconsistent security practices, and high operational costs. There is no cloud-native architecture to provide auto-scaling, unified patient data management, real-time analytics, and compliance-ready security — resulting in degraded patient care and operational inefficiency.

## Objectives
1. **O1** — Design a cloud-native architecture using AWS services that can auto-scale to handle peak traffic
2. **O2** — Build a unified patient data management layer eliminating data silos, achieving <200ms query latency
3. **O3** — Implement security & compliance framework (IAM, encryption, audit logging) aligned to HIPAA/DISHA
4. **O4** — Deploy an analytics pipeline for patient flow monitoring and resource dashboards
5. **O5** — Achieve cost reduction by migrating to pay-per-use cloud model
6. **O6** — Ensure high availability using Multi-AZ deployment and automated failover

## Scope (Assignment-Level)

This is a **minimal viable implementation** for academic purposes. We focus on demonstrating cloud concepts, not building a production-grade hospital system.

### In Scope
- Patient record CRUD (create, read, update, delete)
- Doctor & appointment management
- Basic role-based authentication (admin, doctor, receptionist)
- File upload for medical reports
- Simple analytics dashboard
- AWS migration (EC2, RDS, S3, Lambda, IAM, CloudWatch)

### Out of Scope
- Real EHR/EMR standards (HL7 FHIR)
- Mobile application
- Real-time IoT device integration
- Multi-hospital branch sync (simulated, not real)
- Production-grade HIPAA compliance
- Payment/billing integration

## Two-Phase Development Strategy

| Phase | Scope | Timeline |
|-------|-------|----------|
| Phase 1 | Working local software (FastAPI + SQLite) | 03 Apr – 20 Apr 2026 |
| Phase 2 | AWS Cloud migration & integration | 20 Apr – 03 May 2026 |
| Phase 3 | Final presentation & viva | 04 – 10 May 2026 |
