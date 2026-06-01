#!/usr/bin/env python3
"""
Image Adjustments Component for AI Microscope
Reusable component for image adjustment controls
"""

import customtkinter as ctk
from typing import Optional, Callable, Dict


class ImageAdjustments(ctk.CTkFrame):
    """Reusable image adjustments component."""
    
    def __init__(self, parent, on_change: Optional[Callable] = None, **kwargs):
        """Initialize image adjustments component.
        
        Args:
            parent: Parent widget
            on_change: Callback when adjustments change
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        
        # Title - Professional medical terminology
        title = ctk.CTkLabel(self, text="IMAGE ENHANCEMENT", font=ctk.CTkFont(size=12, weight="bold"))
        title.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Brightness
        ctk.CTkLabel(self, text="Brightness").pack(anchor="w", padx=10)
        self.brightness_slider = ctk.CTkSlider(self, from_=0.5, to=1.5, number_of_steps=100)
        self.brightness_slider.set(1.0)
        self.brightness_slider.pack(pady=5, padx=10, fill="x")
        self.brightness_slider.configure(command=self._on_change)
        
        # Contrast
        ctk.CTkLabel(self, text="Contrast").pack(anchor="w", padx=10)
        self.contrast_slider = ctk.CTkSlider(self, from_=0.5, to=1.5, number_of_steps=100)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(pady=5, padx=10, fill="x")
        self.contrast_slider.configure(command=self._on_change)
    
    def _on_change(self, value: float) -> None:
        """Handle adjustment change.
        
        Args:
            value: Slider value
        """
        if self.on_change:
            self.on_change(self.get_adjustments())
    
    def get_adjustments(self) -> Dict[str, float]:
        """Get current adjustment values.
        
        Returns:
            Dictionary with brightness and contrast values
        """
        return {
            "brightness": self.brightness_slider.get(),
            "contrast": self.contrast_slider.get()
        }
    
    def set_adjustments(self, brightness: float = 1.0, contrast: float = 1.0) -> None:
        """Set adjustment values.
        
        Args:
            brightness: Brightness value
            contrast: Contrast value
        """
        self.brightness_slider.set(brightness)
        self.contrast_slider.set(contrast)
    
    def reset(self) -> None:
        """Reset adjustments to default values."""
        self.set_adjustments(1.0, 1.0)
