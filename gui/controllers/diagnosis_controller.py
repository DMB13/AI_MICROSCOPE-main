#!/usr/bin/env python3
"""
Diagnosis Controller for AI Microscope
Manages AI diagnosis operations and bridges GUI with vision layer
"""

from typing import Optional, Callable
import threading
import inference as inference_module
from core.services.diagnosis_service import DiagnosisService
from vision.inference_wrapper import InferenceWrapper
from core.domain.models import DiagnosisResult
from utils.logger import log_info, log_error, log_warning
from config.constants import CLINICAL_CONFIDENCE_THRESHOLD


class DiagnosisController:
    """Controller for AI diagnosis operations."""
    
    def __init__(self, inference_wrapper: Optional[InferenceWrapper] = None):
        """Initialize diagnosis controller.
        
        Args:
            inference_wrapper: InferenceWrapper instance (creates new if None)
        """
        self.inference_wrapper = inference_wrapper or InferenceWrapper()
        self.diagnosis_service = DiagnosisService(self.inference_wrapper)
        self.current_diagnosis: Optional[DiagnosisResult] = None
        self.on_diagnosis_complete: Optional[Callable] = None
        self.on_diagnosis_error: Optional[Callable] = None
        self.is_running = False
    
    def run_diagnosis(
        self,
        image_path: str,
        patient_id: str,
        confidence_threshold: float = CLINICAL_CONFIDENCE_THRESHOLD
    ) -> None:
        """Run diagnosis in a separate thread.
        
        Args:
            image_path: Path to image file
            patient_id: Patient identifier
            confidence_threshold: Clinical confidence threshold
        """
        if self.is_running:
            log_warning("Diagnosis already in progress")
            return
        
        self.is_running = True
        log_info(f"Starting diagnosis for patient {patient_id}")
        
        # Run in background thread
        thread = threading.Thread(
            target=self._run_diagnosis_thread,
            args=(image_path, patient_id, confidence_threshold),
            daemon=True
        )
        thread.start()
    
    def _run_diagnosis_thread(
        self,
        image_path: str,
        patient_id: str,
        confidence_threshold: float
    ) -> None:
        """Run diagnosis in background thread with enhanced error handling."""
        try:
            diagnosis = self.diagnosis_service.run_diagnosis(
                image_path,
                patient_id,
                confidence_threshold
            )
            
            # Add clinical recommendations based on status (stored in metadata)
            if diagnosis.status.value == "low_confidence":
                diagnosis.metadata["clinical_recommendation"] = (
                    "RECOMMENDATION: Image quality may be insufficient.\n\n"
                    "Suggested actions:\n"
                    "1. Ensure proper Gram staining of bacterial sample\n"
                    "2. Verify microscope is properly focused\n"
                    "3. Check lighting and exposure settings\n"
                    "4. Ensure adequate bacterial concentration\n"
                    "5. Consider re-capturing the image"
                )
            elif diagnosis.status.value == "success":
                diagnosis.metadata["clinical_recommendation"] = (
                    "Diagnosis meets clinical standards. "
                    "Please verify with laboratory culture and sensitivity testing."
                )
            elif diagnosis.status.value == "error":
                diagnosis.metadata["clinical_recommendation"] = (
                    "Technical error during analysis. "
                    "Please try again or contact IT support."
                )
            
            self.current_diagnosis = diagnosis
            self.is_running = False
            
            # Notify callback
            if self.on_diagnosis_complete:
                self.on_diagnosis_complete(diagnosis)
            
        except Exception as e:
            self.is_running = False
            log_error(f"Diagnosis thread error: {str(e)}", exc_info=True)
            
            # Categorize error for user-friendly message
            error_type = self._categorize_error(e)
            user_message = self._get_helpful_error_message(error_type, str(e))
            
            if self.on_diagnosis_error:
                self.on_diagnosis_error(user_message)
    
    def _categorize_error(self, error: Exception) -> str:
        """Categorize error type for appropriate handling.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Error type string
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        if "memory" in error_str or "oom" in error_str:
            return "memory_error"
        elif "gpu" in error_str or "cuda" in error_str or "device" in error_str:
            return "gpu_error"
        elif "model" in error_str or "load" in error_str:
            return "model_load_error"
        elif "image" in error_str or "file" in error_str or "path" in error_str:
            return "image_read_error"
        elif "camera" in error_str or "capture" in error_str:
            return "camera_error"
        elif "permission" in error_str or "access" in error_str:
            return "permission_error"
        elif "timeout" in error_str:
            return "timeout_error"
        else:
            return "inference_error"
    
    def _get_helpful_error_message(self, error_type: str, original_error: str) -> str:
        """Generate user-friendly, actionable error message.
        
        Args:
            error_type: Type of error
            original_error: Original error message
            
        Returns:
            Helpful error message for display
        """
        error_messages = {
            "model_load_error": (
                "AI model failed to load.\n\n"
                "TROUBLESHOOTING:\n"
                "1. Restart the application\n"
                "2. Check available system memory (16GB+ recommended)\n"
                "3. Verify model files are not corrupted\n"
                "4. Contact IT support if issue persists"
            ),
            "image_read_error": (
                "Cannot read image file.\n\n"
                "TROUBLESHOOTING:\n"
                "1. Check if image file exists and is not corrupted\n"
                "2. Ensure file format is supported (JPG, PNG, BMP, TIFF)\n"
                "3. Verify file is not open in another program\n"
                "4. Try uploading a different image"
            ),
            "camera_error": (
                "Camera not accessible.\n\n"
                "TROUBLESHOOTING:\n"
                "1. Check camera connections\n"
                "2. Verify camera is not in use by another application\n"
                "3. Restart the microscope camera\n"
                "4. Check Windows camera permissions"
            ),
            "memory_error": (
                "System memory is low.\n\n"
                "TROUBLESHOOTING:\n"
                "1. Close other applications to free memory\n"
                "2. Restart the application\n"
                "3. Consider upgrading system RAM (16GB+ recommended)\n"
                "4. Reduce image resolution before analysis"
            ),
            "gpu_error": (
                "GPU processing error.\n\n"
                "TROUBLESHOOTING:\n"
                "1. GPU will be disabled, CPU will be used instead\n"
                "2. Analysis will continue but may be slower\n"
                "3. Update graphics drivers if available"
            ),
            "permission_error": (
                "Permission denied.\n\n"
                "TROUBLESHOOTING:\n"
                "1. Run application as administrator\n"
                "2. Check file/folder permissions\n"
                "3. Ensure antivirus is not blocking access"
            ),
            "timeout_error": (
                "Analysis timed out.\n\n"
                "TROUBLESHOOTING:\n"
                "1. Image may be too large or complex\n"
                "2. Try with a smaller image\n"
                "3. Check system performance"
            ),
            "inference_error": (
                f"AI analysis failed: {original_error[:100]}\n\n"
                "TROUBLESHOOTING:\n"
                "1. Try again with a clearer image\n"
                "2. Ensure proper staining and focus\n"
                "3. Restart the application\n"
                "4. Contact IT support if issue persists"
            )
        }
        
        return error_messages.get(error_type, (
            f"An unexpected error occurred:\n{original_error[:100]}\n\n"
            "Please try again or contact IT support."
        ))
    
    def generate_gradcam(self, image_path: str):
        """Generate Grad-CAM heatmap for the current image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL Image: The blended heatmap image
        """
        try:
            # Get the model from the inference_wrapper
            model = self.inference_wrapper.get_model()
            
            # Call the function in inference.py that returns the blended image
            # Note: inference.py returns a PIL Image, not a path!
            gradcam_img = inference_module.grad_cam(image_path, model=model)
            
            return gradcam_img
        except Exception as e:
            log_error(f"Controller failed to generate Grad-CAM: {str(e)}")
            return None
        
    def get_current_diagnosis(self) -> Optional[DiagnosisResult]:
        """Get the most recent diagnosis.
        
        Returns:
            DiagnosisResult or None if no diagnosis available
        """
        return self.current_diagnosis
    
    def validate_for_clinical_use(
        self,
        diagnosis: Optional[DiagnosisResult] = None,
        threshold: float = CLINICAL_CONFIDENCE_THRESHOLD
    ) -> tuple[bool, str]:
        """Validate if diagnosis meets clinical standards.
        
        Args:
            diagnosis: DiagnosisResult to validate (uses current if None)
            threshold: Confidence threshold
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if diagnosis is None:
            diagnosis = self.current_diagnosis
        
        if diagnosis is None:
            return False, "No diagnosis available"
        
        return self.diagnosis_service.validate_diagnosis_for_clinical_use(
            diagnosis,
            threshold
        )
    
    def set_diagnosis_complete_callback(self, callback: Callable) -> None:
        """Set callback for when diagnosis completes.
        
        Args:
            callback: Function to call with DiagnosisResult
        """
        self.on_diagnosis_complete = callback
    
    def set_diagnosis_error_callback(self, callback: Callable) -> None:
        """Set callback for when diagnosis fails.
        
        Args:
            callback: Function to call with error message
        """
        self.on_diagnosis_error = callback
    
    def reset(self) -> None:
        """Reset controller state."""
        self.current_diagnosis = None
        self.is_running = False
