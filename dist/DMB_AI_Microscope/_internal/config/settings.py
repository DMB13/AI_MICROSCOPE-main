#!/usr/bin/env python3
"""
Settings Configuration for AI Microscope Application
Manages application settings with validation and persistence
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import log_info, log_error, log_warning, log_debug

from config.constants import (
    BASE_DIR,
    DOCS_DIR,
    EXPORT_DIR,
    DEFAULT_CAMERA_INDEX,
    DEFAULT_RESOLUTION,
    DEFAULT_FPS,
    CLINICAL_CONFIDENCE_THRESHOLD,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_SIDEBAR_WIDTH,
    DEFAULT_EXPORT_FORMAT,
    BACKUP_FREQUENCY,
    MAX_RECENT_RECORDS
)


class SettingsManager:
    """Manages application settings with validation and persistence."""
    
    DEFAULT_SETTINGS = {
        "camera": {
            "index": DEFAULT_CAMERA_INDEX,
            "resolution": DEFAULT_RESOLUTION,
            "fps": DEFAULT_FPS,
            "auto_detect": True
        },
        "image_adjustments": {
            "brightness": 0,
            "contrast": 0,
            "saturation": 0,
            "sharpness": 0,
            "gamma": 1.0,
            "auto_enhance": False
        },
        "focus_presets": {
            "low": 10,
            "mid": 50,
            "high": 90,
            "custom": 50
        },
        "ai_settings": {
            "confidence_threshold": CLINICAL_CONFIDENCE_THRESHOLD,
            "show_confidence": True,
            "auto_save_results": True,
            "grad_cam_enabled": True,
            "prediction_timeout": 30
        },
        "export_settings": {
            "directory": "../exports",
            "default_format": DEFAULT_EXPORT_FORMAT,
            "include_images": True,
            "include_gradcam": True,
            "auto_export": False,
            "export_interval": "daily"
        },
        "ui_settings": {
            "theme": "System",
            "language": "English",
            "show_tooltips": True,
            "auto_backup": True,
            "window_size": DEFAULT_WINDOW_SIZE,
            "sidebar_width": DEFAULT_SIDEBAR_WIDTH
        },
        "clinical_settings": {
            "patient_id_required": True,
            "auto_timestamp": True,
            "validate_patient_id": True,
            "default_confidence_threshold": CLINICAL_CONFIDENCE_THRESHOLD,
            "enable_audit_log": True
        },
        "advanced_settings": {
            "model_cache_enabled": True,
            "debug_mode": False,
            "log_level": "INFO",
            "max_recent_records": MAX_RECENT_RECORDS,
            "backup_frequency": BACKUP_FREQUENCY
        }
    }
    
    def __init__(self, settings_file: Optional[str] = None):
        """Initialize settings manager."""
        if settings_file is None:
            # Use app directory for settings file
            settings_file = BASE_DIR / 'app' / 'microscope_settings.json'
        
        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file with validation."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                merged_settings = self._merge_with_defaults(loaded_settings)
                validated_settings = self._validate_settings(merged_settings)
                
                log_info(f"Settings loaded from {self.settings_file}")
                return validated_settings
            else:
                log_info("Settings file not found, using defaults")
                return self.DEFAULT_SETTINGS.copy()
                
        except KeyError as e:
            # Handle missing keys gracefully
            log_error(f"Missing key in settings: {e}", exc_info=True)
            log_info("Using default settings")
            return self.DEFAULT_SETTINGS.copy()
        except json.JSONDecodeError as e:
            # Handle corrupted JSON
            log_error(f"Invalid JSON in settings file: {e}", exc_info=True)
            log_info("Using default settings")
            return self.DEFAULT_SETTINGS.copy()
        except Exception as e:
            log_error(f"Error loading settings: {e}", exc_info=True)
            log_info("Using default settings")
            return self.DEFAULT_SETTINGS.copy()
    
    def _merge_with_defaults(self, loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded settings with defaults."""
        merged = self.DEFAULT_SETTINGS.copy()
        
        # Handle legacy flat keys (e.g., "camera_index" -> "camera": {"index": ...})
        # Migrate old flat keys to new nested structure
        if "camera_index" in loaded:
            if "camera" not in merged:
                merged["camera"] = {}
            merged["camera"]["index"] = loaded["camera_index"]
        
        for section, values in loaded.items():
            # Skip legacy flat keys that have been migrated
            if section in ["camera_index", "camera_resolution", "camera_fps"]:
                continue
                
            if section in merged:
                if isinstance(values, dict) and isinstance(merged[section], dict):
                    merged[section].update(values)
                else:
                    merged[section] = values
            else:
                merged[section] = values
        
        return merged
    
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate settings values."""
        validated = settings.copy()
        
        # Camera settings validation
        if "camera" in validated:
            camera = validated["camera"]
            camera["index"] = max(0, int(camera.get("index", 0)))
            camera["fps"] = max(1, min(60, int(camera.get("fps", 30))))
            
            res = camera.get("resolution", DEFAULT_RESOLUTION)
            if isinstance(res, list) and len(res) == 2:
                camera["resolution"] = [max(320, res[0]), max(240, res[1])]
        
        # Image adjustments validation
        if "image_adjustments" in validated:
            img_adj = validated["image_adjustments"]
            for key in ["brightness", "contrast", "saturation", "sharpness"]:
                img_adj[key] = max(-100, min(100, int(img_adj.get(key, 0))))
            img_adj["gamma"] = max(0.1, min(3.0, float(img_adj.get("gamma", 1.0))))
        
        # AI settings validation
        if "ai_settings" in validated:
            ai = validated["ai_settings"]
            ai["confidence_threshold"] = max(0.0, min(1.0, float(ai.get("confidence_threshold", 0.5))))
            ai["prediction_timeout"] = max(5, min(300, int(ai.get("prediction_timeout", 30))))
        
        # Export settings validation
        if "export_settings" in validated:
            export = validated["export_settings"]
            if export.get("default_format") not in ["pdf", "csv", "json"]:
                export["default_format"] = DEFAULT_EXPORT_FORMAT
        
        return validated
    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """Get setting value."""
        if key is None:
            return self.settings.get(section, default)
        
        section_data = self.settings.get(section, {})
        return section_data.get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set setting value."""
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section][key] = value
    
    def update_section(self, section: str, values: Dict[str, Any]) -> None:
        """Update entire section with new values."""
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section].update(values)
    
    def save(self) -> bool:
        """Save settings to file with error handling and backup."""
        try:
            # Ensure settings structure is correct before saving
            # Migrate any legacy flat keys to nested structure
            if "camera_index" in self.settings:
                if "camera" not in self.settings:
                    self.settings["camera"] = {}
                self.settings["camera"]["index"] = self.settings.pop("camera_index")
            
            validated_settings = self._validate_settings(self.settings)
            
            # Create backup of existing file
            if self.settings_file.exists():
                backup_file = self.settings_file.with_suffix('.json.bak')
                try:
                    if backup_file.exists():
                        backup_file.unlink()
                    self.settings_file.rename(backup_file)
                    log_debug(f"Settings backup created: {backup_file}")
                except Exception as e:
                    log_warning(f"Could not create settings backup: {e}")
            
            # Save new settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(validated_settings, f, indent=2, ensure_ascii=False)
            
            # Update in-memory settings with validated settings
            self.settings = validated_settings
            
            log_info(f"Settings saved successfully to {self.settings_file}")
            return True
            
        except PermissionError as e:
            log_error(f"Permission denied when saving settings: {e}", exc_info=True)
            return False
        except json.JSONEncodeError as e:
            log_error(f"JSON encoding error when saving settings: {e}", exc_info=True)
            return False
        except Exception as e:
            log_error(f"Unexpected error saving settings: {e}", exc_info=True)
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = self.DEFAULT_SETTINGS.copy()
    
    def get_documentation_paths(self) -> Dict[str, Path]:
        """Get paths to documentation files.
        
        Returns:
            Dictionary with documentation file paths
        """
        return {
            "user_guide": DOCS_DIR / "USER_GUIDE.md",
            "faq": DOCS_DIR / "FAQ.md",
            "privacy_policy": DOCS_DIR / "PRIVACY_POLICY.md",
            "test_report": DOCS_DIR / "TEST_REPORT.md",
            "deployment_guide": DOCS_DIR / "DEPLOYMENT_GUIDE.md",
            "readme": BASE_DIR / "README.md"
        }
    
    def get_export_directory(self) -> Path:
        """Get the export directory path from settings.
        
        Returns:
            Path to export directory
        """
        export_dir_str = self.get("export_settings", "directory", "../exports")
        export_dir = Path(export_dir_str)
        
        # Convert relative path to absolute
        if not export_dir.is_absolute():
            export_dir = BASE_DIR / export_dir
        
        # Create directory if it doesn't exist
        export_dir.mkdir(parents=True, exist_ok=True)
        
        return export_dir


# Global settings instance
_settings_manager = None

def get_settings_manager() -> SettingsManager:
    """Get global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

def save_settings() -> bool:
    """Save global settings."""
    global _settings_manager
    if _settings_manager is not None:
        return _settings_manager.save()
    return False
