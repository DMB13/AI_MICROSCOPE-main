#!/usr/bin/env python3
"""
Audit Trail Module for AI Microscope Application
Tracks user actions for compliance and accountability
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from utils.logger import log_info, log_error


class ActionType(Enum):
    """Types of actions that can be audited."""
    # Authentication actions
    LOGIN = "login"
    LOGOUT = "logout"
    
    # Diagnosis actions
    DIAGNOSIS_RUN = "diagnosis_run"
    DIAGNOSIS_REVIEWED = "diagnosis_reviewed"
    DIAGNOSIS_VERIFIED = "diagnosis_verified"
    DIAGNOSIS_SAVED = "diagnosis_saved"
    
    # Image actions
    IMAGE_CAPTURED = "image_captured"
    IMAGE_UPLOADED = "image_uploaded"
    
    # Camera actions
    CAMERA_STARTED = "camera_started"
    CAMERA_STOPPED = "camera_stopped"
    
    # Data management
    EXPORT_PERFORMED = "export_performed"
    PATIENT_DATA_EXPORTED = "patient_data_exported"
    PATIENT_DATA_DELETED = "patient_data_deleted"
    
    # Quality control
    QUALITY_CONTROL_CHECK = "quality_control_check"
    CALIBRATION_PERFORMED = "calibration_performed"
    
    # Settings and admin
    SETTINGS_CHANGED = "settings_changed"
    USER_CREATED = "user_created"
    USER_MODIFIED = "user_modified"
    USER_DELETED = "user_deleted"


class AuditEntry:
    """Single audit log entry with medical-grade tracking."""
    
    def __init__(
        self,
        username: str,
        action: ActionType,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
        ip_address: Optional[str] = None,
        patient_id: Optional[str] = None,
        diagnosis_id: Optional[str] = None,
        verification_level: str = "single",
        requires_second_opinion: bool = False
    ):
        self.username = username
        self.action = action.value
        self.details = details or {}
        self.timestamp = timestamp or datetime.now().isoformat()
        self.ip_address = ip_address or "localhost"
        
        # Medical-specific fields
        self.patient_id = patient_id
        self.diagnosis_id = diagnosis_id
        self.verification_level = verification_level
        self.requires_second_opinion = requires_second_opinion
        
        # Generate digital signature hash for audit integrity
        self.signature_hash = self._generate_signature_hash()
    
    def _generate_signature_hash(self) -> str:
        """Generate a simple hash for audit entry integrity."""
        import hashlib
        data = f"{self.username}:{self.action}:{self.timestamp}:{self.patient_id or ''}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary."""
        return {
            "username": self.username,
            "action": self.action,
            "details": self.details,
            "timestamp": self.timestamp,
            "ip_address": self.ip_address,
            "patient_id": self.patient_id,
            "diagnosis_id": self.diagnosis_id,
            "verification_level": self.verification_level,
            "requires_second_opinion": self.requires_second_opinion,
            "signature_hash": self.signature_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEntry':
        """Create entry from dictionary."""
        return cls(
            username=data["username"],
            action=ActionType(data["action"]),
            details=data.get("details", {}),
            timestamp=data.get("timestamp"),
            ip_address=data.get("ip_address", "localhost"),
            patient_id=data.get("patient_id"),
            diagnosis_id=data.get("diagnosis_id"),
            verification_level=data.get("verification_level", "single"),
            requires_second_opinion=data.get("requires_second_opinion", False)
        )


class AuditTrail:
    """Audit trail service for tracking user actions."""
    
    def __init__(self, audit_file: Optional[Path] = None):
        """Initialize audit trail service.
        
        Args:
            audit_file: Path to audit log file (default: storage/audit_trail.json)
        """
        if audit_file is None:
            base_dir = Path(__file__).resolve().parent.parent
            storage_dir = base_dir / "storage"
            storage_dir.mkdir(exist_ok=True)
            audit_file = storage_dir / "audit_trail.json"
        
        self.audit_file = Path(audit_file)
        self.audit_log: List[AuditEntry] = []
        
        self._load_audit_log()
    
    def _load_audit_log(self) -> None:
        """Load audit log from file."""
        try:
            if self.audit_file.exists():
                with open(self.audit_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.audit_log = [AuditEntry.from_dict(entry) for entry in data]
                log_info(f"Loaded {len(self.audit_log)} audit entries")
        except Exception as e:
            log_error(f"Failed to load audit log: {str(e)}", exc_info=True)
            self.audit_log = []
    
    def _save_audit_log(self) -> None:
        """Save audit log to file."""
        try:
            data = [entry.to_dict() for entry in self.audit_log]
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            log_info("Audit log saved")
        except Exception as e:
            log_error(f"Failed to save audit log: {str(e)}", exc_info=True)
    
    def log_action(
        self,
        username: str,
        action: ActionType,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an action to the audit trail.
        
        Args:
            username: Username performing the action
            action: Type of action
            details: Additional details about the action
        """
        entry = AuditEntry(username=username, action=action, details=details)
        self.audit_log.append(entry)
        self._save_audit_log()
        log_info(f"Audit: {username} performed {action.value}")
    
    def get_audit_log(
        self,
        username: Optional[str] = None,
        action_type: Optional[ActionType] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[AuditEntry]:
        """Get filtered audit log entries.
        
        Args:
            username: Filter by username
            action_type: Filter by action type
            start_date: Filter entries after this date (ISO format)
            end_date: Filter entries before this date (ISO format)
            limit: Maximum number of entries to return
            
        Returns:
            Filtered list of audit entries
        """
        filtered = self.audit_log.copy()
        
        if username:
            filtered = [e for e in filtered if e.username == username]
        
        if action_type:
            filtered = [e for e in filtered if e.action == action_type.value]
        
        if start_date:
            filtered = [e for e in filtered if e.timestamp >= start_date]
        
        if end_date:
            filtered = [e for e in filtered if e.timestamp <= end_date]
        
        # Sort by timestamp descending (newest first)
        filtered.sort(key=lambda e: e.timestamp, reverse=True)
        
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def get_user_activity(self, username: str, limit: int = 100) -> List[AuditEntry]:
        """Get recent activity for a specific user.
        
        Args:
            username: Username
            limit: Maximum number of entries
            
        Returns:
            List of audit entries for the user
        """
        return self.get_audit_log(username=username, limit=limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit trail statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_entries = len(self.audit_log)
        unique_users = len(set(e.username for e in self.audit_log))
        
        action_counts = {}
        for entry in self.audit_log:
            action_counts[entry.action] = action_counts.get(entry.action, 0) + 1
        
        return {
            "total_entries": total_entries,
            "unique_users": unique_users,
            "action_counts": action_counts,
            "oldest_entry": self.audit_log[0].timestamp if self.audit_log else None,
            "newest_entry": self.audit_log[-1].timestamp if self.audit_log else None
        }
    
    def clear_old_entries(self, days_to_keep: int = 90) -> int:
        """Clear audit entries older than specified days.
        
        Args:
            days_to_keep: Number of days of entries to keep
            
        Returns:
            Number of entries removed
        """
        cutoff_date = (datetime.now() - datetime(days=days_to_keep)).isoformat()
        original_count = len(self.audit_log)
        
        self.audit_log = [e for e in self.audit_log if e.timestamp >= cutoff_date]
        self._save_audit_log()
        
        removed = original_count - len(self.audit_log)
        if removed > 0:
            log_info(f"Cleared {removed} old audit entries (older than {days_to_keep} days)")
        
        return removed
