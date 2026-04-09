import os
import sys
from pathlib import Path

# Hack to force Briefcase Windows to find our smuggled Tkinter files
if sys.platform == 'win32':
    app_dir = Path(__file__).parent.parent.parent
    os.environ['TCL_LIBRARY'] = str(app_dir / 'tcl' / 'tcl8.6')
    os.environ['TK_LIBRARY'] = str(app_dir / 'tcl' / 'tk8.6')

# --- BRIEFCASE COMPATIBLE PATH LOGIC ---
if getattr(sys, 'frozen', False):
    # Running as a bundled App
    basedir = Path(sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable))
else:
    # Running in 'briefcase dev'
    basedir = Path(__file__).resolve().parent

# Make sure Python can see the 'inference', 'model', and 'app' folders
sys.path.insert(0, str(basedir))
# ---------------------------------------

import threading
from PIL import Image
import customtkinter as ctk
# ... (rest of your imports)
from tkinter import filedialog, messagebox
import cv2
import time
import datetime
import json

if getattr(sys,'frozen', False):
    basedir = os.path.dirname(sys.executable)
else:
    basedir = os.path.dirname(os.path.abspath(__file__))

os.chdir(basedir)
sys.path.insert(0, basedir)

import tensorflow as tf

# Add parent directory and this directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from inference import inference
from model.db import get_db
from model.model_config import MODEL_INPUT_SIZE
from model import report as report_utils
from dmbaimicroscope.settings_manager import get_settings_manager
from dmbaimicroscope.settings_dialog import SettingsDialog
from dmbaimicroscope.services import InferenceService, RecordService, CameraService

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Microscope - Mbeya Regional Referral Hospital")
        self.geometry("1200x800")
        self.resizable(True, True)
        
        # Configure master grid for 3-column layout
        self.grid_columnconfigure(0, weight=1)   # Control Wing (narrow)
        self.grid_columnconfigure(1, weight=3)   # Primary Viewport (wide)
        self.grid_columnconfigure(2, weight=1)   # Intelligence Wing (narrow)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize services and settings
        self.settings_manager = get_settings_manager()
        self.inference_service = InferenceService(model=None)
        self.record_service = RecordService()
        self.camera_service = CameraService()
        
        # State variables
        self.captured_image_path = None
        self.current_frame = None
        self.tkimg = None
        self.heatmap_img = None
        self.model = None  # Initialize model attribute
        
        # Create 3-column dashboard architecture
        self._create_control_wing()      # Column 0: Control Wing
        self._create_primary_viewport()  # Column 1: Primary Viewport  
        self._create_intelligence_wing() # Column 2: Intelligence Wing
        
        # Load settings and populate cameras
        self._load_initial_settings()
        self.after(100, self._populate_cameras)

    def _create_control_wing(self):
        """Column 0: Control Wing - Patient ID, Camera controls, Image adjustments"""
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Title
        title = ctk.CTkLabel(control_frame, text="🎛️ CONTROL WING", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(10, 20))
        
        # Patient ID Section
        patient_frame = ctk.CTkFrame(control_frame)
        patient_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(patient_frame, text="Patient ID", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        self.patient_id = ctk.CTkEntry(patient_frame, placeholder_text="Enter patient ID...")
        self.patient_id.pack(pady=5, padx=10, fill="x")
        
        # Camera Section
        camera_frame = ctk.CTkFrame(control_frame)
        camera_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(camera_frame, text="📷 CAMERA", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        self.camera_menu = ctk.CTkOptionMenu(camera_frame, values=["Detecting..."], command=self._on_camera_select)
        self.camera_menu.pack(pady=5, padx=10, fill="x")
        
        cam_btn_frame = ctk.CTkFrame(camera_frame)
        cam_btn_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_cam_btn = ctk.CTkButton(cam_btn_frame, text="Start Live", command=self.start_camera)
        self.start_cam_btn.pack(pady=2, padx=5, fill="x")
        
        self.stop_cam_btn = ctk.CTkButton(cam_btn_frame, text="Stop Live", command=self.stop_camera)
        self.stop_cam_btn.pack(pady=2, padx=5, fill="x")
        
        # Image Adjustments Section
        adj_frame = ctk.CTkFrame(control_frame)
        adj_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(adj_frame, text="🎨 IMAGE ADJUSTMENTS", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        # Brightness
        ctk.CTkLabel(adj_frame, text="Brightness").pack(anchor="w", padx=10)
        self.brightness_slider = ctk.CTkSlider(adj_frame, from_=0.5, to=1.5, number_of_steps=100)
        self.brightness_slider.set(1.0)
        self.brightness_slider.pack(pady=5, padx=10, fill="x")
        self.brightness_slider.configure(command=self._apply_image_adjustments)
        
        # Contrast
        ctk.CTkLabel(adj_frame, text="Contrast").pack(anchor="w", padx=10)
        self.contrast_slider = ctk.CTkSlider(adj_frame, from_=0.5, to=1.5, number_of_steps=100)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(pady=5, padx=10, fill="x")
        self.contrast_slider.configure(command=self._apply_image_adjustments)
        
        # Upload button
        self.upload_btn = ctk.CTkButton(control_frame, text="📤 Upload Media", command=self.upload_media)
        self.upload_btn.pack(pady=20, padx=10, fill="x")
        
        # Settings button
        self.settings_btn = ctk.CTkButton(control_frame, text="⚙️ Settings", command=self.open_settings)
        self.settings_btn.pack(pady=5, padx=10, fill="x")

    def _create_primary_viewport(self):
        """Column 1: Primary Viewport - Live microscope feed and capture"""
        viewport_frame = ctk.CTkFrame(self)
        viewport_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Title
        title = ctk.CTkLabel(viewport_frame, text="🔬 MICROSCOPE VIEWPORT", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=(10, 20))
        
        # Main image display area
        self.image_label = ctk.CTkLabel(viewport_frame, text="Camera Feed\n(Start camera or upload image)", 
                                      font=ctk.CTkFont(size=14))
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Capture button - prominent and centered
        capture_frame = ctk.CTkFrame(viewport_frame)
        capture_frame.pack(fill="x", padx=20, pady=20)
        
        self.capture_btn = ctk.CTkButton(capture_frame, text="📸 CAPTURE IMAGE", 
                                       command=self.capture_image,
                                       fg_color="blue", hover_color="darkblue",
                                       height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.capture_btn.pack(pady=10, padx=20, fill="x")

    def _create_intelligence_wing(self):
        """Column 2: Intelligence Wing - AI analysis, results, and reporting"""
        intelligence_frame = ctk.CTkFrame(self)
        intelligence_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        # Title
        title = ctk.CTkLabel(intelligence_frame, text="🤖 INTELLIGENCE WING", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(pady=(10, 20))
        
        # AI Analysis Section
        ai_frame = ctk.CTkFrame(intelligence_frame)
        ai_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(ai_frame, text="🧬 AI ANALYSIS", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        self.analyze_btn = ctk.CTkButton(ai_frame, text="🔍 Run AI Diagnosis", command=self.run_diagnosis,
                                        fg_color="green", hover_color="darkgreen", height=40)
        self.analyze_btn.pack(pady=10, padx=10, fill="x")
        
        # Results Display Section
        results_frame = ctk.CTkFrame(intelligence_frame)
        results_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(results_frame, text="📊 RESULTS", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        # Species result
        self.result_label = ctk.CTkLabel(results_frame, text="Species: —", 
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.result_label.pack(pady=5, padx=10)
        
        # Confidence progress bar
        ctk.CTkLabel(results_frame, text="Confidence:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(5, 0))
        self.confidence_bar = ctk.CTkProgressBar(results_frame)
        self.confidence_bar.pack(pady=5, padx=10, fill="x")
        self.confidence_bar.set(0)
        
        # Grad-CAM Display
        gradcam_frame = ctk.CTkFrame(intelligence_frame)
        gradcam_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(gradcam_frame, text="🔥 GRAD-CAM HEATMAP", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        self.gradcam_label = ctk.CTkLabel(gradcam_frame, text="Grad-CAM\n(run AI diagnosis)", 
                                         font=ctk.CTkFont(size=11))
        self.gradcam_label.pack(pady=10, padx=10, fill="x")
        
        # Export Section
        export_frame = ctk.CTkFrame(intelligence_frame)
        export_frame.pack(fill="x", padx=10, pady=20)
        
        ctk.CTkLabel(export_frame, text="📤 EXPORT", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        self.export_btn = ctk.CTkButton(export_frame, text="📊 Generate Report", command=self.export_reports,
                                       fg_color="orange", hover_color="darkorange")
        self.export_btn.pack(pady=10, padx=10, fill="x")

    def _load_initial_settings(self):
        """Load initial settings values"""
        try:
            self.brightness_slider.set(self.settings_manager.get("image_adjustments", "brightness"))
            self.contrast_slider.set(self.settings_manager.get("image_adjustments", "contrast"))
        except:
            pass  # Use defaults if settings not available

    def capture_image(self):
        # if live camera is running, capture current frame
        if self.camera_service.running and self.current_frame is not None:
            self.capture_from_camera()
            return

        path = filedialog.askopenfilename(title="Select image to simulate capture",
                                          filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not path:
            return
        self.captured_image_path = path
        img = Image.open(path).resize((200, 200))
        self.tkimg = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 200))
        self.image_label.configure(image=self.tkimg, text="")
        # Reset Grad-CAM display when new image is captured
        self.gradcam_label.configure(image=None, text="Grad-CAM\n(run AI diagnosis)")
        self.result_label.configure(text="Identified species: —")

    def upload_media(self):
        """Allow user to upload an image or a video file. For videos, extract a single frame."""
        path = filedialog.askopenfilename(title="Select image or video",
                                          filetypes=[
                                              ("All supported media", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff;*.gif;*.webp;*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.webm"),
                                              ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff;*.gif;*.webp"),
                                              ("Video files", "*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.webm"),
                                              ("All files", "*.*")
                                          ])
        if not path:
            return

        suffix = Path(path).suffix.lower()
        image_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.gif', '.webp'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        
        # Ensure save directory exists
        save_dir = Path("model/records")
        save_dir.mkdir(parents=True, exist_ok=True)

        if suffix in image_exts:
            # simple image upload
            try:
                dest = save_dir / Path(path).name
                from shutil import copy2
                copy2(path, dest)
                self.captured_image_path = str(dest)
                img = Image.open(dest).resize((200, 200))
                self.tkimg = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 200))
                self.image_label.configure(image=self.tkimg, text="")
                # Reset Grad-CAM display when new image is uploaded
                self.gradcam_label.configure(image=None, text="Grad-CAM\n(run AI diagnosis)")
                self.result_label.configure(text="Identified species: —")
            except Exception as e:
                messagebox.showerror("Upload error", f"Failed to upload image: {e}")
        elif suffix in video_exts:
            # extract a frame from video (middle frame)
            try:
                import cv2
                import time
                cap = cv2.VideoCapture(path)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                middle_frame = total_frames // 2
                cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
                ret, frame = cap.read()
                cap.release()
                if not ret:
                    raise RuntimeError("Failed to read frame from video")
                timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
                out = save_dir / f"upload_video_frame_{timestamp}.png"
                cv2.imwrite(str(out), frame)
                self.captured_image_path = str(out)
                img = Image.open(out).resize((200, 200))
                self.tkimg = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 200))
                self.image_label.configure(image=self.tkimg, text="")
                # Reset Grad-CAM display when new video frame is uploaded
                self.gradcam_label.configure(image=None, text="Grad-CAM\n(run AI diagnosis)")
                self.result_label.configure(text="Identified species: —")
            except Exception as e:
                messagebox.showerror("Upload error", f"Failed to extract frame: {e}")
        else:
            messagebox.showwarning("Unsupported file", f"Selected file type '{suffix}' is not supported.\n\nSupported formats:\nImages: PNG, JPG, JPEG, BMP, TIFF, GIF, WebP\nVideos: MP4, AVI, MOV, MKV, WMV, FLV, WebM")

    def _populate_cameras(self):
        # Try to detect available camera indices via service
        cams = self.camera_service.detect_cameras(max_index=5)
        self.camera_menu.configure(values=cams)
        # select first available
        try:
            self.camera_menu.set(cams[0])
        except Exception:
            pass

    def _on_camera_select(self, value):
        # noop; selection read at start
        return

    def run_diagnosis(self):
        if not self.captured_image_path:
            messagebox.showwarning("Warning", "Please capture or upload an image first.")
            return
        self.result_label.configure(text="DIAGNOSING... PLEASE WAIT", text_color="#f1c40f")
        threading.Thread(target=self._diagnosis_worker, daemon=True).start()

    def _diagnosis_worker(self):
        """The background thread that runs the AI with dynamic visual feedback."""
        result = None  # Initialize result variable
        
        try:
            # 1. Load model if not already loaded
            if self.model is None:
                from inference.inference import load_model
                self.model = load_model()
                # Update service with loaded model
                self.inference_service.model = self.model

            # 2. Run Prediction + Grad-CAM logic via service
            result, heatmap_img = self.inference_service.run(self.captured_image_path)

            # 3. Dynamic Visual Feedback based on status
            status = result.get("status", "UNKNOWN")
            confidence = result.get("confidence", 0.0)
            species = result.get("species", "Unknown")
            
            if status == "CONFIRMED":
                # CONFIRMED: High confidence - Clinical green
                display_text = f"IDENTIFIED: {species.upper()}\nCONFIDENCE: {confidence:.1%}"
                color = "#2ecc71"  # Clinical green
                bar_color = "#27ae60"  # Darker green for progress bar
            elif status == "REJECTED":
                # REJECTED: Low confidence - Warning red
                display_text = f"INCONCLUSIVE\nCONFIDENCE: {confidence:.1%}\nSAMPLE REJECTED"
                color = "#e74c3c"  # Warning red
                bar_color = "#c0392b"  # Darker red for progress bar
            else:
                # UNKNOWN: Error case - Orange
                display_text = f"ERROR\nSTATUS: {status}\nPLEASE RETRY"
                color = "#f39c12"  # Orange
                bar_color = "#e67e22"  # Darker orange

            # Update UI with dynamic colors
            self.after(0, lambda: self.result_label.configure(
                text=display_text, 
                text_color=color
            ))
            
            # Update confidence progress bar with dynamic color
            self.after(0, lambda: self.confidence_bar.set(confidence))
            self.after(0, lambda: self.confidence_bar.configure(
                progress_color=bar_color
            ))

            # 4. Display Grad-CAM (works for both CONFIRMED and REJECTED)
            if heatmap_img:
                # Resize for UI display
                ctk_heatmap = ctk.CTkImage(light_image=heatmap_img, size=(320, 320))
                self.after(0, lambda: self.gradcam_label.configure(image=ctk_heatmap))
                self.after(0, lambda: setattr(self.gradcam_label, "image", ctk_heatmap))

        except Exception as e:
            import traceback
            traceback.print_exc()
            # Error handling with visual feedback
            error_msg = f"AI Error: {str(e)[:50]}..."
            self.after(0, lambda: self.result_label.configure(
                text=error_msg,
                text_color="#e74c3c",  # Red for errors
            ))
            self.after(0, lambda: self.confidence_bar.set(0))
            self.after(0, lambda: self.confidence_bar.configure(
                progress_color="#e74c3c"  # Red for errors
            ))
            
            # Create a fallback result for database
            result = {
                "species": "Error",
                "confidence": 0.0,
                "class_index": -1,
                "status": "ERROR"
            }

        # 5. Database Persistence (works regardless of status)
        try:
            if result:  # Only save if we have a result
                self.record_service.save_record(
                    patient_id=(self.patient_id.get() or "N/A"),
                    result=result,
                    source_image_path=self.captured_image_path,
                )
        except Exception as e:
            pass  # Database errors handled silently

    # Camera control methods
    def start_camera(self):
        selected = self.camera_menu.get() if hasattr(self.camera_menu, 'get') else None
        cam_index = None
        try:
            cam_index = int(selected)
        except Exception:
            cam_index = 0

        # open capture via service
        if not self.camera_service.start(cam_index):
            messagebox.showerror("Camera error", f"Unable to open camera {cam_index}")
            return

        self.result_label.configure(text="Identified species: Live camera feed")
        self._update_frame()

    def stop_camera(self):
        self.camera_service.stop()
        self.result_label.configure(text="Identified species: Camera stopped")

    def _update_frame(self):
        if not self.camera_service.running:
            return
        frame = self.camera_service.read_frame()
        if frame is None:
            # try again shortly
            self.after(100, self._update_frame)
            return
        # store current frame (BGR)
        self.current_frame = frame
        # convert to PIL and display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((512, 512))
        
        # Apply image adjustments
        img = self._apply_image_adjustments_to_image(img)
        
        self.tkimg = ctk.CTkImage(light_image=img, dark_image=img, size=(512, 512))
        self.image_label.configure(image=self.tkimg, text="")
        # schedule next frame
        self.after(30, self._update_frame)

    def _apply_image_adjustments(self, value=None):
        """Apply image adjustments from sliders."""
        # Save current values to settings
        self.settings_manager.set("image_adjustments", "brightness", self.brightness_slider.get())
        self.settings_manager.set("image_adjustments", "contrast", self.contrast_slider.get())
        self.settings_manager.save()

    def _apply_image_adjustments_to_image(self, img):
        """Apply brightness and contrast adjustments to an image."""
        from PIL import ImageEnhance
        
        brightness = self.brightness_slider.get()
        contrast = self.contrast_slider.get()
        
        # Apply brightness adjustment
        if brightness != 0:
            enhancer = ImageEnhance.Brightness(img)
            factor = 1.0 + (brightness / 100.0)
            img = enhancer.enhance(factor)
        
        # Apply contrast adjustment
        if contrast != 0:
            enhancer = ImageEnhance.Contrast(img)
            factor = 1.0 + (contrast / 100.0)
            img = enhancer.enhance(factor)
        
        return img

    def capture_from_camera(self):
        if self.current_frame is None:
            messagebox.showwarning("No frame", "No camera frame available to capture.")
            return
        try:
            save_dir = Path(__file__).resolve().parents[1] / "model" / "records"
            img_dest = self.camera_service.capture_frame_to_file(self.current_frame, save_dir)
            self.captured_image_path = str(img_dest)
            img = Image.open(img_dest).resize((512, 512))
            self.tkimg = ctk.CTkImage(light_image=img, dark_image=img, size=(512, 512))
            self.image_label.configure(image=self.tkimg, text="")
            # Reset Grad-CAM display when new image is captured from camera
            self.gradcam_label.configure(image=None, text="Grad-CAM\n(run AI diagnosis)")
            self.result_label.configure(text="Identified species: —")
        except Exception as e:
            messagebox.showerror("Save error", f"Failed to save capture: {e}")

    def export_reports(self):
        """Export recent clinical records. User can choose Save As or use default export dir from settings."""
        try:
            db = get_db()
        except Exception as e:
            messagebox.showerror("DB error", f"Database not available: {e}")
            return

        # Ask user whether to use default export dir
        use_default = False
        default_dir = None
        try:
            default_dir = str(self.settings_manager.get_export_directory())
            if default_dir:
                use_default = messagebox.askyesno("Export location", f"Export to default directory?\n{default_dir}")
        except Exception:
            use_default = False

        if use_default and default_dir:
            out_dir = (Path(__file__).resolve().parents[1] / Path(default_dir)).resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            # Default to CSV export in default directory, and also create a PDF summary
            csv_path = out_dir / f"clinical_export_{timestamp}.csv"
            pdf_path = out_dir / f"clinical_export_{timestamp}.pdf"
            try:
                db.export_csv(str(csv_path))
                try:
                    report_utils.export_recent_pdf(db=db, out_path=str(pdf_path))
                except Exception:
                    # Non-fatal: PDF may fail if reportlab not installed or thumbnails missing
                    pass
                messagebox.showinfo("Export", f"Exported {csv_path}\nAlso attempted PDF: {pdf_path}")
            except Exception as e:
                messagebox.showerror("Export error", f"Failed to export: {e}")
            return

        # Otherwise prompt Save As
        save_path = filedialog.asksaveasfilename(title="Save export as", defaultextension='.csv', filetypes=[('CSV','*.csv'), ('PDF','*.pdf')])
        if not save_path:
            return
        try:
            suffix = Path(save_path).suffix.lower()
            if suffix == '.pdf':
                try:
                    report_utils.export_recent_pdf(db=db, out_path=save_path)
                    messagebox.showinfo("Export", f"Exported {save_path}")
                except Exception as e:
                    messagebox.showerror("Export error", f"Failed to export PDF: {e}")
            else:
                db.export_csv(save_path)
                messagebox.showinfo("Export", f"Exported {save_path}")
        except Exception as e:
            messagebox.showerror("Export error", f"Failed to export: {e}")

    def export_csv(self):
        """Export clinical records to CSV."""
        try:
            from model.db import get_db
            db = get_db()
            csv_path = f"clinical_records_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            exported = db.export_csv(csv_path)
            if exported:
                messagebox.showinfo("Export Successful", f"Records exported to:\n{exported}")
            else:
                messagebox.showerror("Export Failed", "Could not export records.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")
    def open_user_guide(self):
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

    def open_faq(self):
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

    def open_privacy_policy(self):
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

    def show_about(self):
        """Show about dialog."""
        about_text = """AI Microscope v1.0.0
        
An advanced diagnostic tool for bacterial identification 
using artificial intelligence and computer vision.

Developed for Mbeya Regional Referral Hospital
© 2026 DMB MUST

Features:
• 39 bacterial species identification
• Grad-CAM explainable AI
• Clinical record management
• PDF/CSV export capabilities
• Real-time camera integration

For support, contact the IT Department."""
        
        messagebox.showinfo("About AI Microscope", about_text)

    def open_settings(self):
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
        if self.camera_service.running:
            self.stop_camera()
            self.start_camera()

def main():
    app = MainApp()
    app.mainloop()
    return app
    
if __name__ == "__main__":
    main()
