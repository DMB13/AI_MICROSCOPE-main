#!/usr/bin/env python3
"""
Primary Viewport View for AI Microscope
Center panel with microscope feed and capture button
"""

import customtkinter as ctk
from typing import Optional, Callable

from gui.components.image_display import ImageDisplay
from utils.logger import log_info


class PrimaryViewport(ctk.CTkFrame):
    """Primary viewport view - center panel with microscope feed."""
    
    def __init__(
        self,
        parent,
        on_capture: Optional[Callable] = None,
        **kwargs
    ):
        """Initialize primary viewport view.
        
        Args:
            parent: Parent widget
            on_capture: Callback for capture button
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)
        self.on_capture = on_capture
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="🔬 MICROSCOPE VIEWPORT",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(10, 20))
        
        # Main image display area
        self.image_display = ImageDisplay(
            self,
            placeholder_text="Camera Feed\n(Start camera or upload image)",
            font=ctk.CTkFont(size=14)
        )
        self.image_display.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Capture button - prominent and centered
        capture_frame = ctk.CTkFrame(self)
        capture_frame.pack(fill="x", padx=20, pady=20)
        
        self.capture_btn = ctk.CTkButton(
            capture_frame,
            text="📸 CAPTURE IMAGE",
            command=self._on_capture,
            fg_color="blue",
            hover_color="darkblue",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.capture_btn.pack(pady=10, padx=20, fill="x")
    
    def _on_capture(self) -> None:
        """Handle capture button click."""
        if self.on_capture:
            self.on_capture()
    
    def display_image(self, pil_image, size: tuple = (512, 512)) -> None:
        """Display an image in the viewport.
        
        Args:
            pil_image: PIL Image to display
            size: Size to resize image to
        """
        self.image_display.display_image(pil_image, size)
    
    def clear(self) -> None:
        """Clear the image display."""
        self.image_display.clear()
    
    def has_image(self) -> bool:
        """Check if an image is currently displayed."""
        return self.image_display.has_image()
    
    def set_capture_enabled(self, enabled: bool) -> None:
        """Enable or disable the capture button.
        
        Args:
            enabled: Whether to enable the button
        """
        state = "normal" if enabled else "disabled"
        self.capture_btn.configure(state=state)
