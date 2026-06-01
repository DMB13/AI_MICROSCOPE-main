#!/usr/bin/env python3
"""
Usage Analytics Tracking for AI Microscope Application
Tracks application usage patterns for optimization and reporting
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

from utils.logger import log_info, log_error, log_warning


class EventType(Enum):
    """Types of events to track."""
    APP_START = "app_start"
    APP_SHUTDOWN = "app_shutdown"
    DIAGNOSIS = "diagnosis"
    CAMERA_START = "camera_start"
    CAMERA_STOP = "camera_stop"
    IMAGE_CAPTURE = "image_capture"
    IMAGE_UPLOAD = "image_upload"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"
    ERROR = "error"
    SETTINGS_CHANGE = "settings_change"


class AnalyticsEvent:
    """Represents a single analytics event."""
    
    def __init__(
        self,
        event_type: EventType,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize analytics event.
        
        Args:
            event_type: Type of event
            user_id: User ID (if authenticated)
            metadata: Additional event metadata
        """
        self.event_type = event_type
        self.user_id = user_id
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class AnalyticsTracker:
    """Tracks application usage analytics."""
    
    def __init__(self, analytics_file: Optional[Path] = None, max_events: int = 1000):
        """Initialize analytics tracker.
        
        Args:
            analytics_file: Path to analytics file (default: storage/analytics.json)
            max_events: Maximum number of events to keep
        """
        if analytics_file is None:
            base_dir = Path(__file__).resolve().parent.parent
            storage_dir = base_dir / "storage"
            storage_dir.mkdir(exist_ok=True)
            analytics_file = storage_dir / "analytics.json"
        
        self.analytics_file = Path(analytics_file)
        self.max_events = max_events
        self.events: List[AnalyticsEvent] = []
        self._load_events()
    
    def _load_events(self) -> None:
        """Load events from file."""
        try:
            if self.analytics_file.exists():
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.events = [
                    AnalyticsEvent(
                        EventType(e["event_type"]),
                        e.get("user_id"),
                        e.get("metadata")
                    )
                    for e in data
                ]
                log_info(f"Loaded {len(self.events)} analytics events")
        except Exception as e:
            log_error(f"Failed to load analytics: {str(e)}", exc_info=True)
    
    def _save_events(self) -> None:
        """Save events to file."""
        try:
            data = [event.to_dict() for event in self.events]
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log_error(f"Failed to save analytics: {str(e)}", exc_info=True)
    
    def track_event(
        self,
        event_type: EventType,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track an analytics event.
        
        Args:
            event_type: Type of event
            user_id: User ID (if authenticated)
            metadata: Additional event metadata
        """
        event = AnalyticsEvent(event_type, user_id, metadata)
        self.events.append(event)
        
        # Trim old events if over limit
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        self._save_events()
        log_info(f"Analytics event tracked: {event_type.value}")
    
    def get_event_count(
        self,
        event_type: Optional[EventType] = None,
        hours: Optional[int] = None
    ) -> int:
        """Get count of events.
        
        Args:
            event_type: Filter by event type (None for all)
            hours: Filter by last N hours (None for all time)
            
        Returns:
            Event count
        """
        filtered = self.events
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
            filtered = [
                e for e in filtered
                if datetime.fromisoformat(e.timestamp) > cutoff
            ]
        
        return len(filtered)
    
    def get_diagnosis_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get diagnosis statistics.
        
        Args:
            hours: Time window in hours
            
        Returns:
            Statistics dictionary
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        diagnosis_events = [
            e for e in self.events
            if e.event_type == EventType.DIAGNOSIS
            and datetime.fromisoformat(e.timestamp) > cutoff
        ]
        
        if not diagnosis_events:
            return {
                "total": 0,
                "avg_confidence": 0.0,
                "species_distribution": {}
            }
        
        confidences = [e.metadata.get("confidence", 0) for e in diagnosis_events]
        species_counts = {}
        for event in diagnosis_events:
            species = event.metadata.get("species", "Unknown")
            species_counts[species] = species_counts.get(species, 0) + 1
        
        return {
            "total": len(diagnosis_events),
            "avg_confidence": sum(confidences) / len(confidences),
            "species_distribution": species_counts
        }
    
    def get_user_activity(self, user_id: str, hours: int = 24) -> Dict[str, int]:
        """Get user activity statistics.
        
        Args:
            user_id: User ID
            hours: Time window in hours
            
        Returns:
            Activity counts by event type
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        user_events = [
            e for e in self.events
            if e.user_id == user_id
            and datetime.fromisoformat(e.timestamp) > cutoff
        ]
        
        activity = {}
        for event in user_events:
            activity[event.event_type.value] = activity.get(event.event_type.value, 0) + 1
        
        return activity
    
    def get_summary_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate summary report.
        
        Args:
            days: Number of days to include
            
        Returns:
            Summary report dictionary
        """
        hours = days * 24
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_events = [
            e for e in self.events
            if datetime.fromisoformat(e.timestamp) > cutoff
        ]
        
        return {
            "period_days": days,
            "total_events": len(recent_events),
            "diagnoses": self.get_event_count(EventType.DIAGNOSIS, hours),
            "images_captured": self.get_event_count(EventType.IMAGE_CAPTURE, hours),
            "images_uploaded": self.get_event_count(EventType.IMAGE_UPLOAD, hours),
            "exports": self.get_event_count(EventType.EXPORT, hours),
            "errors": self.get_event_count(EventType.ERROR, hours),
            "diagnosis_stats": self.get_diagnosis_stats(hours)
        }
