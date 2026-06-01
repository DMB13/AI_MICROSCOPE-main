#!/usr/bin/env python3
"""
AI Microscope Application - Main Entry Point
Launches the clinical bacterial identification application
"""

import os
import sys
from pathlib import Path

# Suppress TensorFlow warnings BEFORE any imports
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Suppress all warnings
import warnings
warnings.filterwarnings('ignore')

# Setup paths
BASE_DIR = Path(__file__).resolve()
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "app"))
sys.path.insert(0, str(BASE_DIR / "inference"))
sys.path.insert(0, str(BASE_DIR / "model"))

from utils.logger import log_info, log_error
from config.settings import get_settings_manager


def main():
    """Main application entry point."""
    try:
        log_info("=" * 70)
        log_info("AI Microscope Application Starting")
        log_info("=" * 70)
        
        # Load settings
        settings = get_settings_manager()
        log_info("Settings loaded successfully")
        
        # Import and launch GUI
        from app.app import MainApp
        import customtkinter as ctk
        
        # Configure CustomTkinter
        ctk.set_appearance_mode(settings.get("ui_settings", "theme", "System"))
        ctk.set_default_color_theme("blue")
        
        # Create and run application
        app = MainApp()
        app.mainloop()
        
        log_info("Application closed normally")
        
    except KeyboardInterrupt:
        log_info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        log_error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
