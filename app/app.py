#!/usr/bin/env python3
"""
Refactored AI Microscope Application
Uses layered architecture with controllers and views
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import warnings
warnings.filterwarnings('ignore')

# Setup paths
basedir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(basedir))
sys.path.insert(0, str(basedir / "app"))
sys.path.insert(0, str(basedir / "inference"))
sys.path.insert(0, str(basedir / "model"))

import threading
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog, messagebox
import cv2
import time
from config.settings import SettingsManager
import datetime
import json

# Import from new architecture
from utils.logger import log_info, log_error, log_warning
from config.settings import get_settings_manager
from config.constants import CLINICAL_CONFIDENCE_THRESHOLD, EXPORT_DIR

# Import TensorFlow and inference
import tensorflow as tf
import inference as inference_module

# Import model components
from model.db import get_db
from model.model_config import MODEL_INPUT_SIZE
from model import report as report_utils

# Import new GUI components
from gui.views.control_wing import ControlWing
from gui.views.primary_viewport import PrimaryViewport
from gui.views.intelligence_wing import IntelligenceWing

# Import new controllers
from gui.controllers.camera_controller import CameraController
from gui.controllers.diagnosis_controller import DiagnosisController
from gui.controllers.export_controller import ExportController

# Import existing services for compatibility
from app.services import InferenceService, RecordService

# Import settings dialog
from app.settings_dialog import SettingsDialog

# Import authentication
from core.auth import AuthenticationService
from gui.components.login_dialog import LoginDialog
from gui.components.clinical_status_bar import ClinicalStatusBar
from gui.components.patient_safety_dialog import PatientSafetyDialog
from gui.components.medical_help_system import MedicalHelpSystem

# Import health check
from core.health_check import HealthCheckService

# Import session manager
from core.session_manager import SessionManager

# Import backup service
from core.backup_service import BackupService

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class MainApp(ctk.CTk):
    """Refactored main application using layered architecture."""
    
    def __init__(self):
        """Initialize the refactored main application."""
        super().__init__()
        
        # Suppress TensorFlow warnings
        import os
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        tf.get_logger().setLevel('ERROR')
        
        # Suppress OpenCV warnings
        import cv2
        cv2.setLogLevel(0)
        
        # Suppress OpenCV INFO/WARN logs
        os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
        
        self.title("DMB AI Microscope - Mbeya University Of Science And Technology (MUST)")
        
        # Set window icon
        try:
            icon_path = Path(__file__).resolve().parent.parent / "logo.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass  # Icon is optional
        
        # Match the windows display size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.minsize(1024, 600)
        self.resizable(True, True)
        
        # Maximize the window on Windows so it fits the display fully
        try:
            self.state('zoomed')
        except Exception:
            # Fallback for non-Windows platforms
            try:
                self.attributes('-zoomed', True)
            except Exception:
                pass
        
        # Configure grid: side panels fixed width, only center viewport expands.
        # This keeps buttons in the side wings in fixed positions during resize.
        SIDE_WING_WIDTH = 280
        self.grid_columnconfigure(0, weight=0, minsize=SIDE_WING_WIDTH)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=SIDE_WING_WIDTH)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # Status bar row - fixed height
        self._side_wing_width = SIDE_WING_WIDTH
        
        # Initialize settings first (needed by controllers)
        self.settings_manager = SettingsManager()
        
        # Initialize controllers
        self.camera_controller = CameraController()
        self.diagnosis_controller = DiagnosisController()
        self.export_controller = ExportController(settings_manager=self.settings_manager)
        
        # Initialize services for compatibility
        self.inference_service = InferenceService(model=None)
        self.record_service = RecordService()
        
        # Initialize authentication
        self.auth_service = AuthenticationService()
        
        # Initialize session manager
        self.session_manager = SessionManager()
        recovered_session = self.session_manager.load_session()
        if recovered_session:
            log_info("Session recovered from previous run")
        
        # Initialize backup service
        self.backup_service = BackupService()
        self._create_backup()
        
        # Run health check
        self._run_health_check()
        
        # State variables
        self.captured_image_path = None
        self.current_frame = None
        self.tkimg = None
        self.heatmap_img = None
        self.model = None
        
        # Image adjustment state
        self.current_adjustments = {
            "brightness": 1.0,
            "contrast": 1.0
        }
        self.original_image = None  # Store original image for adjustments
        
        # Load model
        self._load_model()
        
        # Create views
        self._create_views()
        
        # Wire up callbacks
        self._wire_callbacks()
        
        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Load initial settings
        self._load_initial_settings()
        
        # Show login dialog
        self._show_login_dialog()
        
        # Populate cameras
        self.after(100, self._populate_cameras)
    
    def _load_model(self) -> None:
        """Load the AI model and perform warm-up inference."""
        log_info("Loading AI model...")
        print("Loading AI model...")
        try:
            self.model = inference_module.load_model()
            self.inference_service.model = self.model
            print("Model loaded successfully!")
            print(f"Model: {self.model.name}")
            print(f"Parameters: {self.model.count_params():,}")
            print(f"Input shape: {self.model.input_shape}")
            print(f"Output shape: {self.model.output_shape}")
            log_info(f"Model loaded successfully: {self.model.name}")
            
            # Warm-up inference to reduce first-inference latency
            self._warmup_model()
        except Exception as e:
            log_error(f"Failed to load model: {str(e)}", exc_info=True)
            messagebox.showerror("Model Error", f"Failed to load AI model:\n{str(e)}\n\nApplication cannot continue.")
            raise
    
    def _warmup_model(self) -> None:
        """Perform warm-up inference to initialize GPU and reduce latency."""
        log_info("Performing model warm-up...")
        try:
            import numpy as np
            input_shape = self.model.input_shape[1:3]  # Get height, width
            dummy_input = np.random.rand(1, *input_shape, 3).astype(np.float32)
            
            # Run a few warm-up inferences
            for i in range(3):
                _ = self.model.predict(dummy_input, verbose=0)
            
            log_info("Model warm-up complete")
        except Exception as e:
            log_warning(f"Model warm-up failed (non-critical): {str(e)}")
    
    def _run_health_check(self) -> None:
        """Run health check on startup."""
        log_info("Running system health check...")
        try:
            health_service = HealthCheckService()
            results = health_service.check_all()
            health_service.print_report()
            
            if results["status"] == "unhealthy":
                log_warning("System health check detected issues. Application may have limited functionality.")
        except Exception as e:
            log_warning(f"Health check failed (non-critical): {str(e)}")
    
    def _create_backup(self) -> None:
        """Create automatic database backup on startup."""
        try:
            backup_path = self.backup_service.create_backup(compress=True)
            if backup_path:
                log_info(f"Database backup created: {backup_path.name}")
        except Exception as e:
            log_warning(f"Automatic backup failed (non-critical): {str(e)}")
    
    def _create_views(self) -> None:
        """Create the three main view panels."""
        # Control Wing (left) - fixed width so buttons don't shift on resize
        self.control_wing = ControlWing(
            self,
            on_upload=self.upload_media,
            on_settings=self.open_settings,
            on_export=self.export_reports,
            on_camera_select=self._on_camera_select,
            on_camera_start=self.start_camera,
            on_camera_stop=self.stop_camera,
            on_image_adjustment_change=self._on_image_adjustment_change,
            width=self._side_wing_width
        )
        self.control_wing.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.control_wing.grid_propagate(False)
        self.control_wing.pack_propagate(False)
        
        # Primary Viewport (center) - expands with window
        self.primary_viewport = PrimaryViewport(
            self,
            on_capture=self.capture_image
        )
        self.primary_viewport.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Intelligence Wing (right) - fixed width so buttons don't shift on resize
        self.intelligence_wing = IntelligenceWing(
            self,
            on_diagnose=self.run_diagnosis,
            width=self._side_wing_width
        )
        self.intelligence_wing.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self.intelligence_wing.grid_propagate(False)
        self.intelligence_wing.pack_propagate(False)
        
        # Clinical Status Bar at bottom
        self.status_bar = ClinicalStatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=(0, 5))
    
    def _wire_callbacks(self) -> None:
        """Wire up callbacks between controllers and views."""
        # Camera controller callbacks
        self.camera_controller.set_camera_changed_callback(self._on_camera_state_changed)
        
        # Diagnosis controller callbacks
        self.diagnosis_controller.set_diagnosis_complete_callback(self._on_diagnosis_complete)
        self.diagnosis_controller.set_diagnosis_error_callback(self._on_diagnosis_error)
        
        # Export controller callbacks
        self.export_controller.set_export_complete_callback(self._on_export_complete)
        self.export_controller.set_export_error_callback(self._on_export_error)
    
    def _load_initial_settings(self) -> None:
        """Load initial settings values."""
        try:
            # Load image adjustments
            adj = self.settings_manager.get("image_adjustments")
            # Convert from slider range (-100 to 100) to enhancement factor (0.0 to 2.0)
            brightness_factor = 1.0 + (adj.get("brightness", 0) / 100.0)
            contrast_factor = 1.0 + (adj.get("contrast", 0) / 100.0)
            self.control_wing.set_image_adjustments(
                brightness_factor,
                contrast_factor
            )
            # Also store the raw values for saving
            self.current_adjustments = {
                "brightness": brightness_factor,
                "contrast": contrast_factor
            }
            log_info(f"Initial settings loaded: brightness={brightness_factor:.2f}, contrast={contrast_factor:.2f}")
        except Exception as e:
            log_warning(f"Failed to load initial settings: {str(e)}")
    
    def _populate_cameras(self) -> None:
        """Detect and populate available cameras."""
        cams = self.camera_controller.detect_cameras()
        self.control_wing.update_cameras(cams)
        
        if self.settings_manager.get("camera", "auto_detect"):
            best_index = self.camera_controller.get_best_camera_index()
            if best_index >= 0:
                for cam in cams:
                    if f"Camera {best_index}" in cam:
                        self.control_wing.set_selected_camera(cam)
                        break
    
    def _show_login_dialog(self) -> None:
        """Show login dialog for user authentication."""
        def on_login_success(user) -> None:
            log_info(f"User logged in: {user.username} ({user.role.value})")
        
        login_dialog = LoginDialog(self, self.auth_service, on_login_success)
        self.wait_window(login_dialog)
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for medical workflow."""
        # Medical workflow shortcuts
        # Ctrl+P - Focus Patient ID field
        self.bind("<Control-p>", lambda e: self._focus_patient_id())
        self.bind("<Control-P>", lambda e: self._focus_patient_id())
        
        # Ctrl+D - Run diagnosis
        self.bind("<Control-d>", lambda e: self.run_diagnosis())
        self.bind("<Control-D>", lambda e: self.run_diagnosis())
        
        # Alt+C - Capture image (alternative to Ctrl+C for compatibility)
        self.bind("<Alt-c>", lambda e: self.capture_image())
        self.bind("<Alt-C>", lambda e: self.capture_image())
        
        # Ctrl+C - Capture image (primary)
        self.bind("<Control-c>", lambda e: self.capture_image())
        self.bind("<Control-C>", lambda e: self.capture_image())
        
        # Ctrl+U - Upload image
        self.bind("<Control-u>", lambda e: self.upload_media())
        self.bind("<Control-U>", lambda e: self.upload_media())
        
        # Ctrl+S - Save record
        self.bind("<Control-s>", lambda e: self._save_diagnosis_to_db(None))
        self.bind("<Control-S>", lambda e: self._save_diagnosis_to_db(None))
        
        # Ctrl+Shift+S - Open settings
        self.bind("<Control-Shift-S>", lambda e: self.open_settings())
        
        # Ctrl+E - Export reports
        self.bind("<Control-e>", lambda e: self.export_reports())
        self.bind("<Control-E>", lambda e: self.export_reports())
        
        # F1 - Contextual help
        self.bind("<F1>", lambda e: self._show_contextual_help())
        
        # Escape - Cancel/close dialogs
        self.bind("<Escape>", lambda e: self._handle_escape())
        
        # Space - Start/Stop camera
        self.bind("<space>", lambda e: self._toggle_camera())
        
        # Ctrl+T - Toggle dark/light mode
        self.bind("<Control-t>", lambda e: self._toggle_theme())
        self.bind("<Control-T>", lambda e: self._toggle_theme())
        
        # Ctrl+Q - Quit application
        self.bind("<Control-q>", lambda e: self._confirm_quit())
        self.bind("<Control-Q>", lambda e: self._confirm_quit())
        
        log_info("Keyboard shortcuts configured for medical workflow")
        
        # Initialize patient tracking
        self._current_patient_id = None
        self._track_patient_changes()
    
    def _focus_patient_id(self) -> None:
        """Focus the patient ID entry field."""
        self.control_wing.patient_input.entry.focus_set()
        self.control_wing.patient_input.entry.select_range(0, "end")
    
    def _show_contextual_help(self) -> None:
        """Show help based on current context."""
        self.open_help()
    
    def _handle_escape(self) -> None:
        """Handle escape key - cancel current operation."""
        if self.camera_controller.is_running():
            self.stop_camera()
        elif self.diagnosis_controller.is_running:
            # Can't cancel diagnosis mid-run, just log attempt
            log_info("Escape pressed during diagnosis - operation cannot be cancelled")
    
    def _confirm_quit(self) -> None:
        """Confirm quit with unsaved data check."""
        if self.status_bar.has_unsaved_data():
            from gui.components.patient_safety_dialog import UnsavedDataDialog
            dialog = UnsavedDataDialog(
                self,
                self.status_bar.get_current_patient() or "Unknown",
                on_save=lambda: self._save_and_quit(),
                on_discard=lambda: self.quit(),
                on_cancel=lambda: None
            )
            self.wait_window(dialog)
        else:
            self.quit()
    
    def _save_and_quit(self) -> None:
        """Save data and quit application."""
        self._save_diagnosis_to_db(None)
        self.quit()
    
    def _track_patient_changes(self) -> None:
        """Track patient ID changes for safety warnings."""
        def check_patient_change():
            current_id = self.control_wing.get_patient_id()
            is_anon = self.control_wing.patient_input.is_anonymous()
            
            # Update status bar with current patient
            self.status_bar.set_patient(current_id, is_anon)
            
            # Check for patient change with unsaved data
            if (self._current_patient_id is not None and 
                current_id != self._current_patient_id and
                self.status_bar.has_unsaved_data()):
                
                # Show warning dialog
                dialog = PatientSafetyDialog(
                    self,
                    old_patient_id=self._current_patient_id,
                    new_patient_id=current_id,
                    has_unsaved_data=True,
                    on_save_first=lambda: self._save_diagnosis_to_db(self.diagnosis_controller.get_current_diagnosis()),
                    on_continue=lambda: None,
                    on_cancel=lambda: self.control_wing.set_patient_id(self._current_patient_id)
                )
                self.wait_window(dialog)
            
            # Update tracked patient ID
            if current_id:
                self._current_patient_id = current_id
            
            # Schedule next check
            self.after(500, check_patient_change)
        
        # Start tracking
        check_patient_change()
    
    def _toggle_camera(self) -> None:
        """Toggle camera on/off."""
        if self.camera_controller.is_running():
            self.stop_camera()
        else:
            selected_camera = self.control_wing.get_selected_camera()
            if selected_camera:
                try:
                    camera_index = int(selected_camera.split()[1])
                    self.start_camera(camera_index)
                except (ValueError, IndexError):
                    log_warning("Could not determine camera index from selection")
    
    def _toggle_theme(self) -> None:
        """Toggle between dark and light mode."""
        import customtkinter as ctk
        current_mode = ctk.get_appearance_mode()
        new_mode = "Dark" if current_mode == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        log_info(f"Theme switched to {new_mode} mode")
    
    def _on_camera_state_changed(self, is_running: bool) -> None:
        """Handle camera state change."""
        self.control_wing.set_camera_running_state(is_running)
        if is_running:
            self.status_bar.set_session_status("● Live View Active", "#00AAFF")
        else:
            self.status_bar.show_ready()
    
    def _on_camera_select(self, value: str) -> None:
        """Handle camera selection."""
        pass  # Camera selection handled in start_camera
    
    def _on_image_adjustment_change(self, adjustments: Dict[str, float]) -> None:
        """Handle image adjustment changes.
        
        Args:
            adjustments: Dictionary with brightness and contrast values (enhancement factors)
        """
        self.current_adjustments = adjustments
        # Save adjustments to settings (convert from enhancement factor to slider range)
        try:
            # Convert from enhancement factor (0.0 to 2.0) to slider range (-100 to 100)
            brightness_slider = (adjustments.get("brightness", 1.0) - 1.0) * 100
            contrast_slider = (adjustments.get("contrast", 1.0) - 1.0) * 100
            
            slider_adjustments = {
                "brightness": brightness_slider,
                "contrast": contrast_slider,
                "saturation": self.settings_manager.get("image_adjustments", "saturation", 0),
                "sharpness": self.settings_manager.get("image_adjustments", "sharpness", 0),
                "gamma": self.settings_manager.get("image_adjustments", "gamma", 1.0),
                "auto_enhance": self.settings_manager.get("image_adjustments", "auto_enhance", False)
            }
            
            self.settings_manager.update_section("image_adjustments", slider_adjustments)
            self.settings_manager.save()
            log_info(f"Image adjustments saved: {slider_adjustments}")
        except Exception as e:
            log_error(f"Failed to save image adjustments: {str(e)}", exc_info=True)
        # Apply adjustments to current image if loaded
        if self.original_image is not None:
            self._apply_adjustments_to_image()
    
    def _apply_adjustments_to_image(self) -> None:
        """Apply current adjustments to the displayed image."""
        if self.original_image is None:
            return
        
        try:
            from PIL import Image, ImageEnhance
            
            img = self.original_image.copy()
            
            # Apply brightness
            brightness = self.current_adjustments.get("brightness", 1.0)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)
            
            # Apply contrast
            contrast = self.current_adjustments.get("contrast", 1.0)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
            
            # Update display
            self.primary_viewport.display_image(img)
            # Only log when adjustments are not at default values
            if brightness != 1.0 or contrast != 1.0:
                log_info(f"Applied adjustments: brightness={brightness:.2f}, contrast={contrast:.2f}")
        except Exception as e:
            log_error(f"Failed to apply adjustments: {str(e)}", exc_info=True)
    
    def _on_diagnosis_complete(self, diagnosis: Any) -> None:
        """Handle diagnosis completion.
        
        Args:
            diagnosis: Diagnosis result object
        """
        # Update status bar
        self.status_bar.show_diagnosis_complete()
        
        # Update results on main thread
        self.after(0, lambda: self._update_diagnosis_results(diagnosis))
    
    def _update_diagnosis_results(self, diagnosis: Any) -> None:
        """Update diagnosis results in UI.
        
        Args:
            diagnosis: Diagnosis result object
        """
        # Display species and confidence
        self.intelligence_wing.update_results(diagnosis.species, diagnosis.confidence)
        log_info(f"Results displayed: {diagnosis.species} ({diagnosis.confidence:.2%})")

        if self.captured_image_path and diagnosis.class_index >= 0:
            try:
                # 1. Get the actual IMAGE object from the controller, not a path
                # Ensure your controller's generate_gradcam returns the PIL image
                gradcam_img = self.diagnosis_controller.generate_gradcam(self.captured_image_path)
                
                if gradcam_img:
                    # 2. It is already a PIL image from inference.py, 
                    # so we just need to resize it for the UI
                    gradcam_img = gradcam_img.convert('RGB')
                    gradcam_img = gradcam_img.resize((256, 256))
                    
                    # 3. Display it directly
                    self.intelligence_wing.display_gradcam(gradcam_img)
                    log_info("Grad-CAM image object displayed successfully")
                else:
                    log_warning("Grad-CAM generation returned None")
                    
            except Exception as e:
                log_error(f"Failed to display Grad-CAM: {str(e)}", exc_info=True)
                
        # Save to database
        self._save_diagnosis_to_db(diagnosis)
    
    def _on_diagnosis_error(self, error: str) -> None:
        """Handle diagnosis error with detailed troubleshooting.
        
        Args:
            error: Error message with troubleshooting steps
        """
        # Update status bar
        self.status_bar.show_error("Analysis Failed")
        
        # Show detailed error with troubleshooting
        self.after(0, lambda: messagebox.showerror(
            "Analysis Error", 
            error,
            icon='warning'
        ))
        self.intelligence_wing.clear_results()
        self.status_bar.show_ready()
    
    def _on_export_complete(self, path: str, format: str) -> None:
        """Handle export completion.
        
        Args:
            path: Export file path
            format: Export format
        """
        self.after(0, lambda: messagebox.showinfo("Export Successful", f"{format} export completed:\n{path}"))
    
    def _on_export_error(self, error: str) -> None:
        """Handle export error.
        
        Args:
            error: Error message
        """
        self.after(0, lambda: messagebox.showerror("Export Error", f"Export failed:\n{error}"))
    
    def _save_diagnosis_to_db(self, diagnosis: Any) -> None:
        """Save diagnosis to database with status bar update.
        
        Args:
            diagnosis: Diagnosis result object
        """
        try:
            patient_id = self.control_wing.get_patient_id()
            is_anonymous = self.control_wing.patient_input.is_anonymous()
            
            if not patient_id and not is_anonymous:
                if self.settings_manager.get("clinical", "patient_id_required"):
                    messagebox.showwarning("Patient ID Required", "Please enter a Patient ID before saving, or enable Research Mode for de-identified samples.")
                    return
            
            self.record_service.save_record(
                patient_id=patient_id or "N/A",
                result={
                    "species": diagnosis.species,
                    "confidence": diagnosis.confidence,
                    "class_index": diagnosis.class_index,
                    "status": diagnosis.status.value
                },
                source_image_path=self.captured_image_path
            )
            
            # Update status bar
            self.status_bar.mark_saved()
            log_info("Record saved successfully")
            messagebox.showinfo("Save Successful", f"Diagnosis saved for patient {patient_id}")
            
        except Exception as e:
            log_error(f"Failed to save record: {str(e)}", exc_info=True)
            messagebox.showerror("Save Error", f"Failed to save diagnosis:\n{str(e)}")
    
    # Camera methods
    def start_camera(self) -> None:
        """Start the selected camera."""
        selected = self.control_wing.get_selected_camera()
        try:
            cam_index = int(''.join(filter(str.isdigit, selected.split()[0])))
        except Exception:
            cam_index = 1
        
        if self.camera_controller.start_camera(cam_index):
            self._update_camera_frame()
        else:
            messagebox.showerror("Camera Error", f"Unable to open camera {cam_index}")
    
    def stop_camera(self) -> None:
        """Stop the camera."""
        self.camera_controller.stop_camera()
    
    def _update_camera_frame(self) -> None:
        """Update camera frame display."""
        if not self.camera_controller.is_running():
            return
        
        frame = self.camera_controller.read_frame()
        if frame is None:
            self.after(100, self._update_camera_frame)
            return
        
        pil_image = self.camera_controller.frame_to_pil(frame)
        if pil_image:
            # Store original frame for adjustments
            self.original_image = pil_image.copy()
            # Apply current adjustments
            self._apply_adjustments_to_image()
        
        self.after(30, self._update_camera_frame)
    
    # Capture method
    def capture_image(self) -> None:
        """Capture an image from camera or file."""
        if self.camera_controller.is_running() and self.camera_controller.get_current_frame() is not None:
            # Capture from camera
            save_dir = EXPORT_DIR
            self.captured_image_path = self.camera_controller.capture_frame_to_file(str(save_dir))
            
            if self.captured_image_path:
                pil_image = self.camera_controller.frame_to_pil(self.camera_controller.get_current_frame())
                if pil_image:
                    # Store original for adjustments
                    self.original_image = pil_image.copy()
                    # Apply current adjustments
                    self._apply_adjustments_to_image()
                log_info(f"Image captured: {self.captured_image_path}")
        else:
            messagebox.showwarning("No Camera", "Please start the camera first.")
    
    # Upload method
    def upload_media(self) -> None:
        """Upload media file."""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp"),
                ("Videos", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Handle video or image
        if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm')):
            self._extract_video_frame(file_path)
        else:
            self._load_image(file_path)
    
    def _load_image(self, file_path: str) -> None:
        """Load and display an image.
        
        Args:
            file_path: Path to image file
        """
        try:
            img = Image.open(file_path)
            img = img.convert('RGB')
            
            # Store original image for adjustments
            self.original_image = img.copy()
            self.captured_image_path = file_path
            
            # Apply current adjustments
            self._apply_adjustments_to_image()
            
            log_info(f"Image loaded: {file_path}")
        except Exception as e:
            log_error(f"Failed to load image: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")
    
    def _extract_video_frame(self, video_path: str) -> None:
        """Extract first frame from video.
        
        Args:
            video_path: Path to video file
        """
        try:
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                pil_image = self.camera_controller.frame_to_pil(frame)
                if pil_image:
                    self.primary_viewport.display_image(pil_image)
                    self.captured_image_path = video_path
                    log_info(f"Video frame extracted: {video_path}")
            else:
                messagebox.showerror("Video Error", "Could not read video file")
        except Exception as e:
            messagebox.showerror("Video Error", f"Failed to extract frame:\n{str(e)}")
    
    # Diagnosis method
    def run_diagnosis(self) -> None:
        """Run AI diagnosis on captured image."""
        if not self.captured_image_path:
            messagebox.showwarning("No Image", "Please capture or upload an image first.")
            return
        
        # Save adjusted image before diagnosis if adjustments are active
        if self.original_image is not None:
            try:
                from PIL import Image, ImageEnhance
                
                # Create adjusted image
                adjusted_img = self.original_image.copy()
                brightness = self.current_adjustments.get("brightness", 1.0)
                contrast = self.current_adjustments.get("contrast", 1.0)
                
                if brightness != 1.0:
                    enhancer = ImageEnhance.Brightness(adjusted_img)
                    adjusted_img = enhancer.enhance(brightness)
                
                if contrast != 1.0:
                    enhancer = ImageEnhance.Contrast(adjusted_img)
                    adjusted_img = enhancer.enhance(contrast)
                
                # Save adjusted image for diagnosis
                from pathlib import Path
                adjusted_path = str(Path(self.captured_image_path).parent / f"adjusted_{Path(self.captured_image_path).name}")
                adjusted_img.save(adjusted_path)
                
                # Use adjusted image for diagnosis
                diagnosis_image_path = adjusted_path
                log_info(f"Using adjusted image for diagnosis: {adjusted_path}")
            except Exception as e:
                log_error(f"Failed to save adjusted image: {str(e)}", exc_info=True)
                diagnosis_image_path = self.captured_image_path
        else:
            diagnosis_image_path = self.captured_image_path
        
        patient_id = self.control_wing.get_patient_id()
        self.intelligence_wing.set_results_loading()
        
        self.diagnosis_controller.run_diagnosis(
            diagnosis_image_path,
            patient_id
        )
    
    def open_user_guide(self):
        """Show user guide documentation in app."""
        user_guide_text = """AI MICROSCOPE USER GUIDE
========================

GETTING STARTED
--------------
1. Launch the application
2. Allow camera permissions when prompted
3. Select camera source from dropdown
4. Click "Start Camera" to begin

CAPTURING IMAGES
----------------
1. Position bacterial colony under microscope
2. Adjust focus for clarity
3. Click "Capture" to take image
4. Click "Run AI Diagnosis" for analysis

AI DIAGNOSIS
------------
• Confidence scores shown (90%+ threshold)
• Grad-CAM heatmaps highlight identification areas
• Results automatically saved to clinical records
• Low confidence predictions require manual review

CLINICAL WORKFLOW
----------------
1. Enter Patient ID (required)
2. Capture specimen image
3. Run AI diagnosis
4. Review confidence score
5. Add clinical notes if needed
6. Export reports (PDF/CSV)

TROUBLESHOOTING
---------------
• Camera not detected: Check connections and restart app
• Low confidence: Ensure proper lighting and focus
• Export errors: Verify directory permissions
• Model loading: Ensure model files are present

For detailed help, contact IT Department."""
        
        messagebox.showinfo("User Guide", user_guide_text)

    def open_faq(self):
        """Show FAQ documentation in app."""
        faq_text = """AI MICROSCOPE FREQUENTLY ASKED QUESTIONS
============================================

Q: What bacterial species can the AI identify?
A: The system can identify 33 common bacterial species including:
   • E. coli, S. aureus, K. pneumoniae
   • P. aeruginosa, Enterococcus species
   • Lactobacillus species, and many more

Q: How accurate is the AI diagnosis?
A: The model achieves 95%+ accuracy on validated samples.
   Results below 90% confidence require manual review.

Q: What camera do I need?
A: Any USB camera or microscope camera works.
   Recommended: 1080p resolution for best results.

Q: Why is the confidence score low?
A: Common causes:
   • Poor lighting conditions
   • Out of focus images
   • Insufficient bacterial colony growth
   • Contaminated samples

Q: Can I use existing microscope images?
A: Yes! Click "Upload Image" to analyze saved images.
   Format: PNG, JPG, or TIFF files.

Q: How do I export patient reports?
A: Click "Export Reports" to generate:
   • PDF reports with images and Grad-CAM
   • CSV files for data analysis
   • Both formats include timestamps and patient IDs

Q: Is patient data secure?
A: Yes. All data is stored locally on your computer.
   No data is transmitted to external servers.

Q: What if the AI makes a wrong prediction?
A: Always verify AI results with laboratory testing.
   The AI is a diagnostic aid, not a replacement for lab analysis.

Q: System requirements?
A: • Windows 10/11 or Linux
   • 16GB+ RAM recommended
   • 2GB+ free disk space
   • USB camera or microscope camera

Q: How to improve accuracy?
A: • Ensure proper lighting
   • Use clean microscope slides
   • Allow colonies to grow sufficiently
   • Keep camera lens clean

For technical support, contact IT Department."""

        messagebox.showinfo("FAQ", faq_text)

    def open_privacy_policy(self):
        """Show privacy policy documentation in app."""
        privacy_text = """AI MICROSCOPE PRIVACY POLICY
================================

DATA COLLECTION AND USE
-----------------------
• Patient data is stored locally on your computer
• No data is transmitted to external servers
• Images and results are saved only with explicit consent
• Data is used solely for diagnostic purposes

PATIENT PRIVACY
---------------
• Patient IDs are required for record keeping
• All patient data is encrypted at rest
• Access to clinical records requires proper authorization
• Data retention follows hospital policies

DATA SECURITY
-------------
• Local SQLite database with encryption
• Regular backup recommendations provided
• Audit logs track all data access
• No internet connectivity required for operation

IMAGE HANDLING
---------------
• Microscope images are stored locally
• Grad-CAM heatmaps are generated on-device
• Images may be included in exported reports
• Raw images are retained for quality control

THIRD-PARTY SERVICES
---------------------
• No third-party analytics or tracking
• No cloud storage integration
• No data sharing with external parties
• Offline operation fully supported

USER RIGHTS
-----------
• Access to your data at any time
• Export capabilities for data portability
• Right to delete patient records
• Request data modification or correction

COMPLIANCE
----------
• HIPAA compliant data handling
• Clinical data protection standards
• Hospital information security policies
• Medical device data regulations

CONTACT
-------
For privacy concerns or data requests:
• Contact: Hospital IT Department
• Phone: [Hospital IT Extension]
• Email: [Hospital IT Email]

Last updated: April 2026"""

        messagebox.showinfo("Privacy Policy", privacy_text)

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

    def open_help(self, initial_doc: str = "getting_started.md"):
        """Open the medical help system.

        Args:
            initial_doc: Initial document to display (filename)
        """
        try:
            MedicalHelpSystem(self, initial_doc)
        except Exception as e:
            messagebox.showerror("Help Error", f"Could not open help:\n{str(e)}")

    def open_camera_help(self):
        """Open help specifically for camera operations."""
        self.open_help("getting_started.md")

    def open_diagnosis_help(self):
        """Open help specifically for AI diagnosis."""
        self.open_help("user_guide.md")

    def open_troubleshooting(self):
        """Open troubleshooting help."""
        self.open_help("troubleshooting.md")

    def open_clinical_practices(self):
        """Open clinical best practices guide."""
        self.open_help("clinical_best_practices.md")

    def show_about(self):
        """Show about dialog."""
        about_text = """DMB AI Microscope v1.0.0
        
An advanced diagnostic tool for bacterial identification 
using artificial intelligence and computer vision.

Developed for Mbeya Regional Referral Hospital
© 2026 DMB MUST

Features:
• 33 bacterial species identification
• Grad-CAM explainable AI
• Clinical record management
• PDF/CSV export capabilities
• Real-time camera integration
• 90% confidence threshold for clinical use
• Local data storage (no cloud dependency)
• Built-in help and documentation

For support, contact the IT Department."""
        
        messagebox.showinfo("About DMB AI Microscope", about_text)

    def open_settings(self) -> None:
        """Open settings dialog."""
        settings_dialog = SettingsDialog(self, self.settings_manager, on_save_callback=self._on_settings_saved)
        settings_dialog.grab_set()

    def _on_settings_saved(self):
        """Callback when settings are saved."""
        # Apply theme changes
        theme = self.settings_manager.get("ui_settings", "theme")
        if theme == "Light":
            ctk.set_appearance_mode("light")
        elif theme == "Dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("system")
        
        # Update camera settings if needed
        if self.camera_controller.is_running():
            self.stop_camera()
            self.start_camera()
    
    def export_reports(self) -> None:
        """Export clinical reports with user dialog for format, filename and location."""
        self.export_controller.export_all_records(parent_window=self)
    
    def _initialize_database(self) -> None:
        """Initialize the database connection."""
        try:
            self.db = get_db()
            log_info("Database initialized at G:\\AI_MICROSCOPE-main\\clinical_records.db")
        except Exception as e:
            log_error(f"Failed to initialize database: {str(e)}", exc_info=True)
            messagebox.showerror("Database Error", f"Failed to initialize database:\n{str(e)}")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
