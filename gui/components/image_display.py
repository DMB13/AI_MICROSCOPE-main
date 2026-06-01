#!/usr/bin/env python3
"""
Image Display Component for AI Microscope
Reusable component for displaying images and camera feeds
"""

import customtkinter as ctk
from PIL import Image
from typing import Optional


class ImageDisplay(ctk.CTkLabel):
    """Reusable image display component."""
    
    def __init__(self, parent, placeholder_text: str = "No image", **kwargs):
        """Initialize image display.
        
        Args:
            parent: Parent widget
            placeholder_text: Text to show when no image is displayed
            **kwargs: Additional arguments for CTkLabel
        """
        # Remove font from kwargs if present to avoid duplicate
        kwargs.pop('font', None)
        
        super().__init__(
            parent,
            text=placeholder_text,
            font=ctk.CTkFont(size=14),
            **kwargs
        )
        self.placeholder_text = placeholder_text
        self.current_image = None
        self.ctk_image = None
    
    def display_image(self, pil_image: Image.Image, size: tuple = (512, 512)) -> None:
        """Display a PIL image.
        
        Args:
            pil_image: PIL Image to display
            size: Size to resize image to
        """
        try:
            # Resize image
            pil_image = pil_image.resize(size)
            
            # Create CTkImage
            self.ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
            
            # Update display
            self.configure(image=self.ctk_image, text="")
            self.current_image = pil_image
            
        except Exception as e:
            self.configure(text=f"Error: {str(e)}")
    
    def clear(self) -> None:
        """Clear the image display."""
        self.configure(image=None, text=self.placeholder_text)
        self.current_image = None
        self.ctk_image = None
    
    def has_image(self) -> bool:
        """Check if an image is currently displayed."""
        return self.current_image is not None
