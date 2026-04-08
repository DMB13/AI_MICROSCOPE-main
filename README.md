# AI_MICROSCOPE
Ai-aided microscope workstation

AI-Assisted Workstation for Rapid Bacterial Species Identification
## 📌 Project Overview

In resource-constrained clinical settings, identifying bacterial pathogens traditionally takes 48 to 72 hours through culture methods. This delay often leads to empirical prescribing of broad-spectrum antibiotics, fueling Antimicrobial Resistance (AMR).

This project introduces an Offline AI-Assisted Workstation designed for the Microbiology Laboratory at Mbeya Regional Referral Hospital (MRRH). Using a Deep Learning model (EfficientNet), the system identifies 33 bacterial species directly from digital Gram-stain microscopy images in seconds. It provides laboratory technicians with a "digital second opinion," reducing diagnostic turnaround time (TAT) and human error.
✨ Key Features
 * Offline Inference: No internet connection required, ensuring reliability in regional hospital settings.
 * High-Speed Identification: Species-level classification in under 5 seconds.
 * Explainable AI (Grad-CAM): Visual heatmaps highlight the specific bacterial clusters used by the AI to make its decision, building trust with clinicians.
 * Integrated Patient Registry: A built-in SQLite database logs patient IDs, timestamps, and diagnostic results for easy export and audit trails.
 * User-Friendly GUI: A modern dashboard built with CustomTkinter for easy operation by lab staff.
🔬 Scientific Background
The core of the workstation is a Convolutional Neural Network (CNN) based on the EfficientNet-B0 architecture.
 * Dataset: Trained on the Digital Bacterial System (DiBaS) dataset.
 * Classes: 33 species (including S. aureus, E. coli, Klebsiella pneumoniae, etc.).
 * Explainability: Uses Grad-CAM (Gradient-weighted Class Activation Mapping) to visualize morphological features recognized by the model.
🛠️ Tech Stack
 * Language: Python 3.11
 * Deep Learning: TensorFlow / Keras
 * Computer Vision: OpenCV
 * UI/UX: CustomTkinter (Modernized Tkinter)
 * Database: SQLite3
 * Imaging: Pillow (PIL)
## Project Structure
D:\AI_Microscope\
├── app\
│   ├── main_app.py                # Main GUI Workstation Entry point
│   └── microscope_settings.json   # Hardware calibration settings
├── inference\
│   ├── inference.py               # Pro-Grade Inference Engine & Grad-CAM logic
│   └── __init__.py                # Package initialization
├── model\
│   ├── best_bacteria_model.h5     # Trained Keras model weights
│   ├── class_indices.json         # Mapping of 33 species names
│   └── clinical_records.db        # Local SQLite database for history
└── README.md                      # Project documentation

## Installation & Setup
 * Clone the Repository:
   git clone https://github.com/DMB13/AI-Microscope-main.git
cd AI-Microscope-Workstation

 * Install Dependencies:
   Ensure you have Python 3.11 installed.
   pip install tensorflow opencv-python customtkinter pillow numpy

 * Hardware Connection:
   * Mount your digital microscope camera to the eyepiece.
   * Connect the camera via USB to your workstation.
🖥️ Usage
 * Launch the App:
   python app/main_app.py

 * Patient Registration: Enter the Patient ID/Case No. in the sidebar.
 * Live Stream: View the live microscope feed. Use the brightness/contrast sliders for image optimization.
 * Analyze: * Click Capture to freeze a clear frame.
   * Click Run AI Diagnosis.
   * The system will display the identified species, confidence percentage, and the Grad-CAM heatmap.
 * Export: View the "Recent Logs" pane or export the history as a clinical report.
📊 Performance Metrics
The system is evaluated based on:
 * Accuracy: Overall correct classification rate across 33 species.
 * Sensitivity/Specificity: Ability to identify specific pathogens like MRSA.
 * TAT Reduction: Comparison between AI-assisted reporting vs. traditional culture time.
⚖️ Ethical Disclaimer
This tool is intended as a Decision Support System (DSS) and is currently for research and evaluation purposes at MRRH and MUST. It should be used to assist, not replace, the final clinical judgment of a qualified Microbiologist.
🤝 Acknowledgments
 * Mbeya University of Science and Technology (MUST) - Department of Applied Sciences.
 * Mbeya Regional Referral Hospital (MRRH) - Microbiology Department.
 * Zielinski et al. - For the DiBaS dataset.
👤 Author
DEVIS MULOKOZI BYARUSHENGO.
Bachelor of Laboratory Science and Technology.
Mbeya University of Science and Technology (MUST)
