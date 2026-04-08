# AI Microscope - Deployment Guide

## 🚀 Deployment Overview

This guide provides step-by-step instructions for deploying AI Microscope in a clinical environment at Mbeya Regional Referral Hospital.

---

## 📋 Pre-Deployment Checklist

### System Requirements Verification
- [ ] **Operating System**: Ubuntu 18.04 LTS or later
- [ ] **Hardware**: Minimum 4GB RAM, recommended 8GB+
- [ ] **Storage**: 2GB free disk space
- [ ] **Camera**: Compatible USB microscope or camera
- [ ] **Display**: 1024x768 minimum resolution
- [ ] **Network**: Optional, for updates and remote support

### Software Dependencies
- [ ] **Python 3.11+**: Installed and configured
- [ ] **Virtual Environment**: Created and activated
- [ ] **GPU Drivers**: Optional, for performance optimization
- [ ] **Camera Drivers**: Properly installed and tested

### Staff Preparation
- [ ] **Training**: Staff trained on microscope operation
- [ ] **User Accounts**: System accounts created for users
- [ ] **Permissions**: File system permissions configured
- [ ] **Backup Plan**: Data backup procedures established

---

## 🔧 Installation Process

### Step 1: System Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system dependencies
sudo apt install -y python3.11 python3.11-venv python3-tk
sudo apt install -y cmake build-essential pkg-config
sudo apt install -y libjpeg-dev libtiff-dev libpng-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y libgtk2.0-dev libcanberra-gtk-module
sudo apt install -y libxvidcore-dev libx264-dev
```

### Step 2: Application Setup
```bash
# Navigate to installation directory
cd /opt/ai-microscope  # or chosen location

# Extract application files
# (assuming files are copied from source)

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Model Configuration
```bash
# Verify model file exists
ls -la model/best_microscope_fusion.keras

# Check class indices file
ls -la model/class_indices.json

# Test model loading
python -c "from inference.inference import load_model; print('Model OK')"
```

### Step 4: Camera Setup
```bash
# Test camera detection
python -c "
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f'Camera {i}: Available')
        cap.release()
    else:
        print(f'Camera {i}: Not available')
"
```

### Step 5: Database Initialization
```bash
# Test database creation
python -c "
from model.db import get_db
db = get_db()
print('Database initialized successfully')
"
```

---

## 🏥 Clinical Configuration

### User Account Setup
```bash
# Create application user (if not exists)
sudo useradd -m -s /bin/bash ai-microscope

# Set appropriate permissions
sudo chown -R ai-microscope:ai-microscope /opt/ai-microscope

# Create desktop shortcut
sudo cp docs/ai-microscope.desktop /usr/share/applications/
```

### Directory Structure Setup
```
/opt/ai-microscope/
├── app/                    # Application code
├── model/                  # AI model and database
├── docs/                   # Documentation
├── venv/                   # Python virtual environment
├── exports/                 # Exported reports
├── logs/                    # Application logs
├── backups/                 # Data backups
└── config/                  # Configuration files
```

### Permissions Configuration
```bash
# Set appropriate file permissions
sudo chmod 755 /opt/ai-microscope
sudo chmod 644 /opt/ai-microscope/model/*.keras
sudo chmod 644 /opt/ai-microscope/model/*.json
sudo chmod 755 /opt/ai-microscope/model/
sudo chmod 755 /opt/ai-microscope/exports/
sudo chmod 755 /opt/ai-microscope/logs/
```

---

## 🖥️ Desktop Integration

### Create Desktop Shortcut
```bash
# Create desktop entry file
sudo tee /usr/share/applications/ai-microscope.desktop > /dev/null <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AI Microscope
Comment=AI-powered bacterial identification system
Exec=/opt/ai-microscope/launch.sh
Icon=/opt/ai-microscope/docs/icon.png
Terminal=false
Categories=Science;Medical;
EOF
```

### Create Launch Script
```bash
# Create launch script
sudo tee /opt/ai-microscope/launch.sh > /dev/null <<'EOF'
#!/bin/bash
cd /opt/ai-microscope
source venv/bin/activate
python app/main_app.py
EOF

# Make executable
sudo chmod +x /opt/ai-microscope/launch.sh
```

---

## 🔒 Security Configuration

### File System Security
```bash
# Create application group
sudo groupadd ai-microscope-users

# Add users to group
sudo usermod -a -G ai-microscope-users username

# Set group ownership
sudo chgrp -R ai-microscope-users /opt/ai-microscope
sudo chmod -R g+rw /opt/ai-microscope/model
sudo chmod -R g+rw /opt/ai-microscope/exports
```

### Database Security
```bash
# Set database permissions
sudo chmod 600 /opt/ai-microscope/model/clinical_records.db
sudo chown ai-microscope:ai-microscope-users /opt/ai-microscope/model/clinical_records.db

# Create database backup directory
sudo mkdir -p /opt/ai-microscope/backups/database
sudo chown ai-microscope:ai-microscope-users /opt/ai-microscope/backups/database
```

### Log File Configuration
```bash
# Create log directory
sudo mkdir -p /opt/ai-microscope/logs
sudo chown ai-microscope:ai-microscope-users /opt/ai-microscope/logs
sudo chmod 775 /opt/ai-microscope/logs

# Configure log rotation
sudo tee /etc/logrotate.d/ai-microscope > /dev/null <<EOF
/opt/ai-microscope/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ai-microscope ai-microscope-users
}
EOF
```

---

## 🔄 Backup & Recovery Setup

### Automated Backup Script
```bash
# Create backup script
sudo tee /opt/ai-microscope/backup.sh > /dev/null <<'EOF'
#!/bin/bash

BACKUP_DIR="/opt/ai-microscope/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/opt/ai-microscope/model/clinical_records.db"
RECORDS_DIR="/opt/ai-microscope/model/records"

# Create backup directories
mkdir -p "$BACKUP_DIR/database"
mkdir -p "$BACKUP_DIR/records"

# Backup database
cp "$DB_FILE" "$BACKUP_DIR/database/clinical_records_$DATE.db"

# Backup records
if [ -d "$RECORDS_DIR" ]; then
    tar -czf "$BACKUP_DIR/records/records_$DATE.tar.gz" -C "$RECORDS_DIR" .
fi

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

# Make executable
sudo chmod +x /opt/ai-microscope/backup.sh
```

### Schedule Automated Backups
```bash
# Add to crontab for daily backup at 2 AM
sudo crontab -l | { cat; echo "0 2 * * * /opt/ai-microscope/backup.sh"; } | sudo crontab -

# Verify crontab entry
sudo crontab -l
```

---

## 🧪 Testing & Validation

### Pre-Deployment Testing
```bash
# Run comprehensive test suite
cd /opt/ai-microscope
source venv/bin/activate
python comprehensive_app_test.py

# Test model functionality
python simple_accuracy_test.py

# Test headless functionality
python headless_functionality_test.py
```

### Clinical Validation
1. **Known Samples**: Test with known bacterial species
2. **Quality Control**: Verify accuracy against manual identification
3. **Workflow Testing**: Complete clinical workflow testing
4. **Performance Testing**: Test with typical workload
5. **User Acceptance**: Staff training and feedback

### Validation Checklist
- [ ] **Model Accuracy**: >90% accuracy on test samples
- [ ] **Grad-CAM**: Heatmaps generated correctly
- [ ] **Performance**: <30 seconds per analysis
- [ ] **User Interface**: Intuitive and error-free
- [ ] **Data Storage**: Records saved correctly
- [ ] **Export Function**: Reports generated properly
- [ ] **Camera Integration**: All cameras working
- [ ] **Settings**: All configurations functional

---

## 📚 Training & Documentation

### Staff Training Materials
- [ ] **User Guide**: Distributed to all users
- [ ] **Quick Reference**: One-page summary created
- [ ] **Video Tutorials**: Step-by-step guides
- [ ] **Hands-on Training**: Practical session conducted
- [ ] **Assessment**: Competency verification

### Documentation Deployment
```bash
# Create documentation directory
sudo mkdir -p /opt/ai-microscope/docs/deployed

# Copy all documentation
sudo cp docs/*.md /opt/ai-microscope/docs/deployed/

# Set permissions
sudo chown -R ai-microscope:ai-microscope-users /opt/ai-microscope/docs
sudo chmod -R 644 /opt/ai-microscope/docs/deployed/
```

### Help System Integration
```bash
# Create help directory structure
mkdir -p /opt/ai-microscope/help/{user-guide,faq,privacy,policy}

# Copy documentation for in-app help
cp docs/USER_GUIDE.md /opt/ai-microscope/help/user-guide/
cp docs/FAQ.md /opt/ai-microscope/help/faq/
cp docs/PRIVACY_POLICY.md /opt/ai-microscope/help/privacy/
cp docs/DEPLOYMENT_GUIDE.md /opt/ai-microscope/help/policy/
```

---

## 🚀 Go-Live Procedure

### Pre-Launch Checklist
- [ ] **System Testing**: All tests passed
- [ ] **Staff Training**: Complete and documented
- [ ] **Backup System**: Configured and tested
- [ ] **Security Setup**: Permissions configured
- [ ] **Documentation**: Deployed and accessible
- [ ] **Performance**: System meets requirements
- [ ] **Regulatory**: Compliance verified

### Launch Steps
1. **Final Backup**: Complete system backup
2. **Service Start**: Start application for clinical use
3. **User Notification**: Inform staff of availability
4. **Monitoring**: Initial 24-hour monitoring
5. **Support**: Technical support on standby

### Post-Launch Monitoring
- **Performance Metrics**: Monitor system performance
- **Error Tracking**: Log and address errors
- **User Feedback**: Collect and address issues
- **Accuracy Monitoring**: Track diagnostic accuracy
- **System Health**: Regular health checks

---

## 🔧 Maintenance Procedures

### Regular Maintenance Schedule
- **Daily**: Automated backups, log rotation
- **Weekly**: Performance monitoring, disk space check
- **Monthly**: Security updates, accuracy validation
- **Quarterly**: System updates, staff training
- **Annually**: Full system review, hardware assessment

### Maintenance Tasks
```bash
# Weekly maintenance script
sudo tee /opt/ai-microscope/maintenance.sh > /dev/null <<'EOF'
#!/bin/bash

LOG_FILE="/opt/ai-microscope/logs/maintenance.log"
DATE=$(date)

echo "[$DATE] Starting weekly maintenance" >> $LOG_FILE

# Check disk space
DISK_USAGE=$(df /opt/ai-microscope | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] WARNING: Disk usage at $DISK_USAGE%" >> $LOG_FILE
fi

# Check database integrity
cd /opt/ai-microscope
source venv/bin/activate
python -c "
from model.db import get_db
try:
    db = get_db()
    db.get_recent(1)
    print('Database integrity: OK')
except Exception as e:
    print(f'Database error: {e}')
" >> $LOG_FILE

# Check model file integrity
if [ ! -f "/opt/ai-microscope/model/best_microscope_fusion.keras" ]; then
    echo "[$DATE] ERROR: Model file missing" >> $LOG_FILE
fi

echo "[$DATE] Weekly maintenance completed" >> $LOG_FILE
EOF

# Make executable and schedule
sudo chmod +x /opt/ai-microscope/maintenance.sh
sudo crontab -l | { cat; echo "0 3 * * 1 /opt/ai-microscope/maintenance.sh"; } | sudo crontab -
```

---

## 📞 Support & Troubleshooting

### Support Contact Information
- **Primary Support**: Hospital IT Department
- **Technical Support**: System Administrator
- **Clinical Support**: Microscopy Department Head
- **Emergency**: Hospital Administration

### Common Issues & Solutions
| Issue | Solution | Contact |
|--------|----------|---------|
| Camera not detected | Check connections, restart app | IT Support |
| Model loading failed | Verify model file, check permissions | Technical Support |
| Database errors | Check disk space, permissions | IT Support |
| Performance issues | Check system resources, restart | Technical Support |
| Accuracy concerns | Re-calibrate, training refresh | Clinical Support |

### Escalation Procedures
1. **First Level**: User documentation and self-help
2. **Second Level**: Department technical support
3. **Third Level**: Hospital IT department
4. **Fourth Level**: System administrator/developer

---

## 📊 Monitoring & Reporting

### Performance Metrics
- **System Uptime**: Application availability
- **Response Time**: Analysis processing time
- **Accuracy Rate**: Diagnostic accuracy percentage
- **Error Rate**: System error frequency
- **User Satisfaction**: Staff feedback and satisfaction

### Reporting Schedule
- **Daily**: Automated system health report
- **Weekly**: Performance summary and issues
- **Monthly**: Comprehensive usage and accuracy report
- **Quarterly**: System review and improvement plan

### Key Performance Indicators
- **Availability**: >99% uptime target
- **Accuracy**: >90% diagnostic accuracy
- **Response Time**: <30 seconds per analysis
- **User Satisfaction**: >85% satisfaction rate

---

## ✅ Deployment Completion

### Final Verification
- [ ] **All Tests Passed**: Comprehensive testing successful
- [ ] **Staff Trained**: All users trained and competent
- [ ] **Documentation Complete**: All docs deployed and accessible
- [ ] **Backup System**: Automated backups configured
- [ ] **Security Configured**: All security measures in place
- [ ] **Monitoring Active**: System monitoring operational
- [ ] **Support Ready**: Support procedures established

### Sign-off
**Deployment Engineer**: _________________________  
**Date**: _________________________  
**Hospital Administrator**: _________________________  
**IT Director**: _________________________

---

**Deployment Status**: ✅ READY FOR CLINICAL USE

---

*This deployment guide ensures successful implementation of AI Microscope in clinical environment with proper security, backup, and support procedures.*
