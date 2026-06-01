#!/usr/bin/env python3
"""
First-Run Setup Wizard for AI Microscope Application
Guides new users through initial configuration
"""

import customtkinter as ctk
from typing import Optional, Callable
from pathlib import Path

from core.localization import Localization, Language, t


class FirstRunWizard(ctk.CTkToplevel):
    """First-run setup wizard dialog."""
    
    def __init__(self, parent, on_complete: Callable):
        """Initialize first-run wizard.
        
        Args:
            parent: Parent window
            on_complete: Callback when wizard completes
        """
        super().__init__(parent)
        
        self.parent = parent
        self.on_complete = on_complete
        self.localization = Localization()
        self.current_page = 0
        self.config = {
            "language": Language.ENGLISH,
            "camera_index": 0,
            "patient_id_required": True,
            "theme": "System"
        }
        
        self._setup_window()
        self._create_pages()
        self._show_page(0)
    
    def _setup_window(self) -> None:
        """Setup wizard window."""
        self.title("DMB AI Microscope - First Run Setup")
        self.geometry("600x450")
        self.resizable(False, False)
        
        # Set window icon
        try:
            from pathlib import Path
            icon_path = Path(__file__).resolve().parent.parent.parent / "logo.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (450 // 2)
        self.geometry(f"+{x}+{y}")
        
        # Make modal
        self.transient(self.parent)
        self.grab_set()
    
    def _create_pages(self) -> None:
        """Create wizard pages."""
        self.pages = []
        
        # Page 1: Welcome
        self.pages.append(self._create_welcome_page())
        
        # Page 2: Language Selection
        self.pages.append(self._create_language_page())
        
        # Page 3: Camera Setup
        self.pages.append(self._create_camera_page())
        
        # Page 4: Clinical Settings
        self.pages.append(self._create_clinical_page())
        
        # Page 5: Complete
        self.pages.append(self._create_complete_page())
        
        # Navigation buttons
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        self.back_button = ctk.CTkButton(
            self.button_frame,
            text=t("cancel_button"),
            command=self._on_back,
            width=100
        )
        self.back_button.pack(side="left")
        
        self.next_button = ctk.CTkButton(
            self.button_frame,
            text="Next",
            command=self._on_next,
            width=100
        )
        self.next_button.pack(side="right")
        
        self._update_buttons()
    
    def _create_welcome_page(self) -> ctk.CTkFrame:
        """Create welcome page."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="Welcome to AI Microscope",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(40, 20))
        
        description = ctk.CTkLabel(
            frame,
            text="This wizard will guide you through the initial setup\nof the AI Microscope application.",
            font=("Arial", 14)
        )
        description.pack(pady=20)
        
        features = [
            "• AI-powered bacterial identification",
            "• 39 bacterial species supported",
            "• Clinical-grade accuracy (90%+ confidence)",
            "• Multi-language support (English/Swahili)",
            "• Data encryption and audit trails"
        ]
        
        for feature in features:
            label = ctk.CTkLabel(frame, text=feature, font=("Arial", 12))
            label.pack(pady=5)
        
        return frame
    
    def _create_language_page(self) -> ctk.CTkFrame:
        """Create language selection page."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="Select Language / Chagua Lugha",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(40, 20))
        
        self.language_var = ctk.StringVar(value="English")
        
        languages = [
            ("English", Language.ENGLISH),
            ("Kiswahili", Language.SWAHILI)
        ]
        
        for name, lang in languages:
            rb = ctk.CTkRadioButton(
                frame,
                text=name,
                variable=self.language_var,
                value=name,
                command=lambda l=lang: self._on_language_change(l)
            )
            rb.pack(pady=10)
        
        return frame
    
    def _create_camera_page(self) -> ctk.CTkFrame:
        """Create camera setup page."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="Camera Setup",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(40, 20))
        
        label = ctk.CTkLabel(
            frame,
            text="Select your camera index:",
            font=("Arial", 12)
        )
        label.pack(pady=10)
        
        self.camera_var = ctk.IntVar(value=0)
        
        for i in range(4):
            rb = ctk.CTkRadioButton(
                frame,
                text=f"Camera {i}",
                variable=self.camera_var,
                value=i,
                command=self._on_camera_change
            )
            rb.pack(pady=5)
        
        note = ctk.CTkLabel(
            frame,
            text="Note: If unsure, select Camera 0",
            font=("Arial", 10),
            text_color="gray"
        )
        note.pack(pady=20)
        
        return frame
    
    def _create_clinical_page(self) -> ctk.CTkFrame:
        """Create clinical settings page."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="Clinical Settings",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(40, 20))
        
        self.patient_id_var = ctk.BooleanVar(value=True)
        
        checkbox = ctk.CTkCheckBox(
            frame,
            text="Require Patient ID for diagnosis",
            variable=self.patient_id_var,
            command=self._on_patient_id_change
        )
        checkbox.pack(pady=20)
        
        note = ctk.CTkLabel(
            frame,
            text="Enabling this ensures all diagnoses have patient identification\nfor regulatory compliance and traceability.",
            font=("Arial", 10),
            text_color="gray"
        )
        note.pack(pady=10)
        
        return frame
    
    def _create_complete_page(self) -> ctk.CTkFrame:
        """Create completion page."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="Setup Complete!",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(40, 20))
        
        description = ctk.CTkLabel(
            frame,
            text="AI Microscope is now ready to use.",
            font=("Arial", 14)
        )
        description.pack(pady=20)
        
        summary = ctk.CTkLabel(
            frame,
            text=f"Language: {self.config['language'].value}\n"
                 f"Camera: {self.config['camera_index']}\n"
                 f"Patient ID Required: {self.config['patient_id_required']}",
            font=("Arial", 12)
        )
        summary.pack(pady=20)
        
        return frame
    
    def _show_page(self, page_index: int) -> None:
        """Show specific page.
        
        Args:
            page_index: Page index to show
        """
        # Hide all pages
        for page in self.pages:
            page.pack_forget()
        
        # Show current page
        self.pages[page_index].pack(fill="both", expand=True)
        self.current_page = page_index
        self._update_buttons()
    
    def _update_buttons(self) -> None:
        """Update navigation buttons."""
        if self.current_page == 0:
            self.back_button.configure(text="Cancel", command=self._on_cancel)
        else:
            self.back_button.configure(text=t("cancel_button"), command=self._on_back)
        
        if self.current_page == len(self.pages) - 1:
            self.next_button.configure(text="Finish", command=self._on_finish)
        else:
            self.next_button.configure(text="Next", command=self._on_next)
    
    def _on_language_change(self, language: Language) -> None:
        """Handle language change.
        
        Args:
            language: Selected language
        """
        self.config["language"] = language
        self.localization.set_language(language)
    
    def _on_camera_change(self) -> None:
        """Handle camera change."""
        self.config["camera_index"] = self.camera_var.get()
    
    def _on_patient_id_change(self) -> None:
        """Handle patient ID requirement change."""
        self.config["patient_id_required"] = self.patient_id_var.get()
    
    def _on_next(self) -> None:
        """Handle next button click."""
        if self.current_page < len(self.pages) - 1:
            self._show_page(self.current_page + 1)
    
    def _on_back(self) -> None:
        """Handle back button click."""
        if self.current_page > 0:
            self._show_page(self.current_page - 1)
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.destroy()
    
    def _on_finish(self) -> None:
        """Handle finish button click."""
        self.destroy()
        if self.on_complete:
            self.on_complete(self.config)


def check_first_run() -> bool:
    """Check if this is the first run.
    
    Returns:
        True if first run, False otherwise
    """
    config_file = Path(__file__).parent.parent.parent / "storage" / "setup_complete.flag"
    return not config_file.exists()


def mark_setup_complete() -> None:
    """Mark setup as complete."""
    config_file = Path(__file__).parent.parent.parent / "storage" / "setup_complete.flag"
    config_file.parent.mkdir(exist_ok=True)
    config_file.touch()
