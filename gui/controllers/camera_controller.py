#!/usr/bin/env python3
"""
Camera Controller for AI Microscope
Manages camera operations and bridges GUI with hardware layer
"""

from typing import Optional, Callable, List, Any, Tuple
import cv2
from PIL import Image

from hardware.camera import CameraService
from utils.logger import log_info, log_error, log_warning
from utils.error_handling import retry_on_exception, handle_error_gracefully


class CameraController:
    """Controller for camera operations with auto-reconnection support."""
    
    def __init__(self, camera_service: Optional[CameraService] = None):
        """Initialize camera controller.
        
        Args:
            camera_service: CameraService instance (creates new if None)
        """
        self.camera_service = camera_service or CameraService()
        self.current_frame = None
        self.on_frame_callback: Optional[Callable] = None
        self.on_camera_changed: Optional[Callable] = None
        self.current_camera_index: Optional[int] = None
        self.auto_reconnect_enabled = True
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
    
    def detect_cameras(self, max_index: int = 10) -> List[str]:
        """Detect available cameras.
        
        Args:
            max_index: Maximum camera index to check
            
        Returns:
            List of camera names
        """
        return self.camera_service.detect_cameras(max_index)
    
    def get_best_camera_index(self, max_index: int = 10) -> int:
        """Get the best available camera index.
        
        Args:
            max_index: Maximum camera index to check
            
        Returns:
            Camera index or -1 if none found
        """
        return self.camera_service.get_best_camera_index(max_index)
    
    @retry_on_exception(max_retries=3, delay=0.5, backoff=1.5, fallback_value=False)
    def start_camera(self, camera_index: int) -> bool:
        """Start camera at specified index with retry logic.
        
        Args:
            camera_index: Camera index to start
            
        Returns:
            True if successful, False otherwise
        """
        log_info(f"Starting camera {camera_index}")
        success = self.camera_service.start(camera_index)
        
        if success:
            self.current_camera_index = camera_index
            self.reconnect_attempts = 0
            log_info(f"Camera {camera_index} started successfully")
            if self.on_camera_changed:
                self.on_camera_changed(True)
        else:
            log_error(f"Failed to start camera {camera_index}")
        
        return success
    
    def stop_camera(self) -> None:
        """Stop the camera."""
        log_info("Stopping camera")
        self.camera_service.stop()
        self.current_frame = None
        
        if self.on_camera_changed:
            self.on_camera_changed(False)
        
        log_info("Camera stopped")
    
    def is_running(self) -> bool:
        """Check if camera is running.
        
        Returns:
            True if running, False otherwise
        """
        return self.camera_service.running
    
    def read_frame(self) -> Optional[Any]:
        """Read a frame from the camera with auto-reconnection.
        
        Returns:
            OpenCV frame or None if no frame available
        """
        frame = self.camera_service.read_frame()
        
        # Auto-reconnection logic
        if frame is None and self.auto_reconnect_enabled and self.current_camera_index is not None:
            if self.reconnect_attempts < self.max_reconnect_attempts:
                log_warning(f"Frame read failed, attempting reconnection ({self.reconnect_attempts + 1}/{self.max_reconnect_attempts})")
                self.reconnect_attempts += 1
                
                # Try to restart camera
                if self.camera_service.start(self.current_camera_index):
                    frame = self.camera_service.read_frame()
                    if frame:
                        log_info("Camera reconnected successfully")
                        self.reconnect_attempts = 0
                    else:
                        log_error("Reconnection failed")
                else:
                    log_error(f"Failed to restart camera {self.current_camera_index}")
            else:
                log_error("Max reconnection attempts reached, stopping camera")
                self.stop_camera()
                self.reconnect_attempts = 0
        
        if frame is not None:
            self.current_frame = frame
            self.reconnect_attempts = 0  # Reset on successful read
        
        return frame
    
    def get_current_frame(self) -> Optional[Any]:
        """Get the most recent frame.
        
        Returns:
            Current OpenCV frame or None
        """
        return self.current_frame
    
    def capture_frame_to_file(self, save_dir: str) -> Optional[str]:
        """Capture current frame to file.
        
        Args:
            save_dir: Directory to save the frame
            
        Returns:
            Path to saved file or None if failed
        """
        if self.current_frame is None:
            log_warning("No frame available to capture")
            return None
        
        return self.camera_service.capture_frame_to_file(self.current_frame, save_dir)
    
    def frame_to_pil(self, frame, size: tuple = (512, 512)) -> Optional[Image.Image]:
        """Convert OpenCV frame to PIL Image.
        
        Args:
            frame: OpenCV frame (BGR)
            size: Size to resize to
            
        Returns:
            PIL Image or None if conversion fails
        """
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize(size)
            return img
        except Exception as e:
            log_error(f"Failed to convert frame to PIL: {str(e)}")
            return None
    
    def set_frame_callback(self, callback: Callable) -> None:
        """Set callback for when new frames are available.
        
        Args:
            callback: Function to call with new frame
        """
        self.on_frame_callback = callback
    
    def set_camera_changed_callback(self, callback: Callable) -> None:
        """Set callback for when camera state changes.
        
        Args:
            callback: Function to call with camera running state
        """
        self.on_camera_changed = callback
