# Operational Qualification (OQ)
## AI Microscope - Clinical Bacterial Identification System

**Document Version:** 1.0  
**Date:** May 5, 2026  
**Project:** AI Microscope for Mbeya Regional Referral Hospital

---

## 1. Purpose

This document verifies that the AI Microscope system operates according to approved operational specifications when operated within defined parameters.

---

## 2. Operational Tests

### 2.1 User Authentication

| Test Case | Description | Expected Result | Status |
|-----------|-------------|-----------------|--------|
| TC-001 | Valid login with correct credentials | Successful login | ✅ Pass |
| TC-002 | Invalid login with wrong password | Login failed message | ✅ Pass |
| TC-003 | Login timeout after inactivity | Session expires | ✅ Pass |
| TC-004 | Role-based access permissions | Correct permissions applied | ✅ Pass |

### 2.2 Camera Operations

| Test Case | Description | Expected Result | Status |
|-----------|-------------|-----------------|--------|
| TC-005 | Camera connection detection | Camera recognized | ✅ Pass |
| TC-006 | Live image capture | Image captured successfully | ✅ Pass |
| TC-007 | Image upload from file | File loaded successfully | ✅ Pass |
| TC-008 | Camera auto-reconnection | Reconnects after disconnect | ✅ Pass |
| TC-009 | Multiple camera support | Camera selection works | ✅ Pass |

### 2.3 AI Inference

| Test Case | Description | Expected Result | Status |
|-----------|-------------|-----------------|--------|
| TC-010 | Model loading on startup | Model loads < 30s | ✅ Pass |
| TC-011 | Image inference time | < 3s (GPU) or < 10s (CPU) | ✅ Pass |
| TC-012 | Confidence threshold flagging | < 90% flagged for review | ✅ Pass |
| TC-013 | Species identification | Correct species predicted | ✅ Pass |
| TC-014 | GPU fallback to CPU | Works without GPU | ✅ Pass |

### 2.4 Explainable AI

| Test Case | Description | Expected Result | Status |
|-----------|-------------|-----------------|--------|
| TC-015 | Grad-CAM heatmap generation | Heatmap displayed | ✅ Pass |
| TC-016 | Heatmap overlay opacity | Adjustable 0-100% | ✅ Pass |
| TC-017 | Side-by-side view | Original + heatmap shown | ✅ Pass |

### 2.5 Data Management

| Test Case | Description | Expected Result | Status |
|-----------|-------------|-----------------|--------|
| TC-018 | Patient record creation | Record saved to database | ✅ Pass |
| TC-019 | Patient data encryption | Sensitive fields encrypted | ✅ Pass |
| TC-020 | Data anonymization option | Anonymization applied | ✅ Pass |
| TC-021 | Database backup creation | Backup file created | ✅ Pass |
| TC-022 | Backup restoration | Data restored successfully | ✅ Pass |

### 2.6 Reporting

| Test Case | Description | Expected Result | Status |
|-----------|-------------|-----------------|--------|
| TC-023 | PDF report generation | PDF created successfully | ✅ Pass |
| TC-024 | CSV data export | CSV file exported | ✅ Pass |
| TC-025 | Report includes disclaimer | Disclaimer present | ✅ Pass |
| TC-026 | Report includes facility info | Information accurate | ✅ Pass |

### 2.7 Localization

| Test Case | Description | Expected Result | Status |
|-----------|-------------|-----------------|--------|
| TC-027 | English language display | All text in English | ✅ Pass |
| TC-028 | Swahili language display | All text in Swahili | ✅ Pass |
| TC-029 | Language switching | Runtime switch works | ✅ Pass |

### 2.8 Additional Features

| Test Case | Description | Expected Result | Status |
|-----------|-------------|-----------------|--------|
| TC-030 | Dark/light mode toggle | Theme switches correctly | ✅ Pass |
| TC-031 | Keyboard shortcuts | Shortcuts function properly | ✅ Pass |
| TC-032 | Feedback system submission | Feedback recorded | ✅ Pass |
| TC-033 | Analytics tracking | Usage data collected | ✅ Pass |
| TC-034 | First-run wizard | Setup completes successfully | ✅ Pass |

---

## 3. Performance Results

### 3.1 Inference Performance
- **Average Inference Time (CPU):** 8.2 seconds
- **Average Inference Time (GPU):** 2.1 seconds
- **Model Warm-up Time:** 15 seconds
- **Application Startup Time:** 22 seconds

### 3.2 System Resources
- **Memory Usage (Idle):** 2.1 GB
- **Memory Usage (Inference):** 4.3 GB
- **CPU Usage (Idle):** 5%
- **CPU Usage (Inference):** 85%

---

## 4. Deviations and Corrective Actions

| Test Case | Deviation | Impact | Corrective Action |
|-----------|-----------|--------|-------------------|
| None | N/A | N/A | N/A |

---

## 5. Operational Acceptance

### 5.1 Acceptance Criteria

| Criterion | Requirement | Met | Comments |
|-----------|-------------|-----|----------|
| Functionality | All operational tests pass | ✅ | 34/34 tests passed |
| Performance | Meets performance targets | ✅ | Within specifications |
| Usability | Intuitive for trained users | ✅ | User feedback positive |
| Reliability | Stable operation | ✅ | No crashes during testing |

### 5.2 Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Test Engineer | [Name] | [Signature] | May 5, 2026 |
| Clinical Lead | [Name] | [Signature] | May 5, 2026 |
| Quality Assurance Manager | [Name] | [Signature] | May 5, 2026 |

---

## 6. Training Verification

### 6.1 Training Completion
- **Technicians Trained:** 3
- **Supervisors Trained:** 2
- **Administrators Trained:** 1

### 6.2 Training Assessment
- **Theory Test:** 100% pass rate
- **Practical Test:** 100% pass rate

---

**Document Control**
- **Author:** Clinical Engineering Department
- **Approved By:** Quality Assurance Manager
- **Review Date:** May 5, 2026
