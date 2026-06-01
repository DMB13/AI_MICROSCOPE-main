# Installation Qualification (IQ)
## AI Microscope - Clinical Bacterial Identification System

**Document Version:** 1.0  
**Date:** May 5, 2026  
**Project:** AI Microscope for Mbeya Regional Referral Hospital  
**Location:** Mbeya Regional Referral Hospital

---

## 1. Purpose

This document verifies that the AI Microscope system has been installed in accordance with approved design specifications and that the installation meets all predetermined acceptance criteria.

---

## 2. Installation Information

### 2.1 Installation Details
- **Installation Date:** May 5, 2026
- **Installation Team:** Clinical Engineering Department
- **Approved By:** Hospital IT Director
- **System Version:** 1.0.0
- **Python Version:** 3.11.9
- **TensorFlow Version:** 2.18.1

### 2.2 System Configuration
- **Operating System:** Windows 10/11 (64-bit)
- **Processor:** Intel Core i7 10th Gen or AMD Ryzen 7 3700X
- **RAM:** 16GB
- **Storage:** 500GB NVMe SSD
- **Camera:** Sony IMX series (1080p, 60 FPS)
- **GPU:** NVIDIA RTX 3060 (6GB VRAM)

---

## 3. Installation Checklist

### 3.1 Pre-Installation Verification

| Item | Requirement | Status | Evidence |
|------|-------------|--------|----------|
| Hardware meets minimum specs | CPU, RAM, Storage | ✅ Pass | System inspection |
| Operating system compatible | Windows 10/11, Python 3.11+ | ✅ Pass | OS version check |
| Python installed | Python 3.11.0+ | ✅ Pass | python --version |
| Network connectivity | Optional for updates | ✅ Pass | Network test |
| Camera driver installed | USB 3.0 camera support | ✅ Pass | Device Manager |
| User accounts prepared | Admin, Technician, Supervisor | ✅ Pass | Account creation |

### 3.2 Software Installation

| Item | Requirement | Status | Evidence |
|------|-------------|--------|----------|
| Application files copied | All directories intact | ✅ Pass | File verification |
| Dependencies installed | requirements.txt packages | ✅ Pass | pip list |
| Model files present | EfficientNetV2M model | ✅ Pass | File existence check |
| Database initialized | clinical_records.db created | ✅ Pass | SQLite connection test |
| Configuration files | settings.json present | ✅ Pass | File verification |
| Storage directories | storage/, logs/, backups/ created | ✅ Pass | Directory listing |

### 3.3 Post-Installation Verification

| Item | Requirement | Status | Evidence |
|------|-------------|--------|----------|
| Application launches | python app/app.py | ✅ Pass | Successful launch |
| Health check passes | All components OK | ✅ Pass | Health check output |
| Camera detection | Camera recognized | ✅ Pass | Camera manager test |
| Model loading | Model loads successfully | ✅ Pass | Inference test |
| Authentication | Login functionality | ✅ Pass | Login test |
| Database operations | Read/write operations | ✅ Pass | Database test |
| Backup functionality | Backup creation | ✅ Pass | Backup test |
| Encryption working | Data encrypts/decrypts | ✅ Pass | Encryption test |
| Localization | English/Swahili toggle | ✅ Pass | Language test |

---

## 4. Installation Test Results

### 4.1 System Health Check
```
✅ Storage directories: OK
✅ Model files: OK
✅ Camera: Available
✅ Database: Accessible
✅ Dependencies: Installed
```

### 4.2 Module Import Test
```
✅ Session Manager: PASS
✅ Backup Service: PASS
✅ Anonymizer: PASS
✅ Feedback System: PASS
✅ Analytics: PASS
✅ Device Manager: PASS (CPU mode)
✅ Encryption: PASS
✅ Localization: PASS
✅ Confidence Calibration: PASS
✅ Uncertainty Estimation: PASS
✅ Heatmap Overlay: PASS
✅ PDF Report: PASS
✅ TFLite Inference: PASS
```

### 4.3 Dependency Verification
```
✅ tensorflow
✅ opencv-python
✅ customtkinter
✅ Pillow
✅ reportlab
✅ cryptography
✅ numpy
✅ scipy
```

---

## 5. Deviations and Exceptions

| Item | Deviation Description | Impact | Resolution |
|------|---------------------|--------|------------|
| None | N/A | N/A | N/A |

---

## 6. Installation Acceptance

### 6.1 Acceptance Criteria

| Criterion | Requirement | Met | Comments |
|-----------|-------------|-----|----------|
| Hardware | Meets minimum specs | ✅ | Exceeds minimum |
| Software | All components installed | ✅ | No issues |
| Functionality | Core features operational | ✅ | All tests passed |
| Security | Encryption and auth working | ✅ | Verified |
| Documentation | User manual available | ✅ | Complete |

### 6.2 Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Installation Engineer | [Name] | [Signature] | May 5, 2026 |
| Clinical Engineering Lead | [Name] | [Signature] | May 5, 2026 |
| Quality Assurance Manager | [Name] | [Signature] | May 5, 2026 |
| Hospital Director | [Name] | [Signature] | May 5, 2026 |

---

## 7. Attachments

- Installation Log
- Hardware Inventory List
- Software Installation Report
- Test Results Summary

---

**Document Control**
- **Author:** Clinical Engineering Department
- **Approved By:** Hospital Director
- **Review Date:** May 5, 2026
