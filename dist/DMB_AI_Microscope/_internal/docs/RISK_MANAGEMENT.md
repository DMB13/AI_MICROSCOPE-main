# Risk Management File (ISO 14971)
## AI Microscope - Clinical Bacterial Identification System

**Document Version:** 1.0  
**Date:** May 5, 2026  
**Project:** AI Microscope for Mbeya Regional Referral Hospital  
**Standard:** ISO 14971:2019 Medical devices - Application of risk management to medical devices

---

## 1. Scope

This document describes the risk management process for the AI Microscope, a Computer-Aided Diagnosis (CADx) medical device software intended for bacterial identification from microscope images.

---

## 2. Risk Management Process

### 2.1 Risk Analysis

#### Risk Identification

| ID | Hazard Description | Potential Harm | Affected Stakeholders | Probability | Severity |
|----|-------------------|---------------|----------------------|------------|----------|
| R1 | Incorrect bacterial identification | Misdiagnosis, inappropriate treatment | Patient | Medium | High |
| R2 | System failure during diagnosis | Delayed diagnosis | Patient | Low | Medium |
| R3 | Data breach of patient information | Privacy violation, regulatory penalty | Patient, Hospital | Low | High |
| R4 | Unauthorized access to system | Data tampering, fraud | Hospital | Low | Medium |
| R5 | Loss of clinical data | Loss of diagnostic history | Hospital | Medium | Medium |
| R6 | Model bias/underperformance | Systematic misdiagnosis | Patient population | Low | High |
| R7 | Hardware malfunction (camera) | Inability to capture images | Patient, Technician | Medium | Low |
| R8 | Poor image quality (focus, lighting) | False diagnosis | Patient | High | Medium |
| R9 | User error (incorrect operation) | Incorrect diagnosis | Patient | Medium | Medium |
| R10 | Software bug/crash | System unavailability | Patient, Hospital | Low | Medium |

### 2.2 Risk Estimation

#### Risk Evaluation Matrix

| Severity \ Probability | Low | Medium | High |
|----------------------|-----|--------|------|
| **Catastrophic** | Medium | High | Unacceptable |
| **High** | Low | Medium | High |
| **Medium** | Low | Low | Medium |
| **Low** | Acceptable | Low | Low |

#### Risk Ratings

| Risk ID | Description | Probability | Severity | Risk Rating | Acceptable |
|---------|-------------|------------|----------|-------------|------------|
| R1 | Incorrect identification | Medium | High | Medium | No |
| R2 | System failure | Low | Medium | Low | Yes |
| R3 | Data breach | Low | High | Medium | No |
| R4 | Unauthorized access | Low | Medium | Low | Yes |
| R5 | Data loss | Medium | Medium | Medium | No |
| R6 | Model bias | Low | High | Medium | No |
| R7 | Camera failure | Medium | Low | Low | Yes |
| R8 | Poor image quality | High | Medium | Medium | No |
| R9 | User error | Medium | Medium | Medium | No |
| R10 | Software bug | Low | Medium | Low | Yes |

---

## 3. Risk Control

### 3.1 Risk Control Measures

#### R1: Incorrect Bacterial Identification

**Risk Control Measures:**
- 90% confidence threshold implementation
- Confidence calibration using temperature scaling
- Uncertainty estimation via Monte Carlo dropout
- Grad-CAM heatmap for human verification
- Inconclusive result flagging for low confidence
- Clinical validation with expert review

**Residual Risk:** Low

#### R3: Data Breach

**Risk Control Measures:**
- AES-128 encryption for sensitive fields (patient_name, patient_id, notes)
- Role-based access control
- Audit trail for all data access
- Secure password storage (bcrypt, cost factor 12)
- Session timeout after 30 minutes
- Regular security audits

**Residual Risk:** Low

#### R5: Data Loss

**Risk Control Measures:**
- Automatic daily database backups
- GZIP compression for backup files
- Retention of 10 backup versions
- Backup integrity verification
- Cloud backup option (configurable)
- Database recovery procedures

**Residual Risk:** Low

#### R6: Model Bias

**Risk Control Measures:**
- Diverse training dataset
- Regular model performance monitoring
- Feedback system for wrong predictions
- Model retraining with new data
- Confidence calibration
- Uncertainty estimation

**Residual Risk:** Low

#### R8: Poor Image Quality

**Risk Control Measures:**
- Image quality assessment before inference
- Real-time image preview
- Focus and lighting guidelines in training manual
- Image quality metrics in feedback
- User training on proper microscopy technique

**Residual Risk:** Low

#### R9: User Error

**Risk Control Measures:**
- Intuitive GUI design
- First-run setup wizard
- Comprehensive user training manual
- Role-based permissions
- Audit trail for accountability
- Error prevention in workflow

**Residual Risk:** Low

---

## 4. Overall Residual Risk Evaluation

### 4.1 Risk Summary

| Category | Total Risks | Controlled | Residual Risk Level |
|----------|-------------|------------|-------------------|
| Clinical Safety | 4 | 4 | Low |
| Data Security | 2 | 2 | Low |
| System Reliability | 2 | 2 | Low |
| Usability | 2 | 2 | Low |

### 4.2 Risk-Benefit Analysis

**Benefits:**
- Rapid bacterial identification (seconds vs hours/days)
- High accuracy (90%+ confidence threshold)
- Consistent results independent of operator skill
- Explainable AI with Grad-CAM visualization
- Reduced diagnostic errors through AI assistance
- Improved patient outcomes through faster treatment

**Risks:**
- Potential for misidentification (mitigated by confidence threshold)
- Data privacy concerns (mitigated by encryption)
- System availability (mitigated by backup and recovery)

**Conclusion:** Benefits outweigh residual risks when all control measures are implemented.

---

## 5. Risk Management Review

### 5.1 Review Schedule
- **Initial Review:** May 5, 2026
- **Quarterly Review:** Every 3 months
- **Annual Comprehensive Review:** November 5, 2026
- **Post-Update Review:** After any major software update

### 5.2 Review Criteria
- Effectiveness of control measures
- New risk identification
- Changes in clinical environment
- Regulatory updates
- User feedback and incident reports

---

## 6. Post-Production Information

### 6.1 Incident Reporting
All incidents must be reported to:
- Clinical Engineering Department
- Quality Assurance Manager
- Risk Management Committee

### 6.2 Incident Investigation
- Root cause analysis
- Impact assessment
- Corrective actions
- Preventive measures
- Documentation updates

### 6.3 Risk Management File Updates
This document shall be updated when:
- New risks are identified
- Control measures are modified
- Residual risk levels change
- Regulatory requirements change

---

## 7. Appendices

### Appendix A: Risk Management Team
- **Risk Manager:** Clinical Engineering Director
- **Clinical Lead:** Head of Laboratory
- **Software Lead:** Development Team Lead
- **Quality Manager:** QA Manager

### Appendix B: References
- ISO 14971:2019 Medical devices - Application of risk management
- IEC 62304 Medical device software - Software life cycle processes
- TFDA Guidelines for Medical Device Software
- IEC 80001-1 Application of risk management for IT-networks

---

**Document Control**
- **Author:** Risk Management Committee
- **Approved By:** Clinical Engineering Director
- **Review Date:** May 5, 2026
- **Next Review:** August 5, 2026
