#!/usr/bin/env python3
"""
Storage Repository for AI Microscope Application
Handles database operations for patient records
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import sqlite3
import json

from core.domain.models import PatientRecord, DiagnosisResult
from utils.logger import log_info, log_error
from config.constants import DB_FILE


class PatientRecordRepository:
    """Repository for patient record storage operations."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize repository with database path."""
        self.db_path = db_path or DB_FILE
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database schema if not exists."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create records table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patient_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id TEXT NOT NULL,
                        species TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        class_index INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        image_path TEXT NOT NULL,
                        gradcam_path TEXT,
                        timestamp TEXT NOT NULL,
                        clinical_notes TEXT,
                        sample_id TEXT,
                        metadata TEXT
                    )
                """)
                
                conn.commit()
                log_info(f"Database initialized at {self.db_path}")
                
        except Exception as e:
            log_error(f"Failed to initialize database: {str(e)}", exc_info=True)
            raise
    
    def save_record(self, record: PatientRecord) -> bool:
        """Save a patient record to the database.
        
        Args:
            record: PatientRecord to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO patient_records (
                        patient_id, species, confidence, class_index, status,
                        image_path, gradcam_path, timestamp, clinical_notes,
                        sample_id, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.patient_id,
                    record.diagnosis.species,
                    record.diagnosis.confidence,
                    record.diagnosis.class_index,
                    record.diagnosis.status.value,
                    record.image_path,
                    record.diagnosis.gradcam_path,
                    record.timestamp.isoformat(),
                    record.clinical_notes,
                    record.sample_id,
                    json.dumps(record.diagnosis.metadata)
                ))
                
                conn.commit()
                log_info(f"Record saved for patient {record.patient_id}")
                return True
                
        except Exception as e:
            log_error(f"Failed to save record: {str(e)}", exc_info=True)
            return False
    
    def get_records_by_patient(self, patient_id: str) -> List[PatientRecord]:
        """Get all records for a specific patient.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            List of PatientRecord objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM patient_records
                    WHERE patient_id = ?
                    ORDER BY timestamp DESC
                """, (patient_id,))
                
                rows = cursor.fetchall()
                return [self._row_to_record(row) for row in rows]
                
        except Exception as e:
            log_error(f"Failed to retrieve records: {str(e)}", exc_info=True)
            return []
    
    def get_all_records(self, limit: int = 100) -> List[PatientRecord]:
        """Get all records with optional limit.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of PatientRecord objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM patient_records
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                return [self._row_to_record(row) for row in rows]
                
        except Exception as e:
            log_error(f"Failed to retrieve records: {str(e)}", exc_info=True)
            return []
    
    def _row_to_record(self, row: tuple) -> PatientRecord:
        """Convert database row to PatientRecord object."""
        from datetime import datetime
        from core.domain.models import DiagnosisStatus
        
        return PatientRecord(
            patient_id=row[1],
            diagnosis=DiagnosisResult(
                species=row[2],
                confidence=row[3],
                class_index=row[4],
                status=DiagnosisStatus(row[5]),
                timestamp=datetime.fromisoformat(row[8]),
                gradcam_path=row[7],
                metadata=json.loads(row[11]) if row[11] else {}
            ),
            image_path=row[6],
            timestamp=datetime.fromisoformat(row[8]),
            clinical_notes=row[9],
            sample_id=row[10]
        )
    
    def export_to_csv(self, output_path: str) -> bool:
        """Export all records to CSV file.
        
        Args:
            output_path: Path to output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import csv
            
            records = self.get_all_records()
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Patient ID', 'Species', 'Confidence', 'Status',
                    'Image Path', 'Timestamp', 'Clinical Notes', 'Sample ID'
                ])
                
                # Write records
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
            
            log_info(f"Exported {len(records)} records to {output_path}")
            return True
            
        except Exception as e:
            log_error(f"Failed to export to CSV: {str(e)}", exc_info=True)
            return False
