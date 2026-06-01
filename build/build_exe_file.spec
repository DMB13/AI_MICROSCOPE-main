# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for AI Microscope Application
Builds a single executable with all dependencies embedded
"""

import sys
from pathlib import Path
import os

block_cipher = None

# Get the base directory (use current working directory when run by PyInstaller)
basedir = Path(os.getcwd())

# Collect all data files
datas = [
    # Include model files - critical for the application
    (str(basedir / "model" / "best_clinical_rugged_1777619657.keras"), "model"),
    (str(basedir / "model" / "class_indices.json"), "model"),
    (str(basedir / "model" / "species_33_mapping.json"), "model"),
    (str(basedir / "model" / "clinical_records_schema.sql"), "model"),
    (str(basedir / "model" / "__init__.py"), "model"),
    (str(basedir / "model" / "db.py"), "model"),
    (str(basedir / "model" / "export_manager.py"), "model"),
    (str(basedir / "model" / "model_config.py"), "model"), 
    (str(basedir / "model" / "report.py"), "model"),
    (str(basedir / "model" / "types.py"), "model"),
    
    # Include config files
    (str(basedir / "config" / "constants.py"), "config"),
    (str(basedir / "config" / "settings.py"), "config"),
    
    # Include app folder
    (str(basedir / "app" / "__init__.py"), "app"),
    (str(basedir / "app" / "__main__.py"), "app"),
    (str(basedir / "app" / "services.py"), "app"),
    (str(basedir / "app" / "settings_dialog.py"), "app"),
    (str(basedir / "app" / "settings_manager.py"), "app"),
    (str(basedir / "app" / "microscope_settings.json"), "app"),
    
    # Include documentation
    (str(basedir / "docs"), "docs"),
    
    # Include storage module files
    (str(basedir / "storage" / "__init__.py"), "storage"),
    (str(basedir / "storage" / "export.py"), "storage"),
    (str(basedir / "storage" / "repository.py"), "storage"),
    (str(basedir / "storage" / "users.json"), "storage"),
    (str(basedir / "storage" / "session_state.json"), "storage"),
    (str(basedir / "storage" / "doc_viewer_config.json"), "storage"),
    
    # Include logo
    (str(basedir / "logo.ico"), "."),
    
    # Include README
    (str(basedir / "README.md"), "."),
    (str(basedir / "requirements.txt"), "."),
]

# Add database file if it exists
if (basedir / "clinical_records.db").exists():
    datas.append((str(basedir / "clinical_records.db"), "."))

a = Analysis(
    [str(basedir / "app" / "app.py")],
    pathex=[str(basedir), str(basedir / "app"), str(basedir / "core"), str(basedir / "gui")],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # TensorFlow and Keras
        'tensorflow',
        'keras',
        'tensorflow.python',
        'tensorflow_core',
        'tensorflow.python.framework',
        'tensorflow.python.keras.engine.functional',
        'tensorflow.python.keras.engine.training',
        'tensorflow.python.keras.engine.sequential',
        'tensorflow.python.keras.layers',
        'tensorflow.python.keras.models',
        'tensorflow.python.keras.utils',
        'tensorflow.python.keras.applications',
        'tensorflow.python.keras.applications.efficientnet_v2',
        
        # CustomTkinter
        'customtkinter',
        
        # PIL/Pillow
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL.ImageFilter',
        
        # OpenCV
        'cv2',
        'cv2.cv2',
        
        # NumPy
        'numpy',
        'numpy.core._dtype_ctypes',
        'numpy.core._multiarray_tests',
        
        # ReportLab for PDF generation
        'reportlab',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.platypus',
        'reportlab.lib.styles',
        'reportlab.lib.colors',
        'reportlab.lib.units',
        'reportlab.graphics.shapes',
        'reportlab.graphics',
        'reportlab.pdfgen.canvas',
        
        # SQLite
        'sqlite3',
        
        # Standard library modules that might be missed
        'json',
        'csv',
        'datetime',
        'pathlib',
        'typing',
        'collections',
        'enum',
        'hashlib',
        'base64',
        'io',
        'threading',
        'queue',
        'subprocess',
        'warnings',
        'logging',
        'copy',
        'functools',
        'inspect',
        'types',
        're',
        'math',
        'random',
        'string',
        'time',
        'uuid',
        'zlib',
        'pickle',
        
        # Core modules
        'core.auth',
        'core.audit_trail',
        'core.analytics',
        'core.anonymizer',
        'core.auto_update',
        'core.backup_service',
        'core.confidence_calibration',
        'core.device_manager',
        'core.domain.models',
        'core.encryption',
        'core.feedback_system',
        'core.health_check',
        'core.heatmap_overlay',
        'core.localization',
        'core.pdf_report',
        'core.services.diagnosis_service',
        'core.services.patient_service',
        'core.session_manager',
        'core.tfda_compliance',
        'core.tflite_inference',
        'core.uncertainty_estimation',
        
        # GUI modules
        'gui.controllers.camera_controller',
        'gui.controllers.diagnosis_controller',
        'gui.controllers.export_controller',
        'gui.views.control_wing',
        'gui.views.primary_viewport',
        'gui.views.intelligence_wing',
        'gui.components.camera_controls',
        'gui.components.documentation_viewer',
        'gui.components.export_dialog',
        'gui.components.first_run_wizard',
        'gui.components.image_adjustments',
        'gui.components.image_display',
        'gui.components.loading_spinner',
        'gui.components.login_dialog',
        'gui.components.patient_input',
        'gui.components.results_display',
        'gui.components.user_profile_dialog',
        'gui.components.clinical_status_bar',
        'gui.components.patient_safety_dialog',
        'gui.components.medical_help_system',
        
        # App modules
        'app.services',
        'app.settings_dialog',
        'app.settings_manager',
        
        # Hardware modules
        'hardware.camera',
        
        # Vision modules
        'vision.inference_wrapper',
        
        # Inference modules
        'inference',
        'inference.inference',
        
        # Utils modules
        'utils.logger',
        'utils.error_handling',
        'utils.markdown_converter',
        
        # Config modules
        'config.constants',
        'config.settings',
        
        # Model modules
        'model.db',
        'model.report',
        'model.export_manager',
        'model.model_config',
        'model.types',
        
        # Storage modules
        'storage.export',
        'storage.repository',
    ],
    hookspath=[str(basedir / "build")],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'matplotlib.tests',
        'matplotlib.test',
        'scipy.tests',
        'scipy.test',
        'numpy.tests',
        'numpy.test',
        'pandas.tests',
        'pandas.test',
        'pytest',
        '_pytest',
        'doctest',
        'pydoc',
        'tkinter.test',
        'tkinter.tests',
        # Exclude build tools
        'pyinstaller',
        'PyInstaller',
        'pip',
        'setuptools',
        'wheel',
        # Exclude dev tools
        'black',
        'flake8',
        'mypy',
        'pylint',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DMB_AI_Microscope',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(basedir / "logo.ico") if (basedir / "logo.ico").exists() else None,
    # Request admin privileges on launch
    uac_admin=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DMB_AI_Microscope',
)
