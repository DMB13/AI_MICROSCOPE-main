#!/usr/bin/env python3
"""
Localization Service for AI Microscope Application
Handles multi-language support (English and Swahili)
"""

from typing import Dict, Optional
from enum import Enum
from pathlib import Path
import json

from utils.logger import log_info, log_warning


class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    SWAHILI = "sw"


class Localization:
    """Manages translations for multiple languages."""
    
    def __init__(self, default_language: Language = Language.ENGLISH):
        """Initialize localization service.
        
        Args:
            default_language: Default language to use
        """
        self.current_language = default_language
        self.translations: Dict[Language, Dict[str, str]] = {
            Language.ENGLISH: self._get_english_translations(),
            Language.SWAHILI: self._get_swahili_translations()
        }
    
    def _get_english_translations(self) -> Dict[str, str]:
        """Get English translations."""
        return {
            # UI Labels
            "app_title": "DMB AI Microscope",
            "control_wing": "Control Wing",
            "primary_viewport": "Microscope View",
            "intelligence_wing": "AI Analysis",
            "capture_button": "Capture",
            "upload_button": "Upload",
            "diagnose_button": "Run Diagnosis",
            "export_button": "Export Reports",
            "settings_button": "Settings",
            "camera_label": "Camera",
            "start_camera": "Start Camera",
            "stop_camera": "Stop Camera",
            "patient_id_label": "Patient ID",
            "notes_label": "Notes",
            
            # Diagnosis Results
            "diagnosis_complete": "Diagnosis Complete",
            "confidence_label": "Confidence",
            "species_label": "Species",
            "inconclusive": "INCONCLUSIVE DUE TO LOW CONFIDENCE",
            "gradcam_title": "Grad-CAM Heatmap",
            
            # Messages
            "capturing": "Capturing image...",
            "uploading": "Uploading image...",
            "diagnosing": "Running diagnosis...",
            "exporting": "Exporting reports...",
            "camera_started": "Camera started",
            "camera_stopped": "Camera stopped",
            "image_saved": "Image saved",
            "diagnosis_saved": "Diagnosis saved to database",
            "export_complete": "Export completed",
            "export_failed": "Export failed",
            
            # Errors
            "error_camera_not_detected": "Camera not detected",
            "error_no_image": "No image loaded",
            "error_diagnosis_failed": "Diagnosis failed",
            "error_invalid_file": "Invalid file format",
            "error_database": "Database error",
            
            # Authentication
            "login_title": "Login",
            "username_label": "Username",
            "password_label": "Password",
            "login_button": "Login",
            "login_failed": "Login failed",
            "logout": "Logout",
            
            # Settings
            "settings_title": "Settings",
            "language_label": "Language",
            "theme_label": "Theme",
            "theme_dark": "Dark",
            "theme_light": "Light",
            "backup_label": "Backup",
            "save_button": "Save",
            "cancel_button": "Cancel",
            
            # Roles
            "role_admin": "Administrator",
            "role_supervisor": "Supervisor",
            "role_technician": "Technician",
        }
    
    def _get_swahili_translations(self) -> Dict[str, str]:
        """Get Swahili translations."""
        return {
            # UI Labels
            "app_title": "DMB AI Microscope",
            "control_wing": "Msimamizi wa Udhibiti",
            "primary_viewport": "Mtazamo wa Mikroskopu",
            "intelligence_wing": "Uchambuzi wa AI",
            "capture_button": "Piga Picha",
            "upload_button": "Pakia",
            "diagnose_button": "Enda Uchambuzi",
            "export_button": "Ripoti za Uzinduzi",
            "settings_button": "Mipangilio",
            "camera_label": "Kamera",
            "start_camera": "Anza Kamera",
            "stop_camera": "Acha Kamera",
            "patient_id_label": "Kitambulisho cha Mgonjwa",
            "notes_label": "Maoni",
            
            # Diagnosis Results
            "diagnosis_complete": "Uchambuzi Umekamilika",
            "confidence_label": "Uhakika",
            "species_label": "Aina",
            "inconclusive": "HAIJATHIBITISHWA KWA SABABU YA UHAKIKA MDOGO",
            "gradcam_title": "Joto la Grad-CAM",
            
            # Messages
            "capturing": "Inapiga picha...",
            "uploading": "Inapakia picha...",
            "diagnosing": "Inaendelea na uchambuzi...",
            "exporting": "Inatoa ripoti...",
            "camera_started": "Kamera imianzishwa",
            "camera_stopped": "Kamera imeacha kufanya kazi",
            "image_saved": "Picha imehifadhiwa",
            "diagnosis_saved": "Uchambuzi umehifadhiwa kwenye hifadhidata",
            "export_complete": "Uzinduzi umekamilika",
            "export_failed": "Uzinduzi umeshindwa",
            
            # Errors
            "error_camera_not_detected": "Kamera haijagunduliwa",
            "error_no_image": "Hakuna picha imeloadi",
            "error_diagnosis_failed": "Uchambuzi umeshindwa",
            "error_invalid_file": "Muonekano wa faili si sahihi",
            "error_database": "Hitilafu ya hifadhidata",
            
            # Authentication
            "login_title": "Kuingia",
            "username_label": "Jina la mtumiaji",
            "password_label": "Nenosiri",
            "login_button": "Kuingia",
            "login_failed": "Kuingia kumeshindwa",
            "logout": "Ondoka",
            
            # Settings
            "settings_title": "Mipangilio",
            "language_label": "Lugha",
            "theme_label": "Mandharinyuma",
            "theme_dark": "Njia",
            "theme_light": "Nuru",
            "backup_label": "Hifadhi nakala",
            "save_button": "Hifadhi",
            "cancel_button": "Ghairi",
            
            # Roles
            "role_admin": "Msimamizi",
            "role_supervisor": "Msimamizi Mkuu",
            "role_technician": "Mtaalamu wa teknolojia",
        }
    
    def set_language(self, language: Language) -> None:
        """Set current language.
        
        Args:
            language: Language to set
        """
        self.current_language = language
        log_info(f"Language set to {language.value}")
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get translation for a key.
        
        Args:
            key: Translation key
            default: Default value if key not found
            
        Returns:
            Translated string
        """
        translations = self.translations.get(self.current_language, {})
        return translations.get(key, default or key)
    
    def translate(self, key: str, **kwargs) -> str:
        """Get translation with placeholder replacement.
        
        Args:
            key: Translation key
            **kwargs: Placeholder values
            
        Returns:
            Translated string with placeholders replaced
        """
        text = self.get(key)
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    
    def get_available_languages(self) -> list:
        """Get list of available languages.
        
        Returns:
            List of Language enums
        """
        return list(Language)
    
    def get_language_name(self, language: Language) -> str:
        """Get human-readable language name.
        
        Args:
            language: Language enum
            
        Returns:
            Language name
        """
        names = {
            Language.ENGLISH: "English",
            Language.SWAHILI: "Kiswahili"
        }
        return names.get(language, language.value)


# Global localization instance
_localization_instance: Optional[Localization] = None


def get_localization() -> Localization:
    """Get global localization instance.
    
    Returns:
        Localization instance
    """
    global _localization_instance
    if _localization_instance is None:
        _localization_instance = Localization()
    return _localization_instance


def t(key: str, **kwargs) -> str:
    """Convenience function to get translation.
    
    Args:
        key: Translation key
        **kwargs: Placeholder values
        
    Returns:
        Translated string
    """
    return get_localization().translate(key, **kwargs)
