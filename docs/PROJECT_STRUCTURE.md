# AI Microscope - Project Structure

**Version:** 2.1.0  
**Last Updated:** May 27, 2026

## 📁 Root Directory
```
AI_MICROSCOPE-main/
├── 📄 .gitignore                    # Git ignore rules
├── 📄 Dockerfile                    # Docker configuration
├── 📄 LICENSE                       # MIT License
├── 📄 README.md                     # Project documentation
├── 📄 requirements.txt              # Python dependencies (TF 2.18.1)
├── � main.py                      # Entry point
├── 📄 clinical_records.db           # SQLite clinical database
├── �📁 app/                         # Application GUI and settings
├── 📁 build/                       # Build scripts and installer config
├── 📁 config/                      # Configuration and constants
├── 📁 core/                        # Core services (auth, audit, backup, etc.)
├── 📁 docs/                        # Documentation suite
├── 📁 exports/                     # Export directory for reports
├── 📁 gui/                         # GUI components, views, and controllers
├── 📁 hardware/                    # Camera hardware interface
├── 📁 inference/                   # AI inference engine
├── 📁 model/                       # Model files and database ops
├── 📁 storage/                     # Session state and backups
├── 📁 utils/                       # Utilities (logger, error handling, markdown)
└── 📁 vision/                      # Vision inference wrapper
```

## 📁 app/ - Application Layer
```
app/
├── 📄 __init__.py                 # Package initialization
├── 📄 __main__.py                 # Module entry point
├── 📄 app.py                     # Main GUI application (3-column dashboard)
├── 📄 services.py                # Service initialization
├── 📄 settings_dialog.py          # Settings GUI dialog (medical-grade)
├── 📄 settings_manager.py         # Settings management system
└── 📄 microscope_settings.json    # Application settings (persisted)
```

## 📁 gui/ - GUI Components, Views & Controllers
```
gui/
├── � components/                 # Reusable UI components
│   ├── �📄 camera_controls.py      # Camera selection and control
│   ├── 📄 clinical_status_bar.py  # Clinical status bar (bottom)
│   ├── 📄 documentation_viewer.py # Documentation viewer
│   ├── 📄 export_dialog.py        # Export dialog with time period selection
│   ├── 📄 first_run_wizard.py     # First-run setup wizard
│   ├── 📄 image_adjustments.py    # Brightness/contrast controls
│   ├── 📄 image_display.py        # Image display widget
│   ├── 📄 loading_spinner.py      # Loading spinner
│   ├── 📄 login_dialog.py         # Login/registration with role selection
│   ├── 📄 medical_help_system.py  # In-app medical help system (F1)
│   ├── 📄 patient_input.py        # Patient ID input
│   ├── 📄 patient_safety_dialog.py # Patient safety dialogs
│   ├── 📄 results_display.py      # Results with confidence color-coding
│   └── 📄 user_profile_dialog.py  # User profile management
├── 📁 views/                      # Main layout views
│   ├── 📄 control_wing.py         # Column 0: Control Wing
│   ├── 📄 primary_viewport.py     # Column 1: Microscope Viewport
│   └── 📄 intelligence_wing.py    # Column 2: Intelligence Wing
└── 📁 controllers/                # Business logic controllers
    ├── 📄 camera_controller.py     # Camera operations
    ├── 📄 diagnosis_controller.py  # AI diagnosis with clinical recommendations
    └── 📄 export_controller.py     # Export operations (CSV/PDF)
```

## 📁 core/ - Core Services
```
core/
├── 📄 analytics.py               # Usage analytics tracking
├── 📄 anonymizer.py              # Patient data anonymization
├── 📄 audit_trail.py             # Audit trail with medical fields
├── 📄 auth.py                    # Authentication (login, registration, roles)
├── 📄 auto_update.py             # Auto-update mechanism
├── 📄 backup_service.py          # Automatic database backup
├── 📄 confidence_calibration.py  # Confidence calibration
├── 📄 device_manager.py          # Device management
├── 📄 encryption.py              # Data encryption at rest
├── 📄 feedback_system.py         # Feedback for wrong predictions
├── 📄 health_check.py            # Startup health check service
├── 📄 heatmap_overlay.py         # Grad-CAM heatmap overlay
├── 📄 localization.py            # Multi-language support
├── 📄 pdf_report.py              # Professional PDF report generation
├── 📄 session_manager.py         # Session state and crash recovery
├── 📄 tfda_compliance.py         # TFDA regulatory compliance
├── 📄 tflite_inference.py        # TFLite quantized model support
└── 📄 uncertainty_estimation.py  # Monte Carlo dropout uncertainty
```

## 📁 model/ - Model & Database
```
model/
├── 📄 __init__.py                 # Package initialization
├── 🧠 best_clinical_rugged_1777619657.keras  # Trained AI model (~1.2GB)
├── 📄 class_indices.json           # 34 bacterial species mapping
├── � db.py                       # Database operations
├── 📄 model_config.py             # Model configuration
├── 📄 export_manager.py           # Export manager
├── 📄 report.py                   # Report generation
├── 📄 types.py                    # Type definitions
└── 📁 records/                    # Captured images storage
```

## 📁 build/ - Build & Packaging
```
build/
├── 📄 build_exe.py               # PyInstaller build script
├── 📄 build_exe_file.spec         # PyInstaller spec file
├── 📄 hook-settings_dialog.py     # Custom PyInstaller hook
└── 📄 installer.iss              # Inno Setup installer script
```

## 📁 config/ - Configuration
```
config/
├── 📄 constants.py               # Centralized constants
└── 📄 settings.py                # Settings configuration
```

## 📁 Other Directories
```
inference/                        # Legacy AI inference engine
├── 📄 __init__.py
└── � inference.py               # Core inference logic

hardware/
└── 📄 camera.py                  # Camera hardware interface

storage/
├── 📄 export.py                  # Export storage
├── 📄 repository.py              # Data repository
├── 📁 backups/                   # Automatic database backups
└── 📄 session_state.json         # Session persistence

utils/
├── � error_handling.py          # Error handling utilities
├── 📄 logger.py                  # Structured logging with rotation
└── 📄 markdown_converter.py      # Markdown to HTML converter

vision/
└── 📄 inference_wrapper.py       # Vision inference wrapper

exports/
├── 📄 clinical_export_*.csv      # CSV exports
└── 📄 clinical_export_*.pdf      # PDF reports
```

## 🔧 Current System Specifications
- **Model**: EfficientNetV2M (Clinical Rugged)
- **Model File**: best_clinical_rugged_1777619657.keras (~1.2GB)
- **Input Size**: 224x224 RGB images
- **Output Classes**: 34 bacterial species
- **Framework**: TensorFlow 2.18.1 with Keras 3.x
- **GUI**: CustomTkinter 5.2.2 (3-column dashboard)
- **Database**: SQLite with automatic backups
- **Authentication**: Role-based (admin, technician, lab_manager)
- **Clinical Threshold**: 90% confidence for clinical acceptance
- **Species Display**: Hidden when confidence < 70%

## 🚀 Ready for Deployment
Launch command:
```bash
python app/app.py
```

Build executable:
```bash
python build/build_exe.py
```

Total project size: ~1.3GB (mostly model file)
