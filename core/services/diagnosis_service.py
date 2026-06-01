#!/usr/bin/env python3
"""
Diagnosis Service for AI Microscope Application
Business logic for running AI diagnosis
"""

from typing import Optional, Dict, Any
from pathlib import Path

from core.domain.models import DiagnosisResult, DiagnosisStatus
from utils.logger import log_info, log_error, log_warning
from config.constants import CLINICAL_CONFIDENCE_THRESHOLD


class DiagnosisService:
    """Service for managing AI diagnosis operations."""
    
    def __init__(self, inference_service):
        """Initialize diagnosis service with inference backend."""
        self.inference_service = inference_service
    
    def run_diagnosis(
        self,
        image_path: str,
        patient_id: str,
        confidence_threshold: float = CLINICAL_CONFIDENCE_THRESHOLD
    ) -> DiagnosisResult:
        """Run AI diagnosis on an image.
        
        Args:
            image_path: Path to the image file
            patient_id: Patient identifier
            confidence_threshold: Clinical confidence threshold
            
        Returns:
            DiagnosisResult object with diagnosis information
        """
        log_info(f"Running diagnosis for patient {patient_id} on image {image_path}")
        
        try:
            # Run inference
            result = self.inference_service.run_inference(image_path)
            
            # Determine status
            if result.get("error"):
                status = DiagnosisStatus.ERROR
                confidence = 0.0
                species = "Error"
                class_index = -1
            else:
                confidence = result.get("confidence", 0.0)
                species = result.get("species", "Unknown")
                class_index = result.get("class_index", -1)
                
                if confidence >= confidence_threshold:
                    status = DiagnosisStatus.SUCCESS
                else:
                    status = DiagnosisStatus.LOW_CONFIDENCE
            
            # Create diagnosis result
            diagnosis = DiagnosisResult(
                species=species,
                confidence=confidence,
                class_index=class_index,
                status=status,
                metadata={
                    "patient_id": patient_id,
                    "image_path": image_path,
                    "model_used": getattr(self.inference_service, 'model_name', 'unknown')
                }
            )
            
            log_info(f"Diagnosis complete: {species} ({confidence:.2%}) - {status.value}")
            return diagnosis
            
        except Exception as e:
            log_error(f"Diagnosis failed: {str(e)}", exc_info=True)
            return DiagnosisResult(
                species="Error",
                confidence=0.0,
                class_index=-1,
                status=DiagnosisStatus.ERROR,
                metadata={"error": str(e)}
            )
    
    def validate_diagnosis_for_clinical_use(
        self,
        diagnosis: DiagnosisResult,
        threshold: float = CLINICAL_CONFIDENCE_THRESHOLD
    ) -> tuple[bool, str]:
        """Validate if diagnosis meets clinical standards.
        
        Args:
            diagnosis: DiagnosisResult to validate
            threshold: Confidence threshold
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if diagnosis.status == DiagnosisStatus.ERROR:
            return False, "Diagnosis encountered an error"
        
        if diagnosis.confidence < threshold:
            return False, f"Confidence {diagnosis.confidence:.2%} below threshold {threshold:.2%}"
        
        if not diagnosis.species or diagnosis.species == "Unknown":
            return False, "Species identification failed"
        
        return True, "Diagnosis meets clinical standards"
