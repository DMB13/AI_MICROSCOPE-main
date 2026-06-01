#!/usr/bin/env python3
"""
Patient Data Anonymization Service
Handles anonymization of patient data for privacy protection
"""

import hashlib
from typing import Optional, Dict, Any
from datetime import datetime


class PatientAnonymizer:
    """Service for anonymizing patient data."""
    
    def __init__(self):
        """Initialize anonymizer."""
        self.salt = "AI_MICROSCOPE_SALT_2024"
    
    def anonymize_patient_id(self, patient_id: str) -> str:
        """Anonymize patient ID with hash.
        
        Args:
            patient_id: Original patient ID
            
        Returns:
            Anonymized patient ID (hash)
        """
        if not patient_id:
            return "UNKNOWN"
        
        # Create hash of patient ID
        hash_input = f"{self.salt}{patient_id}".encode()
        hash_digest = hashlib.sha256(hash_input).hexdigest()
        return f"PAT_{hash_digest[:8]}"
    
    def anonymize_name(self, full_name: str) -> str:
        """Anonymize patient name.
        
        Args:
            full_name: Full patient name
            
        Returns:
            Anonymized name (initials only)
        """
        if not full_name:
            return "UNKNOWN"
        
        # Extract initials
        parts = full_name.split()
        initials = "".join([p[0].upper() for p in parts if p])
        return f"Patient {initials}"
    
    def anonymize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize a clinical record.
        
        Args:
            record: Clinical record dictionary
            
        Returns:
            Anonymized record
        """
        anonymized = record.copy()
        
        # Anonymize sensitive fields
        if "patient_id" in anonymized:
            anonymized["patient_id"] = self.anonymize_patient_id(record["patient_id"])
            anonymized["patient_id_original"] = "***ANONYMIZED***"
        
        if "patient_name" in anonymized:
            anonymized["patient_name"] = self.anonymize_name(record["patient_name"])
            anonymized["patient_name_original"] = "***ANONYMIZED***"
        
        if "age" in anonymized:
            # Bucket age ranges
            age = record.get("age", 0)
            if age < 18:
                anonymized["age"] = "<18"
            elif age < 30:
                anonymized["age"] = "18-29"
            elif age < 50:
                anonymized["age"] = "30-49"
            elif age < 70:
                anonymized["age"] = "50-69"
            else:
                anonymized["age"] = "70+"
        
        # Remove other potentially identifying fields
        fields_to_remove = ["address", "phone", "email", "national_id"]
        for field in fields_to_remove:
            if field in anonymized:
                anonymized[field] = "***REDACTED***"
        
        # Add anonymization metadata
        anonymized["anonymized"] = True
        anonymized["anonymized_at"] = datetime.now().isoformat()
        
        return anonymized
    
    def de_identify_export(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for export with de-identification.
        
        Args:
            data: Data to export
            
        Returns:
            De-identified data
        """
        if isinstance(data, list):
            return [self.anonymize_record(item) for item in data]
        elif isinstance(data, dict):
            return self.anonymize_record(data)
        return data
