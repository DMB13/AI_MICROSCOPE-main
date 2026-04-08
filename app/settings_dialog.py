"""
Settings Dialog for AI Microscope Application.
Rewritten to fix CTkSlider label_text errors and missing method definitions.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import customtkinter as ctk
from typing import Dict, Any, Callable, Optional
import logging
import sys

# Ensure local settings_manager can be imported whether run as a script or package
sys.path.insert(0, str(Path(__file__).resolve().parent))
from settings_manager import SettingsManager

logger = logging.getLogger(__name__)

class SettingsDialog(ctk.CTkToplevel):
    """Comprehensive settings dialog for the AI Microscope application."""
    
    def __init__(self, parent, settings_manager: SettingsManager, on_save_callback: Optional[Callable] = None):
        super().__init__(parent)
        
        self.parent = parent
        self.settings_manager = settings_manager
        self.on_save_callback = on_save_callback
        
        self.title("AI Microscope Settings")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Make dialog modal - simplified approach
        self.transient(parent)
        self.focus_force()
        
        # Create main container with scrollbar
        self.main_frame = ctk.CTkScrollableFrame(self, label_text="Application Settings")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Settings widgets storage
        self.widgets = {}
        
        # Create settings sections
        self._create_camera_settings()
        self._create_image_adjustments()
        self._create_ai_settings()
        self._create_export_settings()
        self._create_ui_settings()
        self._create_clinical_settings()
        self._create_advanced_settings()
        self._create_help_section()
        
        # Create buttons
        self._create_buttons()
        
        # Load current settings
        self._load_settings_to_widgets()
        
        # Center dialog and grab after fully displayed
        self.after(200, self._center_and_grab)

    def _create_camera_settings(self):
        """Create camera settings section."""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        title = ctk.CTkLabel(frame, text="📷 Camera Settings", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(10, 5))

        # Camera Index
        ctk.CTkLabel(frame, text="Camera Index").pack(anchor="w", padx=10)
        self.widgets["camera_index"] = ctk.CTkSlider(
            frame, from_=0, to=5, number_of_steps=5
        )
        self.widgets["camera_index"].pack(fill="x", padx=10, pady=(0, 10))
        
        # Resolution
        res_frame = ctk.CTkFrame(frame)
        res_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(res_frame, text="Resolution:").pack(side="left", padx=(0, 10))
        self.widgets["resolution"] = ctk.CTkOptionMenu(
            res_frame, values=["640x480", "1280x720", "1920x1080", "2560x1440"]
        )
        self.widgets["resolution"].pack(side="left", fill="x", expand=True)
        
        # FPS
        ctk.CTkLabel(frame, text="Frames Per Second").pack(anchor="w", padx=10)
        self.widgets["fps"] = ctk.CTkSlider(
            frame, from_=15, to=60, number_of_steps=45
        )
        self.widgets["fps"].pack(fill="x", padx=10, pady=(0, 10))
        
        # Auto detect
        self.widgets["auto_detect"] = ctk.CTkCheckBox(
            frame, text="Auto-detect cameras on startup"
        )
        self.widgets["auto_detect"].pack(anchor="w", padx=10, pady=5)

    def _create_image_adjustments(self):
        """Create image adjustment settings section."""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        title = ctk.CTkLabel(frame, text="🎨 Image Adjustments", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(10, 5))
        
        adjustments = [
            ("brightness", "Brightness", -100, 100, 201),
            ("contrast", "Contrast", -100, 100, 201),
            ("saturation", "Saturation", -100, 100, 201),
            ("sharpness", "Sharpness", -100, 100, 201),
            ("gamma", "Gamma", 0.1, 3.0, 29)
        ]
        
        for key, label, min_val, max_val, steps in adjustments:
            ctk.CTkLabel(frame, text=label).pack(anchor="w", padx=10)
            slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, number_of_steps=steps)
            self.widgets[key] = slider
            slider.pack(fill="x", padx=10, pady=(0, 8))
        
        self.widgets["auto_enhance"] = ctk.CTkCheckBox(frame, text="Auto-enhance images")
        self.widgets["auto_enhance"].pack(anchor="w", padx=10, pady=5)

    def _create_ai_settings(self):
        """Create AI settings section."""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        title = ctk.CTkLabel(frame, text="🤖 AI Settings", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(10, 5))
        
        # Confidence threshold
        ctk.CTkLabel(frame, text="Confidence Threshold").pack(anchor="w", padx=10)
        self.widgets["confidence_threshold"] = ctk.CTkSlider(frame, from_=0.0, to=1.0, number_of_steps=101)
        self.widgets["confidence_threshold"].pack(fill="x", padx=10, pady=(0, 10))
        
        # Checkboxes
        for key, text in [("show_confidence", "Show confidence scores"), 
                          ("auto_save_results", "Auto-save results"), 
                          ("grad_cam_enabled", "Enable Grad-CAM")]:
            checkbox = ctk.CTkCheckBox(frame, text=text)
            self.widgets[key] = checkbox
            checkbox.pack(anchor="w", padx=10, pady=2)
        
        # Prediction timeout
        ctk.CTkLabel(frame, text="Prediction Timeout (seconds)").pack(anchor="w", padx=10)
        self.widgets["prediction_timeout"] = ctk.CTkSlider(frame, from_=5, to=60, number_of_steps=55)
        self.widgets["prediction_timeout"].pack(fill="x", padx=10, pady=(0, 10))

    def _create_export_settings(self):
        """Create export settings section."""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        title = ctk.CTkLabel(frame, text="📁 Export Settings", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(10, 5))
        
        # Export directory
        dir_frame = ctk.CTkFrame(frame)
        dir_frame.pack(fill="x", padx=10, pady=5)
        self.widgets["export_dir"] = ctk.CTkEntry(dir_frame, placeholder_text="Export directory")
        self.widgets["export_dir"].pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(dir_frame, text="Browse", width=80, command=self._browse_export_dir).pack(side="right")
        
        # Format and Interval
        for key, label, vals in [("export_format", "Default Format:", ["PDF", "CSV", "JSON"]),
                                 ("export_interval", "Auto-export Interval:", ["Daily", "Weekly", "Monthly"])]:
            f = ctk.CTkFrame(frame)
            f.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(f, text=label).pack(side="left", padx=(0, 10))
            self.widgets[key] = ctk.CTkOptionMenu(f, values=vals)
            self.widgets[key].pack(side="left", fill="x", expand=True)
            
        # Checkboxes
        for key, text in [("include_images", "Include images in export"),
                          ("include_gradcam", "Include Grad-CAM images"),
                          ("auto_export", "Auto-export reports")]:
            cb = ctk.CTkCheckBox(frame, text=text)
            self.widgets[key] = cb
            cb.pack(anchor="w", padx=10, pady=2)

    def _create_ui_settings(self):
        """Create UI settings section."""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        title = ctk.CTkLabel(frame, text="🎛️ UI Settings", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(10, 5))
        
        for key, label, vals in [("theme", "Theme:", ["System", "Light", "Dark"]),
                                 ("language", "Language:", ["English", "Swahili", "French"])]:
            f = ctk.CTkFrame(frame)
            f.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(f, text=label).pack(side="left", padx=(0, 10))
            self.widgets[key] = ctk.CTkOptionMenu(f, values=vals)
            self.widgets[key].pack(side="left", fill="x", expand=True)

        for key, text in [("show_tooltips", "Show tooltips"), ("auto_backup", "Auto-backup settings")]:
            cb = ctk.CTkCheckBox(frame, text=text)
            self.widgets[key] = cb
            cb.pack(anchor="w", padx=10, pady=2)

    def _create_clinical_settings(self):
        """Create clinical settings section."""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(frame, text="🏥 Clinical Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        for key, text in [("patient_id_required", "Require Patient ID"),
                          ("auto_timestamp", "Auto-add timestamps"),
                          ("validate_patient_id", "Validate Patient ID format"),
                          ("enable_audit_log", "Enable audit logging")]:
            cb = ctk.CTkCheckBox(frame, text=text)
            self.widgets[key] = cb
            cb.pack(anchor="w", padx=10, pady=2)
            
        ctk.CTkLabel(frame, text="Default Confidence Threshold for Clinical Use").pack(anchor="w", padx=10)
        self.widgets["default_confidence_threshold"] = ctk.CTkSlider(frame, from_=0.0, to=1.0, number_of_steps=101)
        self.widgets["default_confidence_threshold"].pack(fill="x", padx=10, pady=(0, 10))

    def _create_advanced_settings(self):
        """Create advanced settings section."""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(frame, text="⚙️ Advanced Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        for key, text in [("model_cache_enabled", "Enable model caching"), ("debug_mode", "Debug mode (restart required)")]:
            cb = ctk.CTkCheckBox(frame, text=text)
            self.widgets[key] = cb
            cb.pack(anchor="w", padx=10, pady=2)
            
        f = ctk.CTkFrame(frame)
        f.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f, text="Log Level:").pack(side="left", padx=(0, 10))
        self.widgets["log_level"] = ctk.CTkOptionMenu(f, values=["DEBUG", "INFO", "WARNING", "ERROR"])
        self.widgets["log_level"].pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(frame, text="Max Recent Records to Display").pack(anchor="w", padx=10)
        self.widgets["max_recent_records"] = ctk.CTkSlider(frame, from_=10, to=500, number_of_steps=49)
        self.widgets["max_recent_records"].pack(fill="x", padx=10, pady=(0, 10))

    def _create_help_section(self):
        """Create help and documentation section."""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        title = ctk.CTkLabel(frame, text="📚 Help & Documentation", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(10, 5))
        
        # Documentation buttons
        docs_frame = ctk.CTkFrame(frame)
        docs_frame.pack(fill="x", padx=10, pady=5)
        
        # User Guide
        user_guide_btn = ctk.CTkButton(
            docs_frame, 
            text="📘 User Guide", 
            command=self._open_user_guide,
            fg_color="blue",
            hover_color="darkblue"
        )
        user_guide_btn.pack(fill="x", pady=2)
        
        # FAQ
        faq_btn = ctk.CTkButton(
            docs_frame, 
            text="❓ FAQ", 
            command=self._open_faq,
            fg_color="orange",
            hover_color="darkorange"
        )
        faq_btn.pack(fill="x", pady=2)
        
        # Privacy Policy
        privacy_btn = ctk.CTkButton(
            docs_frame, 
            text="🔒 Privacy Policy", 
            command=self._open_privacy_policy,
            fg_color="red",
            hover_color="darkred"
        )
        privacy_btn.pack(fill="x", pady=2)
        
        # Deployment Guide
        deploy_btn = ctk.CTkButton(
            docs_frame, 
            text="🚀 Deployment Guide", 
            command=self._open_deployment_guide,
            fg_color="green",
            hover_color="darkgreen"
        )
        deploy_btn.pack(fill="x", pady=2)
        
        # Test Report
        test_btn = ctk.CTkButton(
            docs_frame, 
            text="📊 Test Report", 
            command=self._open_test_report,
            fg_color="purple",
            hover_color="darkviolet"
        )
        test_btn.pack(fill="x", pady=2)
        
        # About
        about_btn = ctk.CTkButton(
            docs_frame, 
            text="ℹ️ About", 
            command=self._show_about,
            fg_color="gray",
            hover_color="darkgray"
        )
        about_btn.pack(fill="x", pady=(2, 10))

    def _create_buttons(self):
        """Create dialog buttons."""
        button_frame = ctk.CTkFrame(self) # Attached to main window, not scrollable frame
        button_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="Save Settings", command=self._save_settings, fg_color="green").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Reset to Defaults", command=self._reset_to_defaults).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Apply", command=self._apply_settings).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)

    def _load_settings_to_widgets(self):
        """Load current settings into widgets."""
        try:
            # Camera
            self.widgets["camera_index"].set(self.settings_manager.get("camera", "index"))
            self.widgets["fps"].set(self.settings_manager.get("camera", "fps"))
            self.widgets["auto_detect"].select() if self.settings_manager.get("camera", "auto_detect") else self.widgets["auto_detect"].deselect()
            
            res = self.settings_manager.get("camera", "resolution")
            self.widgets["resolution"].set(f"{res[0]}x{res[1]}")
            
            # Adjustments
            for adj in ["brightness", "contrast", "saturation", "sharpness", "gamma"]:
                self.widgets[adj].set(self.settings_manager.get("image_adjustments", adj))
            self.widgets["auto_enhance"].select() if self.settings_manager.get("image_adjustments", "auto_enhance") else self.widgets["auto_enhance"].deselect()
            
            # AI
            self.widgets["confidence_threshold"].set(self.settings_manager.get("ai_settings", "confidence_threshold"))
            self.widgets["prediction_timeout"].set(self.settings_manager.get("ai_settings", "prediction_timeout"))
            for cb in ["show_confidence", "auto_save_results", "grad_cam_enabled"]:
                self.widgets[cb].select() if self.settings_manager.get("ai_settings", cb) else self.widgets[cb].deselect()
                
            # Export
            self.widgets["export_dir"].delete(0, tk.END)
            self.widgets["export_dir"].insert(0, str(self.settings_manager.get_export_directory()))
            self.widgets["export_format"].set(self.settings_manager.get("export_settings", "default_format").upper())
            self.widgets["export_interval"].set(self.settings_manager.get("export_settings", "export_interval").title())
            for cb in ["include_images", "include_gradcam", "auto_export"]:
                self.widgets[cb].select() if self.settings_manager.get("export_settings", cb) else self.widgets[cb].deselect()

            # UI
            self.widgets["theme"].set(self.settings_manager.get("ui_settings", "theme"))
            self.widgets["language"].set(self.settings_manager.get("ui_settings", "language"))
            for cb in ["show_tooltips", "auto_backup"]:
                self.widgets[cb].select() if self.settings_manager.get("ui_settings", cb) else self.widgets[cb].deselect()

            # Clinical
            for cb in ["patient_id_required", "auto_timestamp", "validate_patient_id", "enable_audit_log"]:
                self.widgets[cb].select() if self.settings_manager.get("clinical_settings", cb) else self.widgets[cb].deselect()
            self.widgets["default_confidence_threshold"].set(self.settings_manager.get("clinical_settings", "default_confidence_threshold"))

            # Advanced
            for cb in ["model_cache_enabled", "debug_mode"]:
                self.widgets[cb].select() if self.settings_manager.get("advanced_settings", cb) else self.widgets[cb].deselect()
            self.widgets["log_level"].set(self.settings_manager.get("advanced_settings", "log_level"))
            self.widgets["max_recent_records"].set(self.settings_manager.get("advanced_settings", "max_recent_records"))
        except Exception as e:
            logger.error(f"Error loading settings: {e}")

    def _apply_settings(self) -> bool:
        """Collects data from all widgets and updates the SettingsManager."""
        try:
            # Camera Settings
            self.settings_manager.set("camera", "index", int(self.widgets["camera_index"].get()))
            self.settings_manager.set("camera", "fps", int(self.widgets["fps"].get()))
            self.settings_manager.set("camera", "auto_detect", bool(self.widgets["auto_detect"].get()))
            res_parts = self.widgets["resolution"].get().split("x")
            self.settings_manager.set("camera", "resolution", [int(res_parts[0]), int(res_parts[1])])
            
            # Image Adjustments
            for adj in ["brightness", "contrast", "saturation", "sharpness", "gamma"]:
                self.settings_manager.set("image_adjustments", adj, self.widgets[adj].get())
            self.settings_manager.set("image_adjustments", "auto_enhance", bool(self.widgets["auto_enhance"].get()))

            # AI Settings
            self.settings_manager.set("ai_settings", "confidence_threshold", float(self.widgets["confidence_threshold"].get()))
            self.settings_manager.set("ai_settings", "prediction_timeout", int(self.widgets["prediction_timeout"].get()))
            for cb in ["show_confidence", "auto_save_results", "grad_cam_enabled"]:
                self.settings_manager.set("ai_settings", cb, bool(self.widgets[cb].get()))

            # Export Settings
            self.settings_manager.set("export_settings", "directory", self.widgets["export_dir"].get())
            self.settings_manager.set("export_settings", "default_format", self.widgets["export_format"].get().lower())
            self.settings_manager.set("export_settings", "export_interval", self.widgets["export_interval"].get().lower())
            for cb in ["include_images", "include_gradcam", "auto_export"]:
                self.settings_manager.set("export_settings", cb, bool(self.widgets[cb].get()))

            # UI Settings
            self.settings_manager.set("ui_settings", "theme", self.widgets["theme"].get())
            self.settings_manager.set("ui_settings", "language", self.widgets["language"].get())
            for cb in ["show_tooltips", "auto_backup"]:
                self.settings_manager.set("ui_settings", cb, bool(self.widgets[cb].get()))

            # Clinical Settings
            for cb in ["patient_id_required", "auto_timestamp", "validate_patient_id", "enable_audit_log"]:
                self.settings_manager.set("clinical_settings", cb, bool(self.widgets[cb].get()))
            self.settings_manager.set("clinical_settings", "default_confidence_threshold", float(self.widgets["default_confidence_threshold"].get()))

            # Advanced Settings
            self.settings_manager.set("advanced_settings", "model_cache_enabled", bool(self.widgets["model_cache_enabled"].get()))
            self.settings_manager.set("advanced_settings", "debug_mode", bool(self.widgets["debug_mode"].get()))
            self.settings_manager.set("advanced_settings", "log_level", self.widgets["log_level"].get())
            self.settings_manager.set("advanced_settings", "max_recent_records", int(self.widgets["max_recent_records"].get()))
            
            if self.settings_manager.save():
                messagebox.showinfo("Settings", "Settings applied successfully!")
                return True
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Could not apply settings: {e}")
            return False

    def _save_settings(self):
        if self._apply_settings():
            if self.on_save_callback:
                self.on_save_callback()
            self.destroy()

    def _reset_to_defaults(self):
        if messagebox.askyesno("Reset", "Reset all settings to defaults?"):
            self.settings_manager.reset_to_defaults()
            self._load_settings_to_widgets()

    def _browse_export_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.widgets["export_dir"].delete(0, tk.END)
            self.widgets["export_dir"].insert(0, directory)

    def _center_and_grab(self):
        """Center dialog and grab input."""
        try:
            self._center_dialog()
            self.grab_set()
        except tk.TclError:
            # If grab fails, try again after delay
            self.after(100, self._center_and_grab)

    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        x = (self.parent.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.parent.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_camera_settings(self):
        """Create camera settings section."""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        title = ctk.CTkLabel(frame, text="📷 Camera Settings", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(10, 5))

        # Camera Index
        ctk.CTkLabel(frame, text="Camera Index").pack(anchor="w", padx=10)
        self.widgets["camera_index"] = ctk.CTkSlider(
            frame, from_=0, to=5, number_of_steps=5
        )
        self.widgets["camera_index"].pack(fill="x", padx=10, pady=(0, 10))
        
        # Resolution
        res_frame = ctk.CTkFrame(frame)
        res_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(res_frame, text="Resolution:").pack(side="left", padx=(0, 10))
        self.widgets["resolution"] = ctk.CTkOptionMenu(
            res_frame, values=["640x480", "1280x720", "1920x1080", "2560x1440"]
        )
        self.widgets["resolution"].pack(side="left", fill="x", expand=True)
        
        # FPS
        ctk.CTkLabel(frame, text="Frames Per Second").pack(anchor="w", padx=10)
        self.widgets["fps"] = ctk.CTkSlider(
            frame, from_=15, to=60, number_of_steps=45
        )
        self.widgets["fps"].pack(fill="x", padx=10, pady=(0, 10))
        
        # Auto detect
        self.widgets["auto_detect"] = ctk.CTkCheckBox(
            frame, text="Auto-detect cameras on startup"
        )
        self.widgets["auto_detect"].pack(anchor="w", padx=10, pady=5)

    def _open_user_guide(self):
        """Open user guide documentation."""
        try:
            docs = self.settings_manager.get_documentation_paths()
            user_guide_path = docs.get("user_guide")
            if user_guide_path and user_guide_path.exists():
                self._open_document(user_guide_path, "User Guide")
            else:
                messagebox.showinfo("Documentation", "User Guide not found. Please check installation.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open User Guide:\n{str(e)}")

    def _open_faq(self):
        """Open FAQ documentation."""
        try:
            docs = self.settings_manager.get_documentation_paths()
            faq_path = docs.get("faq")
            if faq_path and faq_path.exists():
                self._open_document(faq_path, "FAQ")
            else:
                messagebox.showinfo("Documentation", "FAQ not found. Please check installation.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open FAQ:\n{str(e)}")

    def _open_privacy_policy(self):
        """Open privacy policy documentation."""
        try:
            docs = self.settings_manager.get_documentation_paths()
            privacy_path = docs.get("privacy_policy")
            if privacy_path and privacy_path.exists():
                self._open_document(privacy_path, "Privacy Policy")
            else:
                messagebox.showinfo("Documentation", "Privacy Policy not found. Please check installation.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Privacy Policy:\n{str(e)}")

    def _open_deployment_guide(self):
        """Open deployment guide documentation."""
        try:
            docs = self.settings_manager.get_documentation_paths()
            deployment_path = docs.get("deployment_guide")
            if deployment_path and deployment_path.exists():
                self._open_document(deployment_path, "Deployment Guide")
            else:
                messagebox.showinfo("Documentation", "Deployment Guide not found. Please check installation.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Deployment Guide:\n{str(e)}")

    def _open_test_report(self):
        """Open test report documentation."""
        try:
            docs = self.settings_manager.get_documentation_paths()
            test_report_path = docs.get("test_report")
            if test_report_path and test_report_path.exists():
                self._open_document(test_report_path, "Test Report")
            else:
                messagebox.showinfo("Documentation", "Test Report not found. Please check installation.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Test Report:\n{str(e)}")

    def _open_document(self, file_path, title):
        """Open documentation file in system default viewer."""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Linux":
                subprocess.run(["xdg-open", str(file_path)])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(file_path)])
            elif system == "Windows":
                subprocess.run(["start", str(file_path)], shell=True)
            else:
                # Fallback: try to open with default text editor
                subprocess.run(["less", str(file_path)])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open {title}:\n{str(e)}")

    def _show_about(self):
        """Show about dialog."""
        about_text = """AI Microscope Settings v1.0.0
        
An advanced diagnostic tool for bacterial identification 
using artificial intelligence and computer vision.

Developed for Mbeya Regional Referral Hospital
© 2026 DMB MUST

Settings Features:
• Camera configuration
• Image adjustments
• AI model settings
• Export options
• Clinical preferences
• Advanced options
• Help & Documentation

For support, contact IT Department."""
        
        messagebox.showinfo("About AI Microscope", about_text)
