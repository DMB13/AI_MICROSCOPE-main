# AI_MICROSCOPE
AI-aided microscope workstation

AI-Assisted Workstation for Rapid Bacterial Species Identification

## 📌 Project Overview

In resource-constrained clinical settings, identifying bacterial pathogens traditionally takes 48 to 72 hours through culture methods. This delay often leads to empirical prescribing of broad-spectrum antibiotics, fueling Antimicrobial Resistance (AMR).

This project introduces an Offline AI-Assisted Workstation designed for the Microbiology Laboratory at Mbeya Regional Referral Hospital (MRRH). Using a Deep Learning model (EfficientNetV2M), the system identifies 34 bacterial species directly from digital Gram-stain microscopy images in seconds. It provides laboratory technicians with a "digital second opinion," reducing diagnostic turnaround time (TAT) and human error.

## ✨ Key Features

- **Offline Inference**: No internet connection required, ensuring reliability in regional hospital settings.
- **High-Speed Identification**: Species-level classification in under 5 seconds.
- **Explainable AI (Grad-CAM)**: Visual heatmaps highlight the specific bacterial clusters used by the AI to make its decision, building trust with clinicians.
- **Integrated Patient Registry**: A built-in SQLite database logs patient IDs, timestamps, and diagnostic results for easy export and audit trails.
- **User-Friendly GUI**: A modern dashboard built with CustomTkinter with a layered architecture for maintainability.
- **Real-time Image Adjustments**: Brightness and contrast adjustments applied in real-time to uploaded images and live camera streams.
- **Clinical Confidence Threshold**: 90% confidence guardrail displays "INCONCLUSIVE" for low-confidence predictions.

## 🔬 Scientific Background

The core of the workstation is a Convolutional Neural Network (CNN) based on the EfficientNetV2M architecture.

- **Dataset**: Trained on the Digital Bacterial System (DiBaS) dataset with clinical validation.
- **Classes**: 34 species (including S. aureus, E. coli, Klebsiella pneumoniae, Candida albicans, etc.).
- **Explainability**: Uses Grad-CAM (Gradient-weighted Class Activation Mapping) to visualize morphological features recognized by the model.
- **Input**: 224x224 RGB images with advanced preprocessing.

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Deep Learning**: TensorFlow 2.18.1 with Keras 3.x
- **Computer Vision**: OpenCV
- **UI/UX**: CustomTkinter (Modernized Tkinter)
- **Database**: SQLite3
- **Imaging**: Pillow (PIL)
- **Architecture**: Layered MVC pattern with controllers and views

## Project Structure

```
g:\AI_MICROSCOPE-main\
├── app\
│   ├── app_refactored.py          # Main GUI Workstation Entry point (refactored)
│   ├── services.py                # Service layer for inference and records
│   └── settings_dialog.py         # Settings configuration dialog
├── config\
│   ├── constants.py               # Application constants and paths
│   └── settings.py                # Settings manager with persistence
├── core\
│   ├── database.py                # Database operations
│   └── models.py                  # Data models
├── docs\
│   ├── USER_GUIDE.md              # User documentation
│   ├── FAQ.md                     # Frequently asked questions
│   └── DEPLOYMENT_GUIDE.md        # Deployment instructions
├── gui\
│   ├── components\                # Reusable GUI components
│   │   ├── image_display.py       # Image display component
│   │   ├── patient_input.py       # Patient ID input component
│   │   ├── camera_controls.py     # Camera control component
│   │   └── image_adjustments.py   # Image adjustment sliders
│   ├── views\                     # View layer (UI panels)
│   │   ├── control_wing.py        # Left control panel
│   │   ├── primary_viewport.py    # Center viewport (camera/image)
│   │   └── intelligence_wing.py   # Right intelligence panel
│   └── controllers\               # Controller layer
│       ├── camera_controller.py   # Camera operations
│       ├── diagnosis_controller.py # Diagnosis operations
│       └── export_controller.py   # Export operations
├── hardware\
│   └── camera.py                  # Camera hardware interface
├── inference\
│   ├── inference.py               # Pro-Grade Inference Engine & Grad-CAM logic
│   └── inference_wrapper.py       # Wrapper for inference operations
├── model\
│   ├── clinical_rugged_efficientnetv2m.keras  # Trained Keras model weights
│   ├── species_mapping.json       # Mapping of 34 species names
│   └── clinical_records.db        # Local SQLite database for history
├── storage\
│   ├── images\                    # Captured images storage
│   └── exports\                   # Exported reports storage
├── utils\
│   └── logger.py                  # Logging utilities
├── vision\
│   └── inference_wrapper.py       # Vision processing wrapper
├── main.py                        # Alternative entry point
├── microscope_settings.json       # Hardware calibration settings
└── requirements.txt               # Python dependencies
```

## Installation & Setup

### Clone the Repository
```bash
git clone https://github.com/DMB13/AI-Microscope.git
cd AI-Microscope-Workstation
```

### Install Dependencies
Ensure you have Python 3.11+ installed.

```bash
pip install -r requirements.txt
```

Or manually install core dependencies:
```bash
pip install tensorflow==2.18.1 opencv-python customtkinter pillow numpy
```

### Hardware Connection
- Mount your digital microscope camera to the eyepiece.
- Connect the camera via USB to your workstation.

## 🖥️ Usage

### Launch the App
```bash
python app/app_refactored.py
```

Or use the alternative entry point:
```bash
python main.py
```

### Workflow
1. **Patient Registration**: Enter the Patient ID/Case No. in the Control Wing (left panel).
2. **Image Capture**:
   - **Camera Mode**: Start the camera to view live microscope feed. Use the brightness/contrast sliders in the Image Adjustments section for real-time optimization.
   - **Upload Mode**: Click "Upload Media" to load an existing image file.
3. **Capture**: Click "Capture" to freeze a clear frame from the live stream or use the uploaded image.
4. **Analyze**: Click "Run AI Diagnosis" in the Intelligence Wing (right panel).
   - The system will display the identified species, confidence percentage, and the Grad-CAM heatmap.
   - If confidence is below 90%, the system displays "INCONCLUSIVE DUE TO LOW CONFIDENCE".
5. **Export**: View clinical records in the Intelligence Wing or export the history as a clinical report.

### Settings
Click the "Settings" button in the Control Wing to configure:
- Camera settings (index, resolution, FPS)
- Image adjustments (brightness, contrast, saturation, sharpness, gamma)
- AI settings (confidence threshold, Grad-CAM enabled)
- Export options (format, directory)
- Clinical preferences (patient ID requirements, audit logging)

### Documentation
Access comprehensive documentation through the Settings dialog:
- **User Guide**: Detailed instructions for using the workstation
- **FAQ**: Common questions and troubleshooting
- **Deployment Guide**: Instructions for deployment in clinical settings

## 📊 Performance Metrics

The system is evaluated based on:
- **Accuracy**: Overall correct classification rate across 34 species.
- **Sensitivity/Specificity**: Ability to identify specific pathogens like MRSA.
- **TAT Reduction**: Comparison between AI-assisted reporting vs. traditional culture time.
- **Model Size**: 105.7M parameters with efficient inference (~5 seconds per image).

## ⚖️ Ethical Disclaimer

This tool is intended as a Decision Support System (DSS) and is currently for research and evaluation purposes at MRRH and MUST. It should be used to assist, not replace, the final clinical judgment of a qualified Microbiologist.

## 🤝 Acknowledgments

- **Mbeya University of Science and Technology (MUST)** - Department of Applied Sciences.
- **Mbeya Regional Referral Hospital (MRRH)** - Microbiology Department.
- **Zielinski et al.** - For the DiBaS dataset.

## 👤 Author

**DEVIS MULOKOZI BYARUSHENGO**
Bachelor of Laboratory Science and Technology
Mbeya University of Science and Technology (MUST)

---

**Version**: 2.0 (Refactored Architecture)
**Last Updated**: May 2026
**Status**: Clinical Evaluation Phase
