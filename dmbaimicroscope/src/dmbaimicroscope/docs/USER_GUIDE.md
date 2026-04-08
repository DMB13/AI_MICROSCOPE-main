# AI Microscope - User Guide

## 🏥 Welcome to AI Microscope

AI Microscope is an advanced diagnostic tool that uses artificial intelligence to identify bacterial species from microscope images. This guide will help you get started and use the system effectively.

---

## 🚀 Quick Start

### 1. Launching the Application
```bash
# Navigate to project directory
cd /home/dmb/Desktop/AI_MICROSCOPE-main

# Activate virtual environment
source venv/bin/activate

# Launch the application
python app/main_app.py
```

### 2. First-Time Setup
1. **Camera Setup**: The application will automatically detect available cameras
2. **Settings Configuration**: Adjust brightness, contrast, and AI confidence thresholds
3. **Patient ID**: Enter patient identification for clinical records

---

## 📸 Image Capture & Upload

### Camera Capture
1. **Select Camera**: Choose from detected cameras in the dropdown
2. **Adjust Settings**: Use brightness and contrast sliders for optimal image quality
3. **Capture Image**: Click "Capture Image" to take a photo
4. **Review**: Check image quality before proceeding

### File Upload
1. **Click Upload**: Select "Upload Image" button
2. **Choose File**: Supported formats: PNG, JPG, JPEG, BMP
3. **Image Validation**: System will validate image format and size
4. **Proceed**: Continue to AI diagnosis

---

## 🤖 AI Diagnosis Process

### Running Diagnosis
1. **Patient ID**: Enter patient identification (required)
2. **Start Diagnosis**: Click "Run AI Diagnosis"
3. **Processing**: System analyzes image (typically 10-30 seconds)
4. **Results**: View species identification and confidence score

### Understanding Results
- **Species Name**: Identified bacterial species
- **Confidence Score**: Probability accuracy (0-100%)
- **Grad-CAM Heatmap**: Visual explanation of AI decision
- **Color Coding**: 
  - 🟢 Green: High confidence (>90%)
  - 🟡 Yellow: Medium confidence (70-90%)
  - 🔴 Red: Low confidence (<70%)

---

## 🌡️ Understanding Grad-CAM

Grad-CAM (Gradient-weighted Class Activation Mapping) shows which parts of the image influenced the AI's decision.

### Interpreting Heatmaps
- **Red/Orange Areas**: High importance for identification
- **Blue/Green Areas**: Low importance
- **Clinical Use**: Helps verify AI focused on relevant bacterial structures

### Heatmap Quality
- **Clear Focus**: Good - AI identified relevant features
- **Diffuse Pattern**: May need better image quality
- **No Heatmap**: Technical issue - retry diagnosis

---

## ⚙️ Settings & Adjustments

### Image Adjustments
- **Brightness**: (-100 to +100) Adjust image illumination
- **Contrast**: (-100 to +100) Enhance image clarity
- **Auto-enhance**: Automatically optimize image quality

### AI Settings
- **Confidence Threshold**: Minimum confidence for clinical use
- **Show Confidence**: Display confidence percentages
- **Auto-save Results**: Automatically save diagnosis results
- **Grad-CAM Enabled**: Toggle heatmap generation

### Camera Settings
- **Camera Index**: Select camera device
- **Resolution**: Image capture quality (640x480 to 2560x1440)
- **FPS**: Frames per second for live preview
- **Auto-detect**: Automatically find cameras on startup

---

## 💾 Data Management

### Clinical Records
- **Automatic Saving**: Results saved with timestamp
- **Patient ID**: Links results to patient records
- **Image Storage**: Original and processed images saved
- **Search**: Find records by patient ID or date

### Export Options
- **CSV Export**: For data analysis and spreadsheet use
- **PDF Reports**: Complete clinical documentation with images
- **Include Images**: Add original and Grad-CAM images to exports
- **Auto-export**: Schedule regular data exports

---

## 🔧 Troubleshooting

### Common Issues

#### Camera Not Working
**Problem**: "No camera detected" message
**Solution**:
1. Check camera connection
2. Verify camera drivers
3. Try different camera index
4. Restart application

#### Low Confidence Results
**Problem**: Confidence scores below 70%
**Solution**:
1. Improve image focus
2. Adjust brightness/contrast
3. Ensure proper staining
4. Use higher magnification

#### Grad-CAM Not Showing
**Problem**: No heatmap generated
**Solution**:
1. Check image quality
2. Verify model loading
3. Restart application
4. Check available memory

#### Slow Processing
**Problem**: Diagnosis taking >60 seconds
**Solution**:
1. Close other applications
2. Check system resources
3. Use smaller image resolution
4. Restart application

### Error Messages

#### "AI Error: Model loading failed"
- **Cause**: Model file missing or corrupted
- **Solution**: Verify `model/best_microscope_fusion.keras` exists

#### "Database Error: Cannot save record"
- **Cause**: Disk space or permissions issue
- **Solution**: Check disk space and file permissions

#### "Image format not supported"
- **Cause**: Invalid image file
- **Solution**: Use PNG, JPG, JPEG, or BMP format

---

## 🏥 Clinical Best Practices

### Image Quality
- **Focus**: Ensure sharp, clear images
- **Lighting**: Proper illumination without glare
- **Staining**: Follow standard bacterial staining protocols
- **Magnification**: Use appropriate magnification level

### Diagnosis Workflow
1. **Patient Identification**: Always enter correct patient ID
2. **Image Quality Check**: Verify image before diagnosis
3. **Multiple Images**: Capture several views if uncertain
4. **Confidence Review**: Consider confidence scores in diagnosis
5. **Documentation**: Export results for patient records

### Quality Assurance
- **Regular Calibration**: Check camera and settings regularly
- **Control Samples**: Use known samples for verification
- **Record Keeping**: Maintain detailed usage logs
- **Training**: Ensure staff are properly trained

---

## 📞 Support & Help

### Getting Help
- **Application Help**: Use Help menu in the application
- **Settings Access**: All documentation available through Settings → Help
- **Technical Support**: Contact system administrator
- **User Manual**: Complete manual available in documentation folder

### Reporting Issues
When reporting problems, include:
1. **Error Message**: Exact text of any error
2. **Steps Taken**: What you were doing when issue occurred
3. **System Info**: Operating system and version
4. **Image Sample**: Example image causing issue (if possible)

---

## 📚 Additional Resources

### Training Materials
- **Video Tutorials**: Step-by-step operation guides
- **Quick Reference**: One-page summary of common tasks
- **Clinical Protocols**: Recommended usage procedures

### Technical Documentation
- **API Documentation**: For integration with other systems
- **Database Schema**: For custom reporting
- **Model Information**: AI model details and capabilities

---

## 🔄 Updates & Maintenance

### System Updates
- **Automatic Check**: Application checks for updates
- **Manual Update**: Check through Settings → About
- **Backup**: Always backup data before updating

### Regular Maintenance
- **Database Cleanup**: Remove old records periodically
- **Model Updates**: Update AI models as available
- **Settings Backup**: Export settings for backup

---

*Last Updated: March 9, 2026*  
*Version: 1.0.0*  
*For clinical use at Mbeya Regional Referral Hospital*
