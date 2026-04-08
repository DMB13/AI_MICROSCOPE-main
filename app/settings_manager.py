"""Settings Manager for AI Microscope Application.

Handles loading, saving, and managing application settings with
validation and default values for clinical use.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class SettingsManager:
    """Manages application settings with validation and persistence."""
    
    DEFAULT_SETTINGS = {
        "camera": {
            "index": 0,
            "resolution": [1280, 720],
            "fps": 30,
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
            "confidence_threshold": 0.5,
            "show_confidence": True,
            "auto_save_results": True,
            "grad_cam_enabled": True,
            "prediction_timeout": 30
        },
        "export_settings": {
            "directory": "../exports",
            "default_format": "pdf",
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
            "window_size": [1366, 768],
            "sidebar_width": 220
        },
        "clinical_settings": {
            "patient_id_required": True,
            "auto_timestamp": True,
            "validate_patient_id": True,
            "default_confidence_threshold": 0.7,
            "enable_audit_log": True
        },
        "advanced_settings": {
            "model_cache_enabled": True,
            "debug_mode": False,
            "log_level": "INFO",
            "max_recent_records": 100,
            "backup_frequency": "weekly"
        }
    }
    
    def __init__(self, settings_file: Optional[str] = None):
        """Initialize settings manager.
        
        Args:
            settings_file: Path to settings file. If None, uses default location.
        """
        if settings_file is None:
            settings_file = Path(__file__).resolve().parent / 'microscope_settings.json'
        
        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file with validation."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults and validate
                merged_settings = self._merge_with_defaults(loaded_settings)
                validated_settings = self._validate_settings(merged_settings)
                
                logger.info(f"Settings loaded from {self.settings_file}")
                return validated_settings
            else:
                logger.info("Settings file not found, using defaults")
                return self.DEFAULT_SETTINGS.copy()
                
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            logger.info("Using default settings")
            return self.DEFAULT_SETTINGS.copy()
    
    def _merge_with_defaults(self, loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded settings with defaults."""
        merged = self.DEFAULT_SETTINGS.copy()
        
        for section, values in loaded.items():
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
            
            res = camera.get("resolution", [1280, 720])
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
                export["default_format"] = "pdf"
        
        return validated
    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """Get setting value.
        
        Args:
            section: Settings section name
            key: Specific key within section (optional)
            default: Default value if not found
        """
        if key is None:
            return self.settings.get(section, default)
        
        section_data = self.settings.get(section, {})
        return section_data.get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set setting value.
        
        Args:
            section: Settings section name
            key: Specific key within section
            value: New value
        """
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section][key] = value
    
    def update_section(self, section: str, values: Dict[str, Any]) -> None:
        """Update entire section with new values.
        
        Args:
            section: Settings section name
            values: Dictionary of new values
        """
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section].update(values)
    
    def save(self) -> bool:
        """Save settings to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate before saving
            validated_settings = self._validate_settings(self.settings)
            
            # Create backup of existing file
            if self.settings_file.exists():
                backup_file = self.settings_file.with_suffix('.json.bak')
                try:
                    if backup_file.exists():
                        backup_file.unlink()
                    self.settings_file.rename(backup_file)
                except Exception:
                    pass  # Ignore backup errors
            
            # Save new settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(validated_settings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings saved to {self.settings_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = self.DEFAULT_SETTINGS.copy()
    
    def get_export_directory(self) -> Path:
        """Get validated export directory path."""
        export_dir = Path(self.get("export_settings", "directory", "../exports"))
        
        # Convert relative path to absolute
        if not export_dir.is_absolute():
            export_dir = Path(__file__).resolve().parents[1] / export_dir
        
        # Create directory if it doesn't exist
        export_dir.mkdir(parents=True, exist_ok=True)
        
        return export_dir
    
    def get_camera_settings(self) -> Dict[str, Any]:
        """Get camera settings with validation."""
        return self.get("camera")
    
    def get_image_adjustments(self) -> Dict[str, Any]:
        """Get image adjustment settings."""
        return self.get("image_adjustments")
    
    def get_ai_settings(self) -> Dict[str, Any]:
        """Get AI settings."""
        return self.get("ai_settings")
    
    def get_help_directory(self) -> Path:
        """Get help documentation directory path."""
        help_dir = Path(__file__).resolve().parents[1] / "docs"
        return help_dir
    
    def get_documentation_paths(self) -> Dict[str, Path]:
        """Get paths to all documentation files."""
        help_dir = self.get_help_directory()
        return {
            "user_guide": help_dir / "USER_GUIDE.md",
            "faq": help_dir / "FAQ.md", 
            "privacy_policy": help_dir / "PRIVACY_POLICY.md",
            "deployment_guide": help_dir / "DEPLOYMENT_GUIDE.md",
            "test_report": help_dir / "FINAL_TEST_REPORT.md"
        }

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
