#!/usr/bin/env python3
"""
Patient Safety Dialog for AI Microscope
Handles patient change warnings and unsaved data protection
"""

import customtkinter as ctk
from typing import Optional, Callable


class PatientSafetyDialog(ctk.CTkToplevel):
    """Dialog for patient safety warnings and confirmations."""
    
    def __init__(
        self,
        parent,
        old_patient_id: str,
        new_patient_id: str,
        has_unsaved_data: bool = False,
        on_save_first: Optional[Callable] = None,
        on_continue: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None
    ):
        """Initialize patient safety dialog.
        
        Args:
            parent: Parent window
            old_patient_id: Previous patient ID
            new_patient_id: New patient ID being entered
            has_unsaved_data: Whether there are unsaved diagnoses
            on_save_first: Callback if user chooses to save first
            on_continue: Callback if user continues without saving
            on_cancel: Callback if user cancels the change
        """
        super().__init__(parent)
        
        self.old_patient_id = old_patient_id
        self.new_patient_id = new_patient_id
        self.has_unsaved_data = has_unsaved_data
        self.on_save_first = on_save_first
        self.on_continue = on_continue
        self.on_cancel = on_cancel
        
        self.title("Patient Change Warning")
        self.geometry("500x350")
        self.resizable(False, False)
        
        # Set window icon
        try:
            from pathlib import Path
            icon_path = Path(__file__).resolve().parent.parent.parent / "logo.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (350 // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        # Warning header
        header_frame = ctk.CTkFrame(self, fg_color="#FF6B00")
        header_frame.pack(fill="x", padx=0, pady=0)
        
        warning_label = ctk.CTkLabel(
            header_frame,
            text="⚠️ PATIENT CHANGE DETECTED",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        warning_label.pack(pady=15)
        
        # Main content
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Patient change info
        change_text = f"You are switching patients:\n\n"
        change_text += f"FROM: {self.old_patient_id}\n"
        change_text += f"TO: {self.new_patient_id}\n\n"
        
        if self.has_unsaved_data:
            change_text += "WARNING: You have unsaved diagnosis data for the current patient.\n"
            change_text += "This data will be lost if you continue."
        
        info_label = ctk.CTkLabel(
            content_frame,
            text=change_text,
            font=ctk.CTkFont(size=12),
            wraplength=440,
            justify="left"
        )
        info_label.pack(pady=(0, 20))
        
        # Clinical recommendation
        if self.has_unsaved_data:
            rec_text = "CLINICAL RECOMMENDATION:\n"
            rec_text += "Save current patient data before switching to maintain \n"
            rec_text += "complete medical records and audit trail."
            
            rec_label = ctk.CTkLabel(
                content_frame,
                text=rec_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                wraplength=440,
                text_color="#1e4d8c",
                justify="left"
            )
            rec_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=15)
        
        if self.has_unsaved_data:
            # Save First button
            save_btn = ctk.CTkButton(
                button_frame,
                text="💾 Save Current Patient First",
                command=self._on_save_first,
                fg_color="green",
                hover_color="darkgreen",
                height=40,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            save_btn.pack(fill="x", pady=(0, 10))
        
        # Continue button
        continue_text = "Continue Without Saving" if self.has_unsaved_data else "Continue"
        continue_btn = ctk.CTkButton(
            button_frame,
            text=continue_text,
            command=self._on_continue,
            fg_color="orange",
            hover_color="darkorange",
            height=35
        )
        continue_btn.pack(fill="x", pady=(0, 10))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel - Stay on Current Patient",
            command=self._on_cancel,
            fg_color="gray",
            hover_color="darkgray",
            height=35
        )
        cancel_btn.pack(fill="x")
    
    def _on_save_first(self) -> None:
        """Handle save first button."""
        if self.on_save_first:
            self.on_save_first()
        self.destroy()
    
    def _on_continue(self) -> None:
        """Handle continue button."""
        if self.on_continue:
            self.on_continue()
        self.destroy()
    
    def _on_cancel(self) -> None:
        """Handle cancel button."""
        if self.on_cancel:
            self.on_cancel()
        self.destroy()


class UnsavedDataDialog(ctk.CTkToplevel):
    """Dialog warning about unsaved data before exit."""
    
    def __init__(
        self,
        parent,
        patient_id: str,
        on_save: Optional[Callable] = None,
        on_discard: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None
    ):
        """Initialize unsaved data dialog."""
        super().__init__(parent)
        
        self.patient_id = patient_id
        self.on_save = on_save
        self.on_discard = on_discard
        self.on_cancel = on_cancel
        
        self.title("Unsaved Data Warning")
        self.geometry("450x300")
        self.resizable(False, False)
        
        # Set window icon
        try:
            from pathlib import Path
            icon_path = Path(__file__).resolve().parent.parent.parent / "logo.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        # Warning header
        header = ctk.CTkLabel(
            self,
            text="⚠️ UNSAVED DATA",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="orange"
        )
        header.pack(pady=(20, 10))
        
        # Info text
        info_text = f"Patient {self.patient_id} has unsaved diagnosis data.\n\n"
        info_text += "Medical records must be complete for patient safety \n"
        info_text += "and regulatory compliance."
        
        info_label = ctk.CTkLabel(
            self,
            text=info_text,
            font=ctk.CTkFont(size=12),
            wraplength=400,
            justify="center"
        )
        info_label.pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Data",
            command=self._on_save_click,
            fg_color="green",
            hover_color="darkgreen",
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_btn.pack(fill="x", pady=(0, 10))
        
        discard_btn = ctk.CTkButton(
            button_frame,
            text="Discard Changes",
            command=self._on_discard_click,
            fg_color="red",
            hover_color="darkred",
            height=35
        )
        discard_btn.pack(fill="x", pady=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel_click,
            fg_color="gray",
            hover_color="darkgray",
            height=35
        )
        cancel_btn.pack(fill="x")
    
    def _on_save_click(self) -> None:
        if self.on_save:
            self.on_save()
        self.destroy()
    
    def _on_discard_click(self) -> None:
        if self.on_discard:
            self.on_discard()
        self.destroy()
    
    def _on_cancel_click(self) -> None:
        if self.on_cancel:
            self.on_cancel()
        self.destroy()
