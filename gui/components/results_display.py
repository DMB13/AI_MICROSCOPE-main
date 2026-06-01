#!/usr/bin/env python3
"""
Results Display Component for AI Microscope
Medical-grade diagnosis results with confidence tiers and clinical recommendations
"""

import customtkinter as ctk
from typing import Optional


class ResultsDisplay(ctk.CTkFrame):
    """Medical-grade results display with confidence tiers and clinical guidance."""
    
    # Medical confidence thresholds
    HIGH_CONFIDENCE = 0.95
    ACCEPTABLE_CONFIDENCE = 0.90
    MODERATE_CONFIDENCE = 0.70
    
    def __init__(self, parent, **kwargs):
        """Initialize results display component.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)
        
        # Title - Professional medical terminology
        title = ctk.CTkLabel(self, text="DIAGNOSIS RESULTS", font=ctk.CTkFont(size=12, weight="bold"))
        title.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Main result display
        self.result_label = ctk.CTkLabel(
            self,
            text="No analysis performed",
            font=ctk.CTkFont(size=13, weight="bold"),
            wraplength=250
        )
        self.result_label.pack(pady=5, padx=10)
        
        # Confidence progress bar with label
        ctk.CTkLabel(self, text="Confidence Level:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(5, 0))
        self.confidence_bar = ctk.CTkProgressBar(self)
        self.confidence_bar.pack(pady=5, padx=10, fill="x")
        self.confidence_bar.set(0)
        
        # Clinical recommendation label
        self.recommendation_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            wraplength=250,
            justify="left"
        )
        self.recommendation_label.pack(pady=(5, 10), padx=10)
    
    def update_results(self, species: str, confidence: float) -> None:
        """Update the displayed results with medical-grade confidence tiers.
        
        Args:
            species: Identified species name
            confidence: Confidence score (0-1)
        """
        confidence_percent = confidence * 100
        
        # Medical-grade confidence tiers with recommendations
        if confidence >= self.HIGH_CONFIDENCE:
            status = "HIGH CONFIDENCE"
            color = "#008800"  # Dark green
            recommendation = (
                "This result is suitable for clinical decision support. "
                "Always correlate with laboratory findings."
            )
        elif confidence >= self.ACCEPTABLE_CONFIDENCE:
            status = "ACCEPTABLE CONFIDENCE"
            color = "#66AA00"  # Light green
            recommendation = (
                "Result meets clinical standards. "
                "Verification with laboratory testing is recommended."
            )
        elif confidence >= self.MODERATE_CONFIDENCE:
            status = "MODERATE CONFIDENCE"
            color = "#FF8800"  # Orange
            recommendation = (
                "Consider additional testing or specialist review. "
                "Image quality may be insufficient."
            )
        else:
            status = "LOW CONFIDENCE - REPEAT TEST"
            color = "#CC0000"  # Red
            recommendation = (
                "Sample quality insufficient for reliable diagnosis. "
                "Please re-capture image with proper staining and focus."
            )
        
        # Update display - hide species name if confidence < 70%
        if confidence >= self.MODERATE_CONFIDENCE:
            result_text = f"{status}\n\nOrganism: {species}\nConfidence: {confidence_percent:.1f}%"
        else:
            result_text = f"{status}\n\nConfidence: {confidence_percent:.1f}%"
        
        self.result_label.configure(
            text=result_text,
            text_color=color
        )
        self.confidence_bar.configure(progress_color=color)
        self.confidence_bar.set(confidence)
        
        self.recommendation_label.configure(
            text=f"CLINICAL RECOMMENDATION:\n{recommendation}",
            text_color="#555555"
        )
    
    def clear(self) -> None:
        """Clear the results display."""
        self.result_label.configure(text="No analysis performed", text_color="white")
        self.confidence_bar.set(0)
        self.confidence_bar.configure(progress_color="gray")
        self.recommendation_label.configure(text="")
    
    def set_loading(self) -> None:
        """Set display to loading state."""
        self.result_label.configure(text="ANALYZING SAMPLE...", text_color="#1e4d8c")
        self.confidence_bar.set(0.5)  # Indeterminate-like
        self.confidence_bar.configure(progress_color="#1e4d8c")
        self.recommendation_label.configure(text="Please wait while AI analyzes the image...")
