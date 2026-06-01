#!/usr/bin/env python3
"""
Camera Hardware Interface for AI Microscope Application
Handles camera detection and frame capture
"""

from typing import List, Optional, Any
import cv2
import time       # Global import to fix NameError
import os         # Global import for path handling
import datetime   # Global import for timestamps

from core.domain.models import CameraInfo
from utils.logger import log_info, log_error, log_warning
from config.constants import MAX_CAMERA_INDEX


class CameraService:
    """Hardware interface for camera operations."""
    
    def __init__(self, backend: Any = None) -> None:
        """Initialize camera service."""
        self.backend = backend or cv2
        self.cap: Optional[Any] = None
        self.running: bool = False
    
    def detect_cameras(self, max_index: int = MAX_CAMERA_INDEX) -> List[str]:
        """Detect available camera indices with aggressive detection and USB priority."""
        cams: List[str] = []
        usb_cameras: List[str] = []
        other_cameras: List[str] = []
        
        # Suppress OpenCV errors during detection
        os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
        self.backend.setLogLevel(0)
        
        # Check all indices aggressively
        for i in range(max_index + 1):
            try:
                # Try multiple backend options for robustness
                cap = None
                for backend in [self.backend.CAP_DSHOW, self.backend.CAP_V4L2, 0]:
                    try:
                        cap = self.backend.VideoCapture(i, backend)
                        if cap is not None and cap.isOpened():
                            break
                    except Exception:
                        continue
                
                if cap is None:
                    cap = self.backend.VideoCapture(i)
                
                if cap is not None and cap.isOpened():
                    # Try to get camera info to identify USB cameras
                    try:
                        backend_name = cap.getBackendName()
                        is_usb = 'DSHOW' in backend_name or 'V4L2' in backend_name or i > 0
                    except Exception:
                        is_usb = i > 0  # Assume index > 0 is USB camera
                    
                    cam_name = f"Camera {i}"
                    if is_usb:
                        cam_name += " (USB)"
                        usb_cameras.append(cam_name)
                    else:
                        other_cameras.append(cam_name)
                    
                    cap.release()
            except Exception:
                continue
        
        # Prioritize USB cameras
        cams = usb_cameras + other_cameras
        
        if not cams:
            cams = ["No camera detected"]
        
        log_info(f"Detected {len(cams)} camera(s)")
        return cams
    
    def get_best_camera_index(self, max_index: int = MAX_CAMERA_INDEX) -> int:
        """Get the best available camera index with USB priority."""
        for i in range(max_index, 0, -1):
            try:
                cap = None
                for backend in [self.backend.CAP_DSHOW, self.backend.CAP_V4L2, 0]:
                    try:
                        cap = self.backend.VideoCapture(i, backend)
                        if cap is not None and cap.isOpened():
                            break
                    except Exception:
                        continue
                
                if cap is None:
                    cap = self.backend.VideoCapture(i)
                
                if cap is not None and cap.isOpened():
                    cap.release()
                    log_info(f"Selected camera {i} (USB)")
                    return i
            except Exception:
                continue
        
        try:
            cap = self.backend.VideoCapture(0)
            if cap is not None and cap.isOpened():
                cap.release()
                log_info("Selected camera 0 (built-in)")
                return 0
        except Exception:
            pass
        
        log_error("No camera found")
        return -1 
    
    def start(self, index: int) -> bool:
        """Start a camera stream at the given index."""
        if self.cap is not None and getattr(self.cap, "isOpened", lambda: False)():
            self.stop()
        
        try:
            self.cap = self.backend.VideoCapture(index)
        except Exception:
            self.cap = self.backend.VideoCapture(index)
        
        if self.cap is not None and self.cap.isOpened():
            self.running = True
            log_info(f"Camera {index} started successfully")
            return True
        
        log_error(f"Failed to start camera {index}")
        return False
    
    def stop(self) -> None:
        """Stop the camera stream."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.running = False
        log_info("Camera stopped")
    
    def read_frame(self) -> Optional[Any]:
        """Read a single frame from the active camera."""
        if self.cap is None or not self.running:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    # FIXED: Function name, arguments, and indentation are preserved to protect the codebase
    def capture_frame_to_file(self, frame: Any, save_dir: str) -> Optional[str]:
        """Save a frame to a file. (Indentation fixed to stay inside CameraService)"""
        from pathlib import Path
        
        try:
            save_path = Path(save_dir)
            save_path.mkdir(parents=True, exist_ok=True)
            
            # Using datetime from top-level import
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.png"
            filepath = save_path / filename
            
            # Save using OpenCV
            cv2.imwrite(str(filepath), frame)
            log_info(f"Frame saved to {filepath}")
            return str(filepath)
            
        except Exception as e:
            log_error(f"Failed to save frame: {str(e)}", exc_info=True)
            return None