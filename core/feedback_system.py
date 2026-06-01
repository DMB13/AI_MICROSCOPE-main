#!/usr/bin/env python3
"""
Feedback System for AI Microscope Application
Handles flagging and tracking of incorrect predictions for model improvement
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from utils.logger import log_info, log_error, log_warning


class FeedbackType(Enum):
    """Types of feedback for predictions."""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    UNCERTAIN = "uncertain"
    LOW_CONFIDENCE = "low_confidence"


class FeedbackEntry:
    """Represents a single feedback entry."""
    
    def __init__(
        self,
        image_path: str,
        predicted_species: str,
        predicted_confidence: float,
        feedback_type: FeedbackType,
        correct_species: Optional[str] = None,
        user_id: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """Initialize feedback entry.
        
        Args:
            image_path: Path to the image
            predicted_species: Model's predicted species
            predicted_confidence: Model's confidence score
            feedback_type: Type of feedback
            correct_species: Correct species (if incorrect)
            user_id: User providing feedback
            notes: Additional notes
        """
        self.image_path = image_path
        self.predicted_species = predicted_species
        self.predicted_confidence = predicted_confidence
        self.feedback_type = feedback_type
        self.correct_species = correct_species
        self.user_id = user_id
        self.notes = notes
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "image_path": self.image_path,
            "predicted_species": self.predicted_species,
            "predicted_confidence": self.predicted_confidence,
            "feedback_type": self.feedback_type.value,
            "correct_species": self.correct_species,
            "user_id": self.user_id,
            "notes": self.notes,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeedbackEntry':
        """Create from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            FeedbackEntry instance
        """
        return cls(
            image_path=data["image_path"],
            predicted_species=data["predicted_species"],
            predicted_confidence=data["predicted_confidence"],
            feedback_type=FeedbackType(data["feedback_type"]),
            correct_species=data.get("correct_species"),
            user_id=data.get("user_id"),
            notes=data.get("notes")
        )


class FeedbackSystem:
    """System for collecting and managing feedback on predictions."""
    
    def __init__(self, feedback_file: Optional[Path] = None):
        """Initialize feedback system.
        
        Args:
            feedback_file: Path to feedback file (default: storage/feedback.json)
        """
        if feedback_file is None:
            base_dir = Path(__file__).resolve().parent.parent
            storage_dir = base_dir / "storage"
            storage_dir.mkdir(exist_ok=True)
            feedback_file = storage_dir / "feedback.json"
        
        self.feedback_file = Path(feedback_file)
        self.feedback_entries: List[FeedbackEntry] = []
        self._load_feedback()
    
    def _load_feedback(self) -> None:
        """Load feedback from file."""
        try:
            if self.feedback_file.exists():
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.feedback_entries = [
                    FeedbackEntry.from_dict(entry) for entry in data
                ]
                log_info(f"Loaded {len(self.feedback_entries)} feedback entries")
        except Exception as e:
            log_error(f"Failed to load feedback: {str(e)}", exc_info=True)
    
    def _save_feedback(self) -> None:
        """Save feedback to file."""
        try:
            data = [entry.to_dict() for entry in self.feedback_entries]
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log_error(f"Failed to save feedback: {str(e)}", exc_info=True)
    
    def add_feedback(
        self,
        image_path: str,
        predicted_species: str,
        predicted_confidence: float,
        feedback_type: FeedbackType,
        correct_species: Optional[str] = None,
        user_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> None:
        """Add feedback entry.
        
        Args:
            image_path: Path to the image
            predicted_species: Model's predicted species
            predicted_confidence: Model's confidence score
            feedback_type: Type of feedback
            correct_species: Correct species (if incorrect)
            user_id: User providing feedback
            notes: Additional notes
        """
        entry = FeedbackEntry(
            image_path=image_path,
            predicted_species=predicted_species,
            predicted_confidence=predicted_confidence,
            feedback_type=feedback_type,
            correct_species=correct_species,
            user_id=user_id,
            notes=notes
        )
        self.feedback_entries.append(entry)
        self._save_feedback()
        log_info(f"Feedback added: {feedback_type.value} for {predicted_species}")
    
    def get_incorrect_predictions(self) -> List[FeedbackEntry]:
        """Get all incorrect predictions.
        
        Returns:
            List of incorrect prediction entries
        """
        return [
            entry for entry in self.feedback_entries
            if entry.feedback_type == FeedbackType.INCORRECT
        ]
    
    def get_low_confidence_predictions(self, threshold: float = 0.7) -> List[FeedbackEntry]:
        """Get low confidence predictions.
        
        Args:
            threshold: Confidence threshold
            
        Returns:
            List of low confidence entries
        """
        return [
            entry for entry in self.feedback_entries
            if entry.predicted_confidence < threshold
        ]
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics.
        
        Returns:
            Statistics dictionary
        """
        total = len(self.feedback_entries)
        if total == 0:
            return {
                "total": 0,
                "correct": 0,
                "incorrect": 0,
                "uncertain": 0,
                "accuracy": 0.0
            }
        
        correct = sum(1 for e in self.feedback_entries if e.feedback_type == FeedbackType.CORRECT)
        incorrect = sum(1 for e in self.feedback_entries if e.feedback_type == FeedbackType.INCORRECT)
        uncertain = sum(1 for e in self.feedback_entries if e.feedback_type == FeedbackType.UNCERTAIN)
        
        return {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "uncertain": uncertain,
            "accuracy": correct / (correct + incorrect) if (correct + incorrect) > 0 else 0.0
        }
    
    def export_for_retraining(self, output_file: Path) -> None:
        """Export incorrect predictions for model retraining.
        
        Args:
            output_file: Path to output file
        """
        incorrect = self.get_incorrect_predictions()
        
        try:
            data = [entry.to_dict() for entry in incorrect]
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            log_info(f"Exported {len(incorrect)} incorrect predictions to {output_file}")
        except Exception as e:
            log_error(f"Failed to export for retraining: {str(e)}", exc_info=True)
