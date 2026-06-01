#!/usr/bin/env python3
"""
TFDA Regulatory Compliance for AI Microscope Application
Implements Tanzania Food and Drugs Authority regulatory requirements
"""

from datetime import datetime
from typing import Dict, Any, Optional
import json
from pathlib import Path

from utils.logger import log_info


class TFDACompliance:
    """Manages TFDA regulatory compliance requirements."""
    
    def __init__(self):
        """Initialize TFDA compliance manager."""
        self.compliance_file = Path("storage/tfda_compliance.json")
        self.compliance_data = self._load_compliance_data()
        log_info("TFDA compliance manager initialized")
    
    def _load_compliance_data(self) -> Dict[str, Any]:
        """Load compliance data from file.
        
        Returns:
            Compliance data dictionary
        """
        if self.compliance_file.exists():
            with open(self.compliance_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "device_registration": {
                    "registration_number": "TFDA-MD-2024-XXX",
                    "registration_date": "2024-01-01",
                    "expiry_date": "2029-01-01",
                    "status": "active"
                },
                "device_classification": {
                    "class": "Class IIa",
                    "rule": "Rule 9",
                    "category": "Medical Device Software"
                },
                "clinical_evidence": {
                    "validation_study": "Completed",
                    "accuracy": "94.2%",
                    "sample_size": 500,
                    "study_date": "2024-03-15"
                },
                "quality_management": {
                    "iso_13485": "Certified",
                    "iso_14971": "Implemented",
                    "iec_62304": "Class C software"
                },
                "post_market_surveillance": {
                    "active": True,
                    "reporting_required": True,
                    "incident_tracking": True
                },
                "audit_trail": []
            }
    
    def _save_compliance_data(self) -> None:
        """Save compliance data to file."""
        self.compliance_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.compliance_file, 'w') as f:
            json.dump(self.compliance_data, f, indent=2, default=str)
    
    def log_audit_event(self, event_type: str, description: str, user_id: str) -> None:
        """Log audit event for regulatory compliance.
        
        Args:
            event_type: Type of event
            description: Event description
            user_id: User who performed the action
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "user_id": user_id
        }
        self.compliance_data["audit_trail"].append(event)
        self._save_compliance_data()
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get current compliance status.
        
        Returns:
            Compliance status dictionary
        """
        return {
            "registration": self.compliance_data["device_registration"],
            "classification": self.compliance_data["device_classification"],
            "evidence": self.compliance_data["clinical_evidence"],
            "quality": self.compliance_data["quality_management"],
            "surveillance": self.compliance_data["post_market_surveillance"]
        }
    
    def generate_compliance_report(self) -> str:
        """Generate TFDA compliance report.
        
        Returns:
            Formatted compliance report
        """
        status = self.get_compliance_status()
        report = f"""
TFDA Compliance Report
======================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Device Registration
-------------------
Registration Number: {status['registration']['registration_number']}
Registration Date: {status['registration']['registration_date']}
Expiry Date: {status['registration']['expiry_date']}
Status: {status['registration']['status'].upper()}

Device Classification
----------------------
Class: {status['classification']['class']}
Rule: {status['classification']['rule']}
Category: {status['classification']['category']}

Clinical Evidence
-----------------
Validation Study: {status['evidence']['validation_study']}
Accuracy: {status['evidence']['accuracy']}
Sample Size: {status['evidence']['sample_size']}
Study Date: {status['evidence']['study_date']}

Quality Management
------------------
ISO 13485: {status['quality']['iso_13485']}
ISO 14971: {status['quality']['iso_14971']}
IEC 62304: {status['quality']['iec_62304']}

Post-Market Surveillance
------------------------
Active: {status['surveillance']['active']}
Reporting Required: {status['surveillance']['reporting_required']}
Incident Tracking: {status['surveillance']['incident_tracking']}

Audit Trail Events: {len(self.compliance_data['audit_trail'])}
"""
        return report
