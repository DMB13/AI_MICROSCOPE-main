# Software Requirements Specification (SRS)
## AI Microscope - Clinical Bacterial Identification System

**Document Version:** 1.0  
**Date:** May 5, 2026  
**Project:** AI Microscope for Mbeya Regional Referral Hospital

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for the AI Microscope application, an AI-powered clinical bacterial identification system designed for use at Mbeya Regional Referral Hospital in Tanzania.

### 1.2 Scope
The AI Microscope system provides automated bacterial species identification from microscope images using deep learning models trained on 39 bacterial species. The system includes user authentication, role-based access control, data encryption, multi-language support (English/Swahili), and comprehensive audit trails for regulatory compliance.

### 1.3 Definitions
- **AI Model**: TensorFlow 2.18.1 with Keras 3.x, EfficientNetV2M architecture
- **Clinical Grade**: 90%+ confidence threshold for diagnostic reliability
- **TFDA**: Tanzania Food and Drugs Authority
- **EUDAMED**: European Database on Medical Devices

---

## 2. Overall Description

### 2.1 Product Perspective
The AI Microscope is a standalone desktop application that integrates with digital microscope cameras to provide real-time bacterial identification. It operates as a Computer-Aided Diagnosis (CADx) system, not as a replacement for human medical judgment.

### 2.2 Product Functions
- Real-time image capture from microscope cameras
- AI-powered bacterial species identification (39 species)
- Grad-CAM heatmap visualization for explainable AI
- Patient data management with encryption
- Role-based access control (Technician, Supervisor, Administrator)
- Audit trail logging for regulatory compliance
- Multi-language support (English/Swahili)
- PDF/CSV report generation
- Automatic database backup
- Usage analytics tracking
- Feedback system for model improvement

### 2.3 User Characteristics
- **Technicians**: Capture images, run diagnoses, view results
- **Supervisors**: Review diagnoses, access all patient data, generate reports
- **Administrators**: Manage users, configure system settings, access audit trails

### 2.4 Constraints
- Must run on Windows 10/11 with Python 3.11+
- Requires 16GB RAM for optimal performance
- GPU acceleration optional but recommended
- Must comply with TFDA medical device regulations
- Data must be encrypted at rest and in transit

### 2.5 Assumptions and Dependencies
- Users have basic computer literacy
- Microscope cameras are properly calibrated
- Network connectivity available for updates (optional)
- Regular backups of clinical data maintained

---

## 3. Specific Requirements

### 3.1 Functional Requirements

#### 3.1.1 User Authentication
- **FR-1**: System shall require user login with username and password
- **FR-2**: System shall support three user roles: Technician, Supervisor, Administrator
- **FR-3**: System shall enforce role-based permissions
- **FR-4**: System shall log all authentication attempts in audit trail

#### 3.1.2 Image Capture
- **FR-5**: System shall support USB microscope cameras
- **FR-6**: System shall support multiple camera configurations
- **FR-7**: System shall support image upload from file system
- **FR-8**: System shall capture images at minimum 1080p resolution

#### 3.1.3 AI Inference
- **FR-9**: System shall identify bacterial species from images
- **FR-10**: System shall support 39 bacterial species
- **FR-11**: System shall provide confidence scores for predictions
- **FR-12**: System shall flag predictions below 90% confidence
- **FR-13**: System shall support GPU acceleration with CPU fallback
- **FR-14**: System shall support TFLite quantized models

#### 3.1.4 Explainable AI
- **FR-15**: System shall generate Grad-CAM heatmaps
- **FR-16**: System shall provide side-by-side original + heatmap view
- **FR-17**: System shall support heatmap opacity adjustment

#### 3.1.5 Data Management
- **FR-18**: System shall store patient records in SQLite database
- **FR-19**: System shall encrypt patient data at rest
- **FR-20**: System shall support patient data anonymization
- **FR-21**: System shall require patient ID for diagnosis (configurable)
- **FR-22**: System shall automatically backup database daily

#### 3.1.6 Reporting
- **FR-23**: System shall generate PDF clinical reports
- **FR-24**: System shall export data to CSV format
- **FR-25**: System shall include facility information in reports
- **FR-26**: System shall include disclaimer in all reports

#### 3.1.7 Localization
- **FR-27**: System shall support English language
- **FR-28**: System shall support Swahili language
- **FR-29**: System shall allow language switching at runtime

#### 3.1.8 Quality Assurance
- **FR-30**: System shall perform health checks on startup
- **FR-31**: System shall warm up AI model on startup
- **FR-32**: System shall implement confidence calibration
- **FR-33**: System shall provide uncertainty estimation (Monte Carlo dropout)

### 3.2 Non-Functional Requirements

#### 3.2.1 Performance
- **NFR-1**: Inference time < 3 seconds per image (GPU) or < 10 seconds (CPU)
- **NFR-2**: Application startup time < 30 seconds
- **NFR-3**: Support concurrent operation without performance degradation

#### 3.2.2 Reliability
- **NFR-4**: System uptime > 99%
- **NFR-5**: Mean time between failures > 100 hours
- **NFR-6**: Automatic crash recovery with session state restoration

#### 3.2.3 Security
- **NFR-7**: Passwords stored using bcrypt hashing
- **NFR-8**: Data encrypted using Fernet (AES-128)
- **NFR-9**: Audit trail logging for all user actions
- **NFR-10**: Session timeout after 30 minutes of inactivity

#### 3.2.4 Usability
- **NFR-11**: Intuitive GUI with dark/light mode toggle
- **NFR-12**: Keyboard shortcuts for common operations
- **NFR-13**: First-run setup wizard for initial configuration
- **NFR-14**: User training manual provided

#### 3.2.5 Maintainability
- **NFR-15**: Modular architecture with clear separation of concerns
- **NFR-16**: Comprehensive logging with rotation
- **NFR-17**: Type hints on all functions
- **NFR-18**: Docstrings on all functions

### 3.3 External Interface Requirements

#### 3.3.1 User Interfaces
- CustomTkinter-based GUI
- Responsive design for 1024x768 minimum resolution
- Touch-friendly controls for tablet deployment

#### 3.3.2 Hardware Interfaces
- USB 3.0 camera support
- GPU acceleration (NVIDIA CUDA, optional)
- Minimum 8GB RAM (16GB recommended)

#### 3.3.3 Software Interfaces
- Python 3.11.0+
- TensorFlow 2.18.1 with Keras 3.x
- OpenCV 4.8+
- SQLite 3

---

## 4. System Attributes

### 4.1 Availability
System shall be available 24/7 for clinical operations with scheduled maintenance windows.

### 4.2 Security
Compliance with:
- TFDA medical device regulations
- ISO 13485 quality management
- ISO 14971 risk management
- HIPAA-like data protection standards

### 4.3 Maintainability
Modular design allows for:
- Easy model updates
- Feature additions
- Bug fixes
- Regulatory compliance updates

---

## 5. Verification

### 5.1 Testing Requirements
- Unit tests for all core functions
- Integration tests for camera and inference
- Performance benchmarks
- Security penetration testing
- User acceptance testing

### 5.2 Validation Requirements
- Clinical validation with known samples
- Accuracy verification against manual identification
- Regulatory compliance audit

---

## 6. Appendices

### Appendix A: Bacterial Species List
The system identifies the following 39 bacterial species:
- Escherichia coli
- Staphylococcus aureus
- Klebsiella pneumoniae
- [Complete list in model documentation]

### Appendix B: Regulatory References
- TFDA Guidelines for Medical Device Software
- IEC 62304 Medical Device Software Lifecycle
- ISO 14971 Medical Device Risk Management

---

**Document Control**
- **Author**: AI Microscope Development Team
- **Approved By**: Clinical Engineering Department
- **Review Date**: May 5, 2026
- **Next Review**: November 5, 2026
