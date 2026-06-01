"""
PyInstaller hook for AI Microscope Application
Ensures all modules and data files are properly included in the build
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os
from pathlib import Path

# Get base directory
basedir = Path(__file__).resolve().parent.parent

# Collect all submodules from key packages
hiddenimports = []

# Core modules
hiddenimports += collect_submodules('core')
hiddenimports += collect_submodules('core.services')

# GUI modules  
hiddenimports += collect_submodules('gui')
hiddenimports += collect_submodules('gui.controllers')
hiddenimports += collect_submodules('gui.views')
hiddenimports += collect_submodules('gui.components')

# App modules
hiddenimports += ['app.services', 'app.settings_dialog', 'app.settings_manager']

# Model modules
hiddenimports += ['model.db', 'model.report', 'model.export_manager', 'model.model_config', 'model.types']

# Utils modules
hiddenimports += ['utils.logger', 'utils.error_handling', 'utils.markdown_converter']

# Vision and hardware
hiddenimports += ['vision.inference_wrapper', 'hardware.camera']

# Inference
hiddenimports += ['inference', 'inference.inference']

# Config
hiddenimports += ['config.constants', 'config.settings']

# Storage
hiddenimports += ['storage.export', 'storage.repository']

# Third-party packages that might be missed
hiddenimports += [
    'PIL._tkinter_finder',
    'cv2.cv2',
    'numpy.core._dtype_ctypes',
    'numpy.core._multiarray_tests',
    'tensorflow.python.keras.applications.efficientnet_v2',
]

# Collect data files
datas = []

# Add config files
if (basedir / 'config').exists():
    datas += collect_data_files('config')

# Add docs
if (basedir / 'docs').exists():
    datas.append((str(basedir / 'docs'), 'docs'))

# Add model files
model_files = [
    'best_clinical_rugged_1777619657.keras',
    'class_indices.json',
    'species_33_mapping.json',
    'clinical_records_schema.sql',
]
for f in model_files:
    src = basedir / 'model' / f
    if src.exists():
        datas.append((str(src), 'model'))

# Add storage files
storage_files = ['users.json', 'session_state.json', 'doc_viewer_config.json']
for f in storage_files:
    src = basedir / 'storage' / f
    if src.exists():
        datas.append((str(src), 'storage'))

# Add root level files
root_files = ['logo.ico', 'README.md', 'requirements.txt']
for f in root_files:
    src = basedir / f
    if src.exists():
        datas.append((str(src), '.'))
