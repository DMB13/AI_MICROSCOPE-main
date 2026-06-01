#!/usr/bin/env python3
"""
Constants for AI Microscope Application
Centralized configuration values
"""

from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "model"
DATA_DIR = BASE_DIR / "dataset_clinical"
EXPORT_DIR = BASE_DIR / "exports"
LOG_DIR = BASE_DIR / "logs"
DOCS_DIR = BASE_DIR / "docs"

# Model configuration
MODEL_FILE = "best_clinical_rugged_1777619657.keras"
MODEL_PATH = MODEL_DIR / MODEL_FILE
IMG_SIZE = (224, 224)
NUM_CLASSES = 34

# Clinical thresholds
CLINICAL_CONFIDENCE_THRESHOLD = 0.90
MIN_PATIENT_ID_LENGTH = 3

# Camera configuration
DEFAULT_CAMERA_INDEX = 0
DEFAULT_RESOLUTION = [1280, 720]
DEFAULT_FPS = 30
MAX_CAMERA_INDEX = 10

# UI configuration
DEFAULT_WINDOW_SIZE = [1366, 768]
DEFAULT_SIDEBAR_WIDTH = 220

# Database configuration
DB_FILE = BASE_DIR / "clinical_records.db"
MAX_RECENT_RECORDS = 100

# Export configuration
DEFAULT_EXPORT_FORMAT = "pdf"
BACKUP_FREQUENCY = "weekly"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE_PREFIX = "app_"
