#!/usr/bin/env python3
"""
Clinical Status Bar for AI Microscope
Professional medical status display with patient context and operator info
"""

import customtkinter as ctk
from typing import Optional
from datetime import datetime


class ClinicalStatusBar(ctk.CTkFrame):
    """Professional medical status bar with clinical indicators."""
    
    def __init__(self, parent, **kwargs):
        """Initialize clinical status bar.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)
        
        # Configure appearance
        self.configure(fg_color="#1e4d8c", height=30)
        
        # Left section: Patient context
        self.patient_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.patient_frame.pack(side="left", padx=10, pady=2)
        
        self.patient_label = ctk.CTkLabel(
            self.patient_frame,
            text="Patient: Not selected",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white"
        )
        self.patient_label.pack(side="left")
        
        # Center section: Session status and saved indicator
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(side="left", expand=True, fill="x", padx=20, pady=2)
        
        self.session_label = ctk.CTkLabel(
            self.center_frame,
            text="● Ready",
            font=ctk.CTkFont(size=11),
            text_color="#00FF00"
        )
        self.session_label.pack(side="left")
        
        self.saved_indicator = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="#AAAAAA"
        )
        self.saved_indicator.pack(side="left", padx=(20, 0))
        
        # Right section: Operator and time
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.pack(side="right", padx=10, pady=2)
        
        self.operator_label = ctk.CTkLabel(
            self.right_frame,
            text="Operator: --",
            font=ctk.CTkFont(size=10),
            text_color="white"
        )
        self.operator_label.pack(side="left", padx=(0, 15))
        
        self.time_label = ctk.CTkLabel(
            self.right_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="white"
        )
        self.time_label.pack(side="left")
        
        # Start time update
        self._update_time()
        
        # State tracking
        self._current_patient = None
        self._has_unsaved_data = False
        self._operator_name = "--"
    
    def _update_time(self):
        """Update the time display."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=current_time)
        self.after(1000, self._update_time)
    
    def set_patient(self, patient_id: str, is_anonymous: bool = False):
        """Update patient display.
        
        Args:
            patient_id: Current patient ID
            is_anonymous: Whether in anonymous/research mode
        """
        self._current_patient = patient_id
        
        if is_anonymous:
            display_text = "Patient: [RESEARCH MODE]"
            color = "#88CCFF"
        elif patient_id:
            display_text = f"Patient: {patient_id}"
            color = "white"
        else:
            display_text = "Patient: Not selected"
            color = "#FFAAAA"
        
        self.patient_label.configure(text=display_text, text_color=color)
        
        # Clear saved indicator on patient change
        self._has_unsaved_data = False
        self.saved_indicator.configure(text="")
    
    def set_operator(self, operator_name: str):
        """Set the current operator name.
        
        Args:
            operator_name: Name of logged-in operator
        """
        self._operator_name = operator_name
        self.operator_label.configure(text=f"Operator: {operator_name}")
    
    def set_session_status(self, status: str, color: str = "#00FF00"):
        """Update session status indicator.
        
        Args:
            status: Status text to display
            color: Color for status indicator
        """
        self.session_label.configure(text=status, text_color=color)
    
    def mark_unsaved(self):
        """Mark that there is unsaved data."""
        self._has_unsaved_data = True
        self.saved_indicator.configure(
            text="⚠ UNSAVED DATA",
            text_color="#FF8800"
        )
    
    def mark_saved(self, timestamp: Optional[str] = None):
        """Mark that data has been saved.
        
        Args:
            timestamp: Optional save timestamp
        """
        self._has_unsaved_data = False
        if timestamp:
            self.saved_indicator.configure(
                text=f"Saved: {timestamp}",
                text_color="#00FF00"
            )
        else:
            current_time = datetime.now().strftime("%H:%M")
            self.saved_indicator.configure(
                text=f"Saved: {current_time}",
                text_color="#00FF00"
            )
    
    def get_current_patient(self) -> Optional[str]:
        """Get current patient ID."""
        return self._current_patient
    
    def has_unsaved_data(self) -> bool:
        """Check if there is unsaved data."""
        return self._has_unsaved_data
    
    def show_diagnosis_in_progress(self):
        """Show diagnosis is running."""
        self.set_session_status("● Analyzing...", "#FFAA00")
    
    def show_diagnosis_complete(self):
        """Show diagnosis complete."""
        self.set_session_status("● Analysis Complete", "#00FF00")
        self.mark_unsaved()
    
    def show_ready(self):
        """Show ready state."""
        self.set_session_status("● Ready", "#00FF00")
    
    def show_error(self, message: str = "Error"):
        """Show error state."""
        self.set_session_status(f"● {message}", "#FF0000")
