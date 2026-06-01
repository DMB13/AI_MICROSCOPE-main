#!/usr/bin/env python3
"""
Patient Service for AI Microscope Application
Business logic for patient record management
"""

from typing import Optional, List
from datetime import datetime

from core.domain.models import PatientRecord
from utils.logger import log_info, log_error, log_warning
from config.constants import MIN_PATIENT_ID_LENGTH


class PatientService:
    """Service for managing patient records and validation."""
    
    def __init__(self, storage_repository):
        """Initialize patient service with storage backend."""
        self.storage = storage_repository
    
    def validate_patient_id(self, patient_id: str) -> tuple[bool, str]:
        """Validate patient ID format.
        
        Args:
            patient_id: Patient identifier to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if not patient_id or not patient_id.strip():
            return False, "Patient ID is required"
        
        patient_id = patient_id.strip()
        
        if len(patient_id) < MIN_PATIENT_ID_LENGTH:
            return False, f"Patient ID must be at least {MIN_PATIENT_ID_LENGTH} characters"
        
        return True, "Patient ID is valid"
    
    def create_patient_record(
        self,
        patient_id: str,
        diagnosis,
        image_path: str,
        sample_id: Optional[str] = None,
        clinical_notes: Optional[str] = None
    ) -> PatientRecord:
        """Create a new patient record.
        
        Args:
            patient_id: Patient identifier
            diagnosis: DiagnosisResult object
            image_path: Path to diagnostic image
            sample_id: Optional sample identifier
            clinical_notes: Optional clinical notes
            
        Returns:
            PatientRecord object
        """
        # Validate patient ID
        is_valid, reason = self.validate_patient_id(patient_id)
        if not is_valid:
            log_warning(f"Invalid patient ID: {reason}")
            raise ValueError(reason)
        
        record = PatientRecord(
            patient_id=patient_id,
            diagnosis=diagnosis,
            image_path=image_path,
            sample_id=sample_id,
            clinical_notes=clinical_notes
        )
        
        log_info(f"Created patient record for {patient_id}")
        return record
    
    def save_patient_record(self, record: PatientRecord) -> bool:
        """Save patient record to storage.
        
        Args:
            record: PatientRecord to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not record.validate():
                log_error("Invalid patient record - missing required fields")
                return False
            
            self.storage.save_record(record)
            log_info(f"Saved patient record for {record.patient_id}")
            return True
            
        except Exception as e:
            log_error(f"Failed to save patient record: {str(e)}", exc_info=True)
            return False
    
    def get_patient_records(self, patient_id: str) -> List[PatientRecord]:
        """Get all records for a patient.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            List of PatientRecord objects
        """
        try:
            records = self.storage.get_records_by_patient(patient_id)
            log_info(f"Retrieved {len(records)} records for patient {patient_id}")
            return records
        except Exception as e:
            log_error(f"Failed to retrieve patient records: {str(e)}", exc_info=True)
            return []
