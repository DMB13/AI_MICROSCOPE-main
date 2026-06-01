#!/usr/bin/env python3
"""
PDF Report Generation for AI Microscope Application
Generates professional clinical diagnosis reports
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.platypus import PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from utils.logger import log_info


class PDFReportGenerator:
    """Generates PDF clinical reports."""
    
    def __init__(self):
        """Initialize PDF report generator."""
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()
    
    def _add_custom_styles(self) -> None:
        """Add custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='Header',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='Body',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10
        ))
    
    def generate_report(
        self,
        output_path: str,
        diagnosis_data: Dict[str, Any],
        image_path: Optional[str] = None
    ) -> None:
        """Generate PDF report.
        
        Args:
            output_path: Output PDF file path
            diagnosis_data: Diagnosis information
            image_path: Optional image to include
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Header
        story.append(Paragraph("AI Microscope - Clinical Diagnosis Report", self.styles['Header']))
        story.append(Spacer(1, 0.2*inch))
        
        # Facility Information
        facility_data = [
            ["Facility:", diagnosis_data.get("facility", "Not specified")],
            ["Report Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Report ID:", diagnosis_data.get("report_id", "N/A")]
        ]
        
        facility_table = Table(facility_data, colWidths=[1.5*inch, 4*inch])
        facility_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(facility_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information
        story.append(Paragraph("Patient Information", self.styles['SubHeader']))
        
        patient_data = [
            ["Patient ID:", diagnosis_data.get("patient_id", "N/A")],
            ["Patient Name:", diagnosis_data.get("patient_name", "N/A")],
            ["Age:", str(diagnosis_data.get("age", "N/A"))],
            ["Sex:", diagnosis_data.get("sex", "N/A")]
        ]
        
        patient_table = Table(patient_data, colWidths=[1.5*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Diagnosis Results
        story.append(Paragraph("Diagnosis Results", self.styles['SubHeader']))
        
        diagnosis_result = [
            ["Predicted Species:", diagnosis_data.get("species", "N/A")],
            ["Confidence:", f"{diagnosis_data.get('confidence', 0):.2%}"],
            ["Status:", "RELIABLE" if diagnosis_data.get("confidence", 0) >= 0.9 else "REQUIRES REVIEW"]
        ]
        
        diagnosis_table = Table(diagnosis_result, colWidths=[1.5*inch, 4*inch])
        diagnosis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(diagnosis_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add image if provided
        if image_path and Path(image_path).exists():
            try:
                story.append(Paragraph("Microscopy Image", self.styles['SubHeader']))
                img = Image(image_path, width=4*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                log_warning(f"Could not include image in report: {str(e)}")
        
        # Notes
        if diagnosis_data.get("notes"):
            story.append(Paragraph("Notes", self.styles['SubHeader']))
            story.append(Paragraph(diagnosis_data["notes"], self.styles['Body']))
            story.append(Spacer(1, 0.2*inch))
        
        # Disclaimer
        story.append(PageBreak())
        story.append(Paragraph("Disclaimer", self.styles['SubHeader']))
        disclaimer = (
            "This report was generated by an AI-powered diagnostic system. "
            "The results should be reviewed by a qualified medical professional "
            "before making clinical decisions. The system provides assistance "
            "but does not replace professional medical judgment."
        )
        story.append(Paragraph(disclaimer, self.styles['Body']))
        
        # Build PDF
        doc.build(story)
        log_info(f"PDF report generated: {output_path}")
