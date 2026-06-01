#!/usr/bin/env python3
"""
Session Manager for AI Microscope Application
Handles session state persistence and crash recovery
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from utils.logger import log_info, log_error, log_warning


class SessionManager:
    """Manages session state persistence and crash recovery."""
    
    def __init__(self, session_file: Optional[Path] = None):
        """Initialize session manager.
        
        Args:
            session_file: Path to session state file (default: storage/session_state.json)
        """
        if session_file is None:
            base_dir = Path(__file__).resolve().parent.parent
            storage_dir = base_dir / "storage"
            storage_dir.mkdir(exist_ok=True)
            session_file = storage_dir / "session_state.json"
        
        self.session_file = Path(session_file)
        self.session_state: Dict[str, Any] = {}
        self.auto_save_enabled = True
    
    def save_state(self, key: str, value: Any) -> None:
        """Save a session state value.
        
        Args:
            key: State key
            value: State value
        """
        self.session_state[key] = value
        self.session_state["last_updated"] = datetime.now().isoformat()
        
        if self.auto_save_enabled:
            self._save_to_file()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a session state value.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value or default
        """
        return self.session_state.get(key, default)
    
    def load_session(self) -> Dict[str, Any]:
        """Load session state from file.
        
        Returns:
            Loaded session state
        """
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    self.session_state = json.load(f)
                log_info(f"Session loaded from {self.session_file}")
                
                # Check for crash recovery
                if self.session_state.get("last_updated"):
                    last_time = datetime.fromisoformat(self.session_state["last_updated"])
                    time_diff = (datetime.now() - last_time).total_seconds()
                    
                    # If last update was recent (< 5 minutes), possible crash
                    if time_diff < 300:
                        log_warning(f"Possible crash detected. Last session was {int(time_diff)} seconds ago.")
                        return self.session_state.copy()
            else:
                log_info("No previous session found")
        except Exception as e:
            log_error(f"Failed to load session: {str(e)}", exc_info=True)
        
        return {}
    
    def _save_to_file(self) -> None:
        """Save session state to file."""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_state, f, indent=2)
        except Exception as e:
            log_error(f"Failed to save session: {str(e)}", exc_info=True)
    
    def clear_session(self) -> None:
        """Clear current session state."""
        self.session_state = {}
        self._save_to_file()
        log_info("Session cleared")
    
    def save_camera_state(self, camera_index: int, is_running: bool) -> None:
        """Save camera state.
        
        Args:
            camera_index: Camera index
            is_running: Whether camera is running
        """
        self.save_state("camera", {
            "index": camera_index,
            "running": is_running
        })
    
    def get_camera_state(self) -> Optional[Dict[str, Any]]:
        """Get saved camera state.
        
        Returns:
            Camera state dict or None
        """
        return self.get_state("camera")
    
    def save_image_adjustments(self, brightness: float, contrast: float) -> None:
        """Save image adjustment values.
        
        Args:
            brightness: Brightness value
            contrast: Contrast value
        """
        self.save_state("image_adjustments", {
            "brightness": brightness,
            "contrast": contrast
        })
    
    def get_image_adjustments(self) -> Optional[Dict[str, float]]:
        """Get saved image adjustments.
        
        Returns:
            Adjustment dict or None
        """
        return self.get_state("image_adjustments")
    
    def save_last_image_path(self, image_path: str) -> None:
        """Save last captured/uploaded image path.
        
        Args:
            image_path: Path to image
        """
        self.save_state("last_image_path", image_path)
    
    def get_last_image_path(self) -> Optional[str]:
        """Get last image path.
        
        Returns:
            Image path or None
        """
        return self.get_state("last_image_path")
    
    def mark_recovery_complete(self) -> None:
        """Mark crash recovery as complete."""
        self.save_state("recovery_complete", True)
    
    def is_recovery_needed(self) -> bool:
        """Check if crash recovery is needed.
        
        Returns:
            True if recovery needed, False otherwise
        """
        return not self.get_state("recovery_complete", False)
