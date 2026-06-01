# AI Microscope - User Training Manual

## Table of Contents
1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Getting Started](#getting-started)
4. [Basic Operations](#basic-operations)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)
8. [Safety Considerations](#safety-considerations)

---

## Introduction

### Purpose
This manual provides comprehensive training for laboratory personnel using the AI Microscope system for bacterial identification. It covers all aspects of operation from basic setup to advanced features.

### Target Audience
- Laboratory technicians
- Clinical microbiologists
- Quality control personnel
- System administrators

### Prerequisites
- Basic computer literacy
- Understanding of microbiology concepts
- Familiarity with microscope operation

---

## System Overview

### What is AI Microscope?
The AI Microscope is an AI-powered diagnostic system that:
- Captures microscope images
- Identifies bacterial species using deep learning
- Generates clinical reports
- Maintains audit trails for compliance

### System Components
- **Microscope**: Brightfield compound microscope (40x-1000x)
- **Camera**: Digital camera (1080p or higher)
- **Computer**: PC with AI analysis software
- **Software**: TensorFlow-based identification system

### Supported Bacterial Species (34 total)
- Escherichia coli
- Staphylococcus aureus
- Klebsiella pneumoniae
- Pseudomonas aeruginosa
- And 30 additional species (see model/class_indices.json)

---

## Getting Started

### Initial Setup

#### 1. Hardware Setup
1. Connect camera to microscope C-mount
2. Connect camera to computer via USB 3.0
3. Power on microscope and adjust lighting
4. Turn on computer and launch application

#### 2. Software Launch
- Windows: Run `python app/app.py` or double-click executable
- Linux: Run `python app/app.py`
- Login with credentials:
  - Admin: `admin` / `admin123`
  - Technician: `technician` / `tech123`
  - Lab Manager: `lab_manager` / `lab123`

#### 3. Camera Configuration
1. Select camera from dropdown menu
2. Click "Start Camera" button
3. Adjust focus using microscope controls
4. Verify image quality on screen

### User Roles

#### Administrator
- Full system access
- User management
- Settings configuration
- System maintenance

#### Lab Manager
- Clinical oversight
- Report approval
- Quality control
- Staff supervision

#### Technician
- Sample analysis
- Diagnosis execution
- Report generation
- Daily operations

---

## Basic Operations

### Sample Preparation

#### Microscope Slide Preparation
1. Prepare bacterial smear on glass slide
2. Apply appropriate staining (Gram stain recommended)
3. Cover with coverslip
4. Place slide on microscope stage

#### Image Capture

**Live Camera Capture:**
1. Ensure camera is running
2. Position sample using stage controls
3. Focus on bacterial cells (40x or 100x objective)
4. Click "Capture" button or press `Ctrl+C`
5. Review captured image

**Image Upload:**
1. Click "Upload Media" button or press `Ctrl+U`
2. Select image file (JPG, PNG, TIFF)
3. Click "Open" to load image
4. Adjust brightness/contrast if needed

### Running Diagnosis

#### Step-by-Step Diagnosis
1. Capture or upload sample image
2. Click "Run Diagnosis" button or press `Ctrl+D`
3. Wait for AI analysis (1-2 seconds)
4. Review results:
   - Predicted species
   - Confidence score (must be ≥90% for clinical use)
   - Grad-CAM heatmap visualization

#### Interpreting Results

**Confidence Threshold:**
- ≥90%: Clinically reliable result (green)
- 70-89%: Moderate confidence (yellow) - species name shown
- <70%: Low confidence (red) - species name hidden, repeat analysis

**Grad-CAM Heatmap:**
- Red areas: Regions most influential in prediction
- Use to verify AI is analyzing bacterial cells
- Check for artifact interference

### Saving Results

#### Automatic Database Save
- Results automatically saved to clinical_records.db
- Includes: patient ID, species, confidence, timestamp
- Requires patient ID if configured in settings

#### Export Reports
1. Click "Export Reports" button or press `Ctrl+E`
2. Select export format (CSV or PDF)
3. Choose destination folder
4. Click "Export"

---

## Advanced Features

### Image Adjustments

#### Brightness/Contrast
- Use sliders in Control Wing
- Adjust for optimal image clarity
- Changes apply to displayed image only

### Keyboard Shortcuts

| Shortcut | Function |
|----------|----------|
| Ctrl+C | Capture image |
| Ctrl+U | Upload image |
| Ctrl+D | Run diagnosis |
| Ctrl+S | Open settings |
| Ctrl+E | Export reports |
| Ctrl+Q | Quit application |
| Space | Toggle camera on/off |
| Ctrl+T | Toggle dark/light mode |

### Settings Configuration

#### Access Settings
- Click "Settings" button or press `Ctrl+S`
- Admin access required for some settings

#### Key Settings
- Patient ID requirement
- Confidence threshold
- Camera default
- Backup frequency
- Theme (dark/light)

### Authentication

#### Login
- Required on application startup
- Enter username and password
- Role determines available features

#### Logout
- Click user menu → Logout
- Returns to login screen

### Session Recovery

- Application saves session state automatically
- Camera settings preserved
- Last image path remembered
- Recovery after crash: automatic prompt

---

## Troubleshooting

### Common Issues

#### Camera Not Detected
**Symptoms:** No cameras listed in dropdown

**Solutions:**
1. Check USB cable connection
2. Try different USB port
3. Restart application
4. Verify camera drivers installed
5. Test camera on another computer

#### Image Quality Poor
**Symptoms:** Blurry or dark images

**Solutions:**
1. Adjust microscope focus
2. Clean microscope objectives
3. Increase illumination intensity
4. Clean camera lens
5. Adjust camera settings in software

#### Diagnosis Fails
**Symptoms:** Error message when running diagnosis

**Solutions:**
1. Verify image is loaded
2. Check model file exists: `model/best_clinical_rugged_1777619657.keras` (~1.2GB)
3. Ensure sufficient RAM (8GB minimum, 16GB recommended)
4. Restart application
5. Check health check logs
6. Verify TensorFlow 2.18.1 is installed

#### Low Confidence Results
**Symptoms:** Confidence <90% consistently

**Solutions:**
1. Improve image quality (better focus, lighting)
2. Ensure proper staining technique
3. Verify sample preparation
4. Check for artifacts in image
5. Use higher magnification (100x oil immersion)

#### Application Crashes
**Symptoms:** Application closes unexpectedly

**Solutions:**
1. Check system resources (CPU, RAM)
2. Review error logs in `logs/` directory
3. Restart computer
4. Verify TensorFlow installation
5. Contact technical support

### Error Messages

#### "Model not found"
- Check `model/` directory contains `best_clinical_rugged_1777619657.keras`
- Verify model file integrity (~1.2GB)
- Reinstall model if corrupted

#### "Database locked"
- Close other instances of application
- Check for database file in use
- Restart application

#### "Camera initialization failed"
- Disconnect and reconnect camera
- Restart computer with camera connected
- Update camera drivers

---

## Best Practices

### Sample Preparation
- Use consistent staining protocol
- Ensure proper smear thickness
- Allow slides to dry completely
- Use fresh stains (within expiration date)

### Image Capture
- Use appropriate magnification (40x-100x)
- Ensure proper focus before capture
- Capture multiple fields if needed
- Record magnification used

### Quality Control
- Run daily calibration checks
- Include control samples periodically
- Review low-confidence results manually
- Maintain audit trail compliance

### Data Management
- Regular database backups
- Export reports regularly
- Maintain patient confidentiality
- Follow data retention policies

### System Maintenance
- Clean microscope optics weekly
- Update software when available
- Monitor disk space
- Review logs periodically

---

## Safety Considerations

### Biological Safety
- Follow standard microbiological safety procedures
- Use appropriate PPE (lab coat, gloves, eye protection)
- Dispose of slides properly (biohazard waste)
- Disinfect microscope stage after use

### Electrical Safety
- Ensure proper grounding
- Use surge protector
- Do not expose to moisture
- Unplug during maintenance

### Data Privacy
- Protect patient information
- Use anonymization for data export
- Follow HIPAA/local regulations
- Secure access to system

### System Security
- Do not share passwords
- Log out when not in use
- Regular password changes
- Report suspicious activity

---

## Training Checklist

### Initial Training
- [ ] Hardware setup and connection
- [ ] Software installation and launch
- [ ] User authentication
- [ ] Camera operation
- [ ] Sample preparation
- [ ] Image capture
- [ ] Diagnosis execution
- [ ] Result interpretation
- [ ] Report generation
- [ ] Export functionality

### Advanced Training
- [ ] Settings configuration
- [ ] User management (admin only)
- [ ] Backup and restore
- [ ] Troubleshooting basic issues
- [ ] Keyboard shortcuts (F1 for help)
- [ ] Theme customization
- [ ] Analytics review
- [ ] Medical Help System usage

### Competency Assessment
- [ ] Complete 10 supervised diagnoses
- [ ] Demonstrate sample preparation
- [ ] Pass knowledge quiz
- [ ] Troubleshoot common issues
- [ ] Generate test reports
- [ ] Understand confidence thresholds (70% display, 90% clinical)

---

## Support Resources

### Documentation
- User Guide (this document)
- Deployment Guide
- FAQ
- Hardware Recommendations

### Technical Support
- Email: support@aimicroscope.example.com
- Phone: +1-XXX-XXX-XXXX
- Hours: 8:00 AM - 6:00 PM (local time)

### Online Resources
- Website: www.aimicroscope.example.com
- Knowledge Base: support.aimicroscope.example.com
- Video Tutorials: youtube.com/aimicroscope

---

## Version History
- v1.0 - Initial training manual
- v2.1.0 - Updated for TensorFlow 2.18.1 compatibility
- Updated model to best_clinical_rugged_1777619657.keras (34 classes)
- Added keyboard shortcuts reference (F1 for help)
- Updated confidence thresholds (70% display, 90% clinical)
- Updated user roles (admin, lab_manager, technician)
- Included troubleshooting section
