#!/usr/bin/env python3
"""
Intelligence Wing View for AI Microscope
Right panel with AI analysis, results, and Grad-CAM display
"""

import customtkinter as ctk
from typing import Optional, Callable

from gui.components.image_display import ImageDisplay
from gui.components.results_display import ResultsDisplay
from utils.logger import log_info


class IntelligenceWing(ctk.CTkFrame):
    """Intelligence wing view - right panel with AI analysis."""
    
    def __init__(
        self,
        parent,
        on_diagnose: Optional[Callable] = None,
        **kwargs
    ):
        """Initialize intelligence wing view.
        
        Args:
            parent: Parent widget
            on_diagnose: Callback for diagnosis button
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)
        self.on_diagnose = on_diagnose
        
        # Title - Professional medical terminology
        title = ctk.CTkLabel(
            self,
            text="DIAGNOSTIC ANALYSIS",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=(10, 20))
        
        # AI Analysis Section
        ai_frame = ctk.CTkFrame(self)
        ai_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(ai_frame, text="ANALYSIS", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        self.analyze_btn = ctk.CTkButton(
            ai_frame,
            text="Run Diagnosis",
            command=self._on_diagnose,
            fg_color="green",
            hover_color="darkgreen",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.analyze_btn.pack(pady=10, padx=10, fill="x")
        
        # Results Display Section
        self.results_display = ResultsDisplay(self)
        self.results_display.pack(fill="x", padx=10, pady=5)
        
        # Grad-CAM Display
        gradcam_frame = ctk.CTkFrame(self)
        gradcam_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(gradcam_frame, text="VISUAL EXPLANATION", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        self.gradcam_display = ImageDisplay(
            gradcam_frame,
            placeholder_text="Grad-CAM\n(run AI diagnosis)",
            font=ctk.CTkFont(size=11)
        )
        self.gradcam_display.pack(pady=10, padx=10, fill="x")
    
    def _on_diagnose(self) -> None:
        """Handle diagnosis button click."""
        if self.on_diagnose:
            self.on_diagnose()
    
    def update_results(self, species: str, confidence: float) -> None:
        """Update the displayed results.
        
        Args:
            species: Identified species name
            confidence: Confidence score (0-1)
        """
        self.results_display.update_results(species, confidence)
    
    def clear_results(self) -> None:
        """Clear the results display."""
        self.results_display.clear()
    
    def set_results_loading(self) -> None:
        """Set results to loading state."""
        self.results_display.set_loading()
    
    def display_gradcam(self, pil_image, size: tuple = (256, 256)) -> None:
        """Display Grad-CAM heatmap.
        
        Args:
            pil_image: PIL Image to display
            size: Size to resize image to
        """
        self.gradcam_display.display_image(pil_image, size)
    
    def clear_gradcam(self) -> None:
        """Clear the Grad-CAM display."""
        self.gradcam_display.clear()
    
    def set_diagnose_enabled(self, enabled: bool) -> None:
        """Enable or disable the diagnosis button.
        
        Args:
            enabled: Whether to enable the button
        """
        state = "normal" if enabled else "disabled"
        self.analyze_btn.configure(state=state)
