# Software Design Specification (SDS)
## AI Microscope - Clinical Bacterial Identification System

**Document Version:** 1.0  
**Date:** May 5, 2026  
**Project:** AI Microscope for Mbeya Regional Referral Hospital

---

## 1. System Architecture

### 1.1 High-Level Architecture
The AI Microscope follows a layered architecture pattern:

```
┌─────────────────────────────────────────┐
│         GUI Layer (CustomTkinter)       │
├─────────────────────────────────────────┤
│      Application Layer (app/)          │
├─────────────────────────────────────────┤
│      Business Logic Layer (core/)      │
├─────────────────────────────────────────┤
│      Vision Layer (vision/)            │
├─────────────────────────────────────────┤
│      Hardware Layer (hardware/)        │
├─────────────────────────────────────────┤
│      Utilities Layer (utils/)          │
└─────────────────────────────────────────┘
```

### 1.2 Module Organization

#### Core Modules (`core/`)
- `auth_service.py` - User authentication and authorization
- `session_manager.py` - Session state management
- `backup_service.py` - Database backup automation
- `anonymizer.py` - Patient data anonymization
- `feedback_system.py` - Feedback collection for model improvement
- `analytics.py` - Usage analytics tracking
- `device_manager.py` - GPU/CPU device management
- `encryption.py` - Data encryption at rest
- `localization.py` - Multi-language support (EN/SW)
- `confidence_calibration.py` - Model confidence calibration
- `uncertainty_estimation.py` - Monte Carlo dropout uncertainty
- `heatmap_overlay.py` - Heatmap visualization with opacity
- `pdf_report.py` - PDF report generation
- `tflite_inference.py` - TFLite quantized model support

#### Vision Modules (`vision/`)
- `inference_wrapper.py` - AI model inference wrapper
- `gradcam.py` - Grad-CAM heatmap generation

#### Hardware Modules (`hardware/`)
- `camera_manager.py` - Camera control and management
- `retry_handler.py` - Exponential backoff retry logic

#### GUI Components (`gui/components/`)
- `first_run_wizard.py` - Initial setup wizard
- Authentication dialogs
- Main application interface

---

## 2. Data Design

### 2.1 Database Schema

#### Clinical Records Table
```sql
CREATE TABLE clinical_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    patient_id TEXT,
    patient_name TEXT,
    age INTEGER,
    sex TEXT,
    species TEXT,
    confidence REAL,
    image_path TEXT,
    notes TEXT,
    user_id TEXT
);
```

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 File Structure
```
AI_MICROSCOPE-main/
├── app/                    # Application layer
├── core/                   # Business logic
├── gui/                    # User interface
├── hardware/               # Hardware interfaces
├── vision/                 # Computer vision
├── utils/                  # Utilities
├── model/                  # AI model files
├── storage/                # Runtime data
│   ├── clinical_records.db
│   ├── session_state.json
│   ├── audit_trail.json
│   ├── analytics.json
│   ├── feedback.json
│   └── backups/
├── logs/                   # Application logs
├── docs/                   # Documentation
├── tests/                  # Test suite
├── deploy/                 # Deployment scripts
└── build/                  # Build artifacts
```

---

## 3. Component Design

### 3.1 Authentication Service
**Class:** `AuthService`

**Methods:**
- `authenticate(username, password)` - Verify credentials
- `create_user(username, password, role)` - Create new user
- `get_user_role(user_id)` - Get user role
- `hash_password(password)` - Hash password with bcrypt
- `verify_password(password, hash)` - Verify password

**Dependencies:**
- `bcrypt` for password hashing
- SQLite for user storage

### 3.2 Session Manager
**Class:** `SessionManager`

**Methods:**
- `save_state(key, value)` - Save session state
- `get_state(key)` - Retrieve session state
- `auto_save()` - Periodic auto-save
- `load_on_startup()` - Restore session on startup

**File:** `storage/session_state.json`

### 3.3 Backup Service
**Class:** `BackupService`

**Methods:**
- `create_backup()` - Create database backup
- `auto_backup()` - Scheduled automatic backup
- `cleanup_old_backups()` - Remove old backups
- `restore_backup(backup_path)` - Restore from backup

**Backup Format:** GZIP compressed SQLite database

### 3.4 Device Manager
**Class:** `DeviceManager`

**Methods:**
- `_check_gpu_available()` - Detect GPU
- `select_device()` - Choose GPU or CPU
- `force_cpu()` - Force CPU mode
- `configure_for_inference()` - Optimize TensorFlow settings

**GPU Detection:** TensorFlow physical device enumeration

### 3.5 Encryption Service
**Class:** `EncryptionService`

**Methods:**
- `encrypt(data)` - Encrypt string data
- `decrypt(encrypted_data)` - Decrypt data
- `encrypt_dict(data, keys)` - Encrypt specific keys in dictionary
- `decrypt_dict(data, keys)` - Decrypt specific keys

**Algorithm:** Fernet (AES-128) from cryptography library

### 3.6 Localization Service
**Class:** `Localization`

**Methods:**
- `set_language(language)` - Set current language
- `get(key)` - Get translation for key
- `translate(key, **kwargs)` - Get translation with placeholders

**Languages:** English, Swahili

### 3.7 Confidence Calibrator
**Class:** `ConfidenceCalibrator`

**Methods:**
- `fit(logits, labels)` - Fit calibrator with validation data
- `calibrate(logits)` - Calibrate confidence scores
- `_negative_log_likelihood(temp, logits, labels)` - Temperature scaling

**Methods:** Temperature scaling, Isotonic regression

### 3.8 Uncertainty Estimator
**Class:** `UncertaintyEstimator`

**Methods:**
- `enable_mc_dropout()` - Enable dropout during inference
- `disable_mc_dropout()` - Disable dropout
- `predict_with_uncertainty(image)` - Predict with uncertainty metrics
- `is_prediction_reliable(uncertainty)` - Check reliability

**Technique:** Monte Carlo Dropout (30 samples)

### 3.9 Heatmap Overlay
**Class:** `HeatmapOverlay`

**Methods:**
- `set_opacity(opacity)` - Set overlay opacity (0-1)
- `overlay_heatmap(original, heatmap)` - Blend images
- `create_side_by_side(original, heatmap)` - Create comparison view
- `save_side_by_side(original_path, heatmap, output_path)` - Save to file

**Colormap:** JET (default), customizable

### 3.10 PDF Report Generator
**Class:** `PDFReportGenerator`

**Methods:**
- `generate_report(output_path, diagnosis_data, image_path)` - Generate PDF
- `_add_custom_styles()` - Add report styles

**Library:** ReportLab

---

## 4. Interface Design

### 4.1 GUI Components

#### Main Window
- **Control Wing:** Camera controls, image capture/upload
- **Primary Viewport:** Live camera feed or loaded image
- **Intelligence Wing:** AI results, Grad-CAM heatmap
- **Settings Panel:** User preferences, language selection

#### First-Run Wizard
1. Welcome screen with feature overview
2. Language selection (English/Swahili)
3. Camera configuration
4. Clinical settings (patient ID requirement)
5. Completion summary

### 4.2 API Interfaces

#### Internal APIs
- Camera Manager API for hardware abstraction
- Inference Wrapper API for model access
- Database API for data persistence

#### External APIs (Future)
- Cloud backup API
- Update server API

---

## 5. Security Design

### 5.1 Authentication
- Password hashing with bcrypt (cost factor 12)
- Session timeout after 30 minutes
- Audit trail for all authentication events

### 5.2 Data Encryption
- Fernet (AES-128) encryption for sensitive fields
- Encryption keys stored securely or derived from password
- Encrypted columns: patient_name, patient_id, notes

### 5.3 Access Control
- Role-based permissions:
  - **Technician:** Capture images, run diagnoses, view own results
  - **Supervisor:** Review all diagnoses, generate reports
  - **Administrator:** Manage users, configure system

### 5.4 Audit Trail
- All user actions logged with timestamp and user ID
- Audit log stored in `storage/audit_trail.json`
- Immutable log entries

---

## 6. Performance Design

### 6.1 Optimization Strategies
- **Model Warm-up:** Pre-load model on startup
- **GPU Acceleration:** Automatic GPU detection with CPU fallback
- **TFLite Support:** Quantized models for edge deployment
- **Lazy Loading:** Load modules only when needed

### 6.2 Performance Targets
- Inference: < 3 seconds (GPU), < 10 seconds (CPU)
- Startup: < 30 seconds
- Image capture: < 1 second
- Report generation: < 5 seconds

---

## 7. Error Handling

### 7.1 Error Categories
- **Hardware Errors:** Camera disconnection, GPU failure
- **Model Errors:** Model loading failure, inference errors
- **Data Errors:** Database corruption, missing files
- **User Errors:** Invalid inputs, authentication failures

### 7.2 Recovery Strategies
- **Retry Logic:** Exponential backoff for hardware
- **Graceful Degradation:** CPU fallback when GPU unavailable
- **Session Recovery:** Auto-save and crash recovery
- **Backup Restoration:** Automatic backup restoration on corruption

---

## 8. Testing Strategy

### 8.1 Unit Tests
- All core functions
- Individual module functionality
- Edge cases and error conditions

### 8.2 Integration Tests
- Camera + inference pipeline
- Database operations
- Authentication flow
- Backup/restore operations

### 8.3 Performance Tests
- Inference latency benchmarks
- Memory usage profiling
- Stress testing with concurrent operations

---

## 9. Deployment Design

### 9.1 Deployment Options
- **Development:** Direct Python execution
- **Production:** PyInstaller single executable
- **Enterprise:** Windows installer (Inno Setup)

### 9.2 Deployment Artifacts
- `deploy/deploy_windows.bat` - Windows deployment script
- `deploy/deploy_linux.sh` - Linux deployment script
- `build/ai_microscope.iss` - Inno Setup installer script

---

## 10. Maintenance Design

### 10.1 Logging
- Structured logging with rotation (10MB max, 5 backups)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log location: `logs/` directory

### 10.2 Monitoring
- Health check on startup
- Analytics tracking for usage monitoring
- Error reporting via logs

### 10.3 Updates
- Model updates via replacement
- Configuration updates via settings.json
- Software updates via auto-update mechanism (future)

---

**Document Control**
- **Author:** AI Microscope Development Team
- **Approved By:** Clinical Engineering Department
- **Review Date:** May 5, 2026
- **Next Review:** November 5, 2026
