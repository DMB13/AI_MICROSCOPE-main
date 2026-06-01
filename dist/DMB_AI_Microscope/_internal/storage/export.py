#!/usr/bin/env python3
"""
Export Service for AI Microscope Application
Handles export of records to various formats
"""

from typing import List, Optional
from pathlib import Path
import csv
import json

from core.domain.models import PatientRecord
from utils.logger import log_info, log_error
from config.constants import EXPORT_DIR


class ExportService:
    """Service for exporting patient records."""
    
    def __init__(self, repository):
        """Initialize export service with repository."""
        self.repository = repository
        self.export_dir = EXPORT_DIR
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_csv(self, output_path: Optional[str] = None) -> Optional[str]:
        """Export all records to CSV format.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to exported file or None if failed
        """
        try:
            if output_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.export_dir / f"export_{timestamp}.csv"
            
            success = self.repository.export_to_csv(str(output_path))
            
            if success:
                log_info(f"CSV export successful: {output_path}")
                return str(output_path)
            else:
                log_error("CSV export failed")
                return None
                
        except Exception as e:
            log_error(f"CSV export error: {str(e)}", exc_info=True)
            return None
    
    def export_to_json(self, output_path: Optional[str] = None) -> Optional[str]:
        """Export all records to JSON format.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to exported file or None if failed
        """
        try:
            records = self.repository.get_all_records()
            
            if output_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.export_dir / f"export_{timestamp}.json"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump([record.to_dict() for record in records], f, indent=2, ensure_ascii=False)
            
            log_info(f"JSON export successful: {output_path}")
            return str(output_path)
            
        except Exception as e:
            log_error(f"JSON export error: {str(e)}", exc_info=True)
            return None
    
    def export_patient_to_csv(self, patient_id: str, output_path: Optional[str] = None) -> Optional[str]:
        """Export records for a specific patient to CSV.
        
        Args:
            patient_id: Patient identifier
            output_path: Optional custom output path
            
        Returns:
            Path to exported file or None if failed
        """
        try:
            records = self.repository.get_records_by_patient(patient_id)
            
            if output_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.export_dir / f"patient_{patient_id}_{timestamp}.csv"
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                writer.writerow([
                    'Patient ID', 'Species', 'Confidence', 'Status',
                    'Image Path', 'Timestamp', 'Clinical Notes', 'Sample ID'
                ])
                
                for record in records:
                    writer.writerow([
                        record.patient_id,
                        record.diagnosis.species,
                        f"{record.diagnosis.confidence:.4f}",
                        record.diagnosis.status.value,
                        record.image_path,
                        record.timestamp.isoformat(),
                        record.clinical_notes,
                        record.sample_id
                    ])
            
            log_info(f"Patient CSV export successful: {output_path}")
            return str(output_path)
            
        except Exception as e:
            log_error(f"Patient CSV export error: {str(e)}", exc_info=True)
            return None
