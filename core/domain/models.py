#!/usr/bin/env python3
"""
Domain Models for AI Microscope Application
Pure business entities without dependencies on GUI or hardware
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class DiagnosisStatus(Enum):
    """Status of a diagnosis."""
    SUCCESS = "SUCCESS"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    ERROR = "ERROR"
    PENDING = "PENDING"


@dataclass
class DiagnosisResult:
    """Result of an AI diagnosis."""
    species: str
    confidence: float
    class_index: int
    status: DiagnosisStatus
    timestamp: datetime = field(default_factory=datetime.now)
    gradcam_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_clinically_acceptable(self, threshold: float = 0.90) -> bool:
        """Check if diagnosis meets clinical confidence threshold."""
        return self.status == DiagnosisStatus.SUCCESS and self.confidence >= threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "species": self.species,
            "confidence": self.confidence,
            "class_index": self.class_index,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "gradcam_path": self.gradcam_path,
            "metadata": self.metadata
        }


@dataclass
class PatientRecord:
    """Clinical patient record."""
    patient_id: str
    diagnosis: DiagnosisResult
    image_path: str
    timestamp: datetime = field(default_factory=datetime.now)
    clinical_notes: Optional[str] = None
    sample_id: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate patient record has required fields."""
        return bool(self.patient_id and self.diagnosis and self.image_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "patient_id": self.patient_id,
            "diagnosis": self.diagnosis.to_dict(),
            "image_path": self.image_path,
            "timestamp": self.timestamp.isoformat(),
            "clinical_notes": self.clinical_notes,
            "sample_id": self.sample_id
        }


@dataclass
class CameraInfo:
    """Information about a camera device."""
    index: int
    name: str
    is_usb: bool = False
    resolution: tuple = (1280, 720)
    fps: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "index": self.index,
            "name": self.name,
            "is_usb": self.is_usb,
            "resolution": self.resolution,
            "fps": self.fps
        }


@dataclass
class ImageAdjustments:
    """Image adjustment parameters."""
    brightness: int = 0
    contrast: int = 0
    saturation: int = 0
    sharpness: int = 0
    gamma: float = 1.0
    auto_enhance: bool = False
    
    def validate(self) -> bool:
        """Validate adjustment values are within bounds."""
        return (
            -100 <= self.brightness <= 100 and
            -100 <= self.contrast <= 100 and
            -100 <= self.saturation <= 100 and
            -100 <= self.sharpness <= 100 and
            0.1 <= self.gamma <= 3.0
        )
