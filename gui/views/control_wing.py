#!/usr/bin/env python3
"""
Control Wing View for AI Microscope
Left panel with patient ID, camera controls, and image adjustments
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional, Callable

from gui.components.patient_input import PatientInput
from gui.components.camera_controls import CameraControls
from gui.components.image_adjustments import ImageAdjustments
from utils.logger import log_info


class ControlWing(ctk.CTkFrame):
    """Control wing view - left panel with controls."""
    
    def __init__(
        self,
        parent,
        on_upload: Optional[Callable] = None,
        on_settings: Optional[Callable] = None,
        on_export: Optional[Callable] = None,
        on_camera_select: Optional[Callable] = None,
        on_camera_start: Optional[Callable] = None,
        on_camera_stop: Optional[Callable] = None,
        on_image_adjustment_change: Optional[Callable] = None,
        **kwargs
    ):
        """Initialize control wing view.
        
        Args:
            parent: Parent widget
            on_upload: Callback for upload button
            on_settings: Callback for settings button
            on_export: Callback for export button
            on_camera_select: Callback for camera selection
            on_camera_start: Callback for camera start
            on_camera_stop: Callback for camera stop
            on_image_adjustment_change: Callback when image adjustments change
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)
        self.on_upload = on_upload
        self.on_settings = on_settings
        self.on_export = on_export
        self.on_camera_select = on_camera_select
        self.on_camera_start = on_camera_start
        self.on_camera_stop = on_camera_stop
        self.on_image_adjustment_change = on_image_adjustment_change
        
        # Title - Professional medical terminology
        title = ctk.CTkLabel(self, text="PATIENT & CONTROLS", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(10, 16))
        
        # Patient ID Section
        self.patient_input = PatientInput(self)
        self.patient_input.pack(fill="x", padx=10, pady=5)
        
        # Camera Section
        self.camera_controls = CameraControls(
            self,
            on_camera_select=self.on_camera_select,
            on_start=self.on_camera_start,
            on_stop=self.on_camera_stop
        )
        self.camera_controls.pack(fill="x", padx=10, pady=5)
        
        # Image Adjustments Section
        self.image_adjustments = ImageAdjustments(
            self,
            on_change=self.on_image_adjustment_change
        )
        self.image_adjustments.pack(fill="x", padx=10, pady=5)
        
        # Upload button
        self.upload_btn = ctk.CTkButton(self, text="Upload Image", command=self._on_upload)
        self.upload_btn.pack(pady=20, padx=10, fill="x")
        
        # Settings button
        self.settings_btn = ctk.CTkButton(self, text="Settings", command=self._on_settings)
        self.settings_btn.pack(pady=5, padx=10, fill="x")
        
        # Export Section
        export_frame = ctk.CTkFrame(self)
        export_frame.pack(fill="x", padx=8, pady=12)
        
        ctk.CTkLabel(export_frame, text="EXPORT", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(8, 5))
        
        self.export_btn = ctk.CTkButton(
            export_frame,
            text="Generate Report",
            command=self._on_export,
            fg_color="orange",
            hover_color="darkorange"
        )
        self.export_btn.pack(pady=8, padx=8, fill="x")
    
    def _on_upload(self) -> None:
        """Handle upload button click."""
        if self.on_upload:
            self.on_upload()
    
    def _on_settings(self) -> None:
        """Handle settings button click."""
        if self.on_settings:
            self.on_settings()
    
    def _on_export(self) -> None:
        """Handle export button click."""
        if self.on_export:
            self.on_export()
    
    def get_patient_id(self) -> str:
        """Get the current patient ID."""
        return self.patient_input.get_patient_id()
    
    def set_patient_id(self, patient_id: str) -> None:
        """Set the patient ID."""
        self.patient_input.set_patient_id(patient_id)
    
    def update_cameras(self, cameras: list) -> None:
        """Update the list of available cameras.
        
        Args:
            cameras: List of camera names
        """
        self.camera_controls.update_cameras(cameras)
    
    def get_selected_camera(self) -> str:
        """Get the currently selected camera."""
        return self.camera_controls.get_selected_camera()
    
    def set_selected_camera(self, camera_name: str) -> None:
        """Set the selected camera."""
        self.camera_controls.set_selected_camera(camera_name)
    
    def set_camera_running_state(self, is_running: bool) -> None:
        """Update camera button states."""
        self.camera_controls.set_running_state(is_running)
    
    def get_image_adjustments(self) -> dict:
        """Get current image adjustment values."""
        return self.image_adjustments.get_adjustments()
    
    def set_image_adjustments(self, brightness: float, contrast: float) -> None:
        """Set image adjustment values."""
        self.image_adjustments.set_adjustments(brightness, contrast)
