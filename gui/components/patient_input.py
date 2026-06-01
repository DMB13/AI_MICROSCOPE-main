#!/usr/bin/env python3
"""
Patient Input Component for AI Microscope
Medical-grade patient ID input with validation and privacy options
"""

import customtkinter as ctk
from typing import Optional, Callable
import re


class PatientInput(ctk.CTkFrame):
    """Medical-grade patient ID input component with validation."""
    
    # Standard format: INSTITUTION-YEAR-SEQUENTIAL (e.g., DMB-2024-0001)
    PATIENT_ID_PATTERN = re.compile(r'^[A-Z]{2,4}-\d{4}-\d{3,}$')
    
    def __init__(self, parent, on_change: Optional[Callable] = None, **kwargs):
        """Initialize patient input component.
        
        Args:
            parent: Parent widget
            on_change: Callback when patient ID changes
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self._anonymous_mode = False
        
        # Title
        title = ctk.CTkLabel(self, text="Patient ID", font=ctk.CTkFont(size=12, weight="bold"))
        title.pack(pady=(10, 2), padx=10, anchor="w")
        
        # Format hint
        hint = ctk.CTkLabel(
            self, 
            text="Format: INSTITUTION-YEAR-NUMBER (e.g., DMB-2024-0001)",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        hint.pack(pady=(0, 5), padx=10, anchor="w")
        
        # Entry field
        self.entry = ctk.CTkEntry(self, placeholder_text="DMB-2024-0001")
        self.entry.pack(pady=2, padx=10, fill="x")
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Validation label
        self.validation_label = ctk.CTkLabel(
            self, 
            text="", 
            font=ctk.CTkFont(size=9),
            text_color="orange"
        )
        self.validation_label.pack(pady=(0, 2), padx=10, anchor="w")
        
        # Anonymization option for research
        self.anon_checkbox = ctk.CTkCheckBox(
            self,
            text="Research Mode (De-identified)",
            font=ctk.CTkFont(size=10),
            command=self._toggle_anonymization
        )
        self.anon_checkbox.pack(pady=5, padx=10, anchor="w")
        
        # Privacy note
        privacy_note = ctk.CTkLabel(
            self,
            text="Patient data is stored locally only",
            font=ctk.CTkFont(size=8),
            text_color="gray"
        )
        privacy_note.pack(pady=(0, 5), padx=10, anchor="w")
    
    def _on_key_release(self, event) -> None:
        """Handle key release event."""
        self._validate_format()
        if self.on_change:
            self.on_change(self.get_patient_id())
    
    def _on_focus_out(self, event) -> None:
        """Validate on focus out."""
        self._validate_format()
    
    def _validate_format(self) -> bool:
        """Validate patient ID format and update UI."""
        if self._anonymous_mode:
            self.validation_label.configure(text="Research mode - no ID required", text_color="blue")
            return True
        
        patient_id = self.get_patient_id()
        if not patient_id:
            self.validation_label.configure(text="Patient ID is required", text_color="orange")
            return False
        
        if self.PATIENT_ID_PATTERN.match(patient_id):
            self.validation_label.configure(text="Valid format", text_color="green")
            return True
        else:
            self.validation_label.configure(
                text="Invalid format. Use: XXX-YYYY-ZZZ (e.g., DMB-2024-001)", 
                text_color="orange"
            )
            return False
    
    def _toggle_anonymization(self):
        """Enable/disable research mode (anonymized)."""
        self._anonymous_mode = bool(self.anon_checkbox.get())
        if self._anonymous_mode:
            self.entry.configure(state="disabled")
            self.entry.delete(0, "end")
            self.entry.insert(0, "ANONYMOUS")
            self.validation_label.configure(text="Research mode - no ID required", text_color="blue")
        else:
            self.entry.configure(state="normal")
            self.entry.delete(0, "end")
            self.validation_label.configure(text="Patient ID is required", text_color="orange")
        
        if self.on_change:
            self.on_change(self.get_patient_id())
    
    def get_patient_id(self) -> str:
        """Get the current patient ID."""
        if self._anonymous_mode:
            return "ANONYMOUS"
        return self.entry.get().strip() if self.entry.get() else ""
    
    def set_patient_id(self, patient_id: str) -> None:
        """Set the patient ID."""
        self.entry.delete(0, "end")
        self.entry.insert(0, patient_id)
        self._validate_format()
    
    def clear(self) -> None:
        """Clear the patient ID."""
        self.entry.delete(0, "end")
        self.validation_label.configure(text="")
        self._anonymous_mode = False
        self.anon_checkbox.deselect()
        self.entry.configure(state="normal")
    
    def is_valid(self) -> bool:
        """Medical-grade validation with format checking."""
        if self._anonymous_mode:
            return True
        patient_id = self.get_patient_id()
        if not patient_id:
            return False
        return bool(self.PATIENT_ID_PATTERN.match(patient_id))
    
    def is_anonymous(self) -> bool:
        """Check if in anonymous/research mode."""
        return self._anonymous_mode
