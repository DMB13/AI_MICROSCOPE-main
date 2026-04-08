from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClinicalRecord:
    """Represents a single clinical record."""
    id: int
    patient_id: str
    timestamp: str
    species: str
    confidence: float
    image_path: Optional[str]
    gradcam_path: Optional[str]

