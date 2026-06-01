#!/usr/bin/env python3
"""
Camera Controls Component for AI Microscope
Reusable component for camera selection and control
"""

import customtkinter as ctk
from typing import Optional, Callable, List


class CameraControls(ctk.CTkFrame):
    """Reusable camera controls component."""
    
    def __init__(
        self,
        parent,
        on_camera_select: Optional[Callable] = None,
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        **kwargs
    ):
        """Initialize camera controls component.
        
        Args:
            parent: Parent widget
            on_camera_select: Callback when camera is selected
            on_start: Callback when start button is clicked
            on_stop: Callback when stop button is clicked
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)
        self.on_camera_select = on_camera_select
        self.on_start = on_start
        self.on_stop = on_stop
        
        # Title - Professional medical terminology
        title = ctk.CTkLabel(self, text="MICROSCOPE CAMERA", font=ctk.CTkFont(size=12, weight="bold"))
        title.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Camera dropdown
        self.camera_menu = ctk.CTkOptionMenu(self, values=["Detecting..."], command=self._on_select)
        self.camera_menu.pack(pady=5, padx=10, fill="x")
        
        # Button frame
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        # Start button
        self.start_btn = ctk.CTkButton(btn_frame, text="Start Live", command=self._on_start_click)
        self.start_btn.pack(pady=2, padx=5, fill="x")
        
        # Stop button
        self.stop_btn = ctk.CTkButton(btn_frame, text="Stop Live", command=self._on_stop_click)
        self.stop_btn.pack(pady=2, padx=5, fill="x")
    
    def _on_select(self, value: str) -> None:
        """Handle camera selection."""
        if self.on_camera_select:
            self.on_camera_select(value)
    
    def _on_start_click(self) -> None:
        """Handle start button click."""
        if self.on_start:
            self.on_start()
    
    def _on_stop_click(self) -> None:
        """Handle stop button click."""
        if self.on_stop:
            self.on_stop()
    
    def update_cameras(self, cameras: List[str]) -> None:
        """Update the list of available cameras.
        
        Args:
            cameras: List of camera names
        """
        self.camera_menu.configure(values=cameras)
    
    def get_selected_camera(self) -> str:
        """Get the currently selected camera."""
        return self.camera_menu.get()
    
    def set_selected_camera(self, camera_name: str) -> None:
        """Set the selected camera.
        
        Args:
            camera_name: Name of camera to select
        """
        self.camera_menu.set(camera_name)
    
    def set_running_state(self, is_running: bool) -> None:
        """Update button states based on camera running state.
        
        Args:
            is_running: Whether camera is currently running
        """
        if is_running:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
