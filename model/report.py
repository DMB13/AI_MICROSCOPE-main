"""Report generation utilities for AI_MICROSCOPE.

Provides CSV and PDF export helpers that can be used by the GUI
or CLI to export recent clinical records with embedded images.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
from PIL import Image
import io
import datetime

from model.db import get_db


def _make_thumbnail_bytes(path: Optional[str], size=(120, 120)) -> Optional[io.BytesIO]:
    """Create thumbnail from image path."""
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        im = Image.open(p)
        im.thumbnail(size)
        bio = io.BytesIO()
        im.save(bio, format="PNG")
        bio.seek(0)
        return bio
    except Exception:
        return None


def _get_medical_header_footer(canvas, doc, title: str = "Clinical Report"):
    """Draw medical-style header and footer on each page."""
    canvas.saveState()
    
    # Header background
    canvas.setFillColor(colors.HexColor("#1e4d8c"))
    canvas.rect(0, A4[1] - 30*mm, A4[0], 30*mm, fill=1, stroke=0)
    
    # Header text
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(20*mm, A4[1] - 18*mm, "AI MICROSCOPE - CLINICAL DIAGNOSTICS")
    canvas.setFont("Helvetica", 10)
    canvas.drawString(20*mm, A4[1] - 25*mm, title)
    
    # Header logo/icon area (right side)
    canvas.setFillColor(colors.HexColor("#ffffff"))
    canvas.circle(A4[0] - 25*mm, A4[1] - 15*mm, 8*mm, fill=0, stroke=1)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(A4[0] - 25*mm, A4[1] - 17*mm, "MUST")
    
    # Footer line
    canvas.setStrokeColor(colors.HexColor("#1e4d8c"))
    canvas.setLineWidth(2)
    canvas.line(20*mm, 15*mm, A4[0] - 20*mm, 15*mm)
    
    # Footer text
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(20*mm, 10*mm, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} | Page {canvas.getPageNumber()}")
    canvas.drawRightString(A4[0] - 20*mm, 10*mm, "Mbeya University Of Science And Technology (MUST)")
    
    canvas.restoreState()


def export_records_pdf(
    records: List[Dict[str, Any]], 
    out_path: str, 
    title: str = "Clinical Records Report",
    period_info: Optional[str] = None,
    summary_stats: Optional[Dict] = None
) -> Path:
    """Export given records to a professionally formatted medical PDF.

    Args:
        records: list of record dicts
        out_path: output PDF path
        title: document title
        period_info: Optional string describing the time period (e.g., "2024-01-01 to 2024-01-31")
        summary_stats: Optional dict with summary statistics

    Returns:
        Path to generated PDF
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Use letter size with comfortable margins
    doc = SimpleDocTemplate(
        str(out), 
        pagesize=letter, 
        rightMargin=20*mm, 
        leftMargin=20*mm, 
        topMargin=40*mm,  # Space for header
        bottomMargin=25*mm  # Space for footer
    )
    
    styles = getSampleStyleSheet()
    
    # Custom medical styles
    title_style = ParagraphStyle(
        name="MedicalTitle", 
        parent=styles["Title"], 
        fontSize=22, 
        leading=28, 
        alignment=1,
        textColor=colors.HexColor("#1e4d8c"),
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        name="MedicalSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#555555"),
        spaceAfter=15
    )
    
    section_header = ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1e4d8c"),
        spaceBefore=15,
        spaceAfter=10,
        borderColor=colors.HexColor("#1e4d8c"),
        borderWidth=1,
        borderPadding=5
    )
    
    table_header_style = ParagraphStyle(
        name="TableHeader", 
        parent=styles["Normal"], 
        fontSize=9, 
        leading=11, 
        alignment=1, 
        textColor=colors.white,
        fontName="Helvetica-Bold"
    )
    
    normal_cell_style = ParagraphStyle(
        name="NormalCell",
        parent=styles["Normal"],
        fontSize=8,
        leading=10
    )
    
    stats_style = ParagraphStyle(
        name="StatsStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#333333")
    )

    story = []

    # Main Title
    story.append(Paragraph(title, title_style))
    
    # Subtitle with period info
    if period_info:
        story.append(Paragraph(f"<i>Report Period: {period_info}</i>", subtitle_style))
    else:
        story.append(Paragraph(f"<i>Generated: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}</i>", subtitle_style))
    
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1e4d8c")))
    story.append(Spacer(1, 15))

    # Summary Statistics Section
    if summary_stats:
        story.append(Paragraph("SUMMARY STATISTICS", section_header))
        
        # Calculate default average confidence if not provided
        avg_conf = summary_stats.get('avg_confidence')
        if avg_conf is None:
            confidences = [r.get('confidence') for r in records if isinstance(r.get('confidence'), (int, float))]
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
        
        stats_data = [
            ["Metric", "Value"],
            ["Total Records", str(summary_stats.get('total_records', len(records)))],
            ["Unique Patients", str(summary_stats.get('unique_patients', len(set(r.get('patient_id') for r in records if r.get('patient_id')))))],
            ["Average Confidence", f"{avg_conf:.2%}"],
            ["Species Identified", str(summary_stats.get('unique_species', len(set(r.get('species') for r in records if r.get('species')))))]
        ]
        
        stats_table = Table(stats_data, colWidths=[60*mm, 60*mm])
        stats_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e4d8c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f5f5f5")),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))

    # Detailed Records Section
    if records:
        story.append(Paragraph("DETAILED RECORDS", section_header))
        story.append(Spacer(1, 5))

        # Table header
        table_data = [[
            Paragraph("ID", table_header_style),
            Paragraph("Patient ID", table_header_style),
            Paragraph("Date/Time", table_header_style),
            Paragraph("Species", table_header_style),
            Paragraph("Confidence", table_header_style),
            Paragraph("Image", table_header_style),
            Paragraph("Heatmap", table_header_style)
        ]]

        # Calculate column widths to fit within margins (letter width ~216mm, margins 40mm total)
        usable_width = 216*mm - 40*mm  # ~176mm
        col_widths = [
            12*mm,   # ID
            28*mm,   # Patient ID
            35*mm,   # Date/Time
            38*mm,   # Species
            20*mm,   # Confidence
            28*mm,   # Image
            28*mm    # Heatmap
        ]

        for r in records:
            img_thumb = _make_thumbnail_bytes(r.get("image_path"), size=(80, 80))
            gc_thumb = _make_thumbnail_bytes(r.get("gradcam_path"), size=(80, 80))

            img_cell = RLImage(img_thumb, width=25*mm, height=25*mm) if img_thumb is not None else Paragraph("N/A", normal_cell_style)
            gc_cell = RLImage(gc_thumb, width=25*mm, height=25*mm) if gc_thumb is not None else Paragraph("N/A", normal_cell_style)

            confidence = r.get("confidence")
            if isinstance(confidence, float):
                # Color code confidence
                if confidence >= 0.90:
                    conf_display = f"<font color='green'>{confidence:.1%}</font>"
                elif confidence >= 0.70:
                    conf_display = f"<font color='orange'>{confidence:.1%}</font>"
                else:
                    conf_display = f"<font color='red'>{confidence:.1%}</font>"
            else:
                conf_display = str(confidence) if confidence is not None else "N/A"

            # Format timestamp nicely
            timestamp = r.get("timestamp", "")
            try:
                if isinstance(timestamp, str) and len(timestamp) > 10:
                    dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime("%m/%d/%y %H:%M")
            except Exception:
                pass

            row = [
                Paragraph(str(r.get("id", "")), normal_cell_style),
                Paragraph(r.get("patient_id", "") or "N/A", normal_cell_style),
                Paragraph(timestamp, normal_cell_style),
                Paragraph(r.get("species", "") or "N/A", normal_cell_style),
                Paragraph(conf_display, normal_cell_style),
                img_cell,
                gc_cell
            ]
            table_data.append(row)

        records_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        records_table.setStyle(TableStyle([
            # Header styling
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e4d8c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            # Body styling
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            # Alternating row colors for readability
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#f9f9f9")),
            ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#f9f9f9")),
            ("BACKGROUND", (0, 6), (-1, 6), colors.HexColor("#f9f9f9")),
            ("BACKGROUND", (0, 8), (-1, 8), colors.HexColor("#f9f9f9")),
            # Grid and alignment
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (4, -1), "LEFT"),
            ("ALIGN", (4, 1), (4, -1), "CENTER"),
            # Padding for comfortable reading
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        story.append(records_table)
    else:
        story.append(Paragraph("No records found for the selected period.", stats_style))

    # Build the PDF with header/footer on each page
    def draw_header_footer(canvas, doc):
        _get_medical_header_footer(canvas, doc, title)

    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    return out


def export_recent_pdf(db=None, out_path: str = "exports/clinical_export.pdf", limit: int = 100) -> Path:
    """Export recent records to PDF."""
    if db is None:
        db = get_db()
    records = db.get_recent(limit)
    return export_records_pdf(records, out_path)


def export_by_date_range(
    start_date: datetime.date,
    end_date: datetime.date,
    out_path: str,
    db=None
) -> Path:
    """Export records within a date range.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        out_path: Output PDF path
        db: Database instance (optional)
    
    Returns:
        Path to generated PDF
    """
    if db is None:
        db = get_db()
    
    # Get all records and filter by date
    all_records = db.get_all_records()
    filtered_records = []
    
    for r in all_records:
        try:
            ts = r.get("timestamp", "")
            if isinstance(ts, str):
                record_date = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00')).date()
            elif isinstance(ts, datetime.datetime):
                record_date = ts.date()
            else:
                continue
            
            if start_date <= record_date <= end_date:
                filtered_records.append(r)
        except Exception:
            continue
    
    period_info = f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
    
    # Calculate summary statistics
    summary_stats = {
        'total_records': len(filtered_records),
        'unique_patients': len(set(r.get('patient_id') for r in filtered_records if r.get('patient_id'))),
        'unique_species': len(set(r.get('species') for r in filtered_records if r.get('species')))
    }
    
    confidences = [r.get('confidence') for r in filtered_records if isinstance(r.get('confidence'), (int, float))]
    if confidences:
        summary_stats['avg_confidence'] = sum(confidences) / len(confidences)
    
    return export_records_pdf(
        filtered_records, 
        out_path, 
        title="Clinical Records Report",
        period_info=period_info,
        summary_stats=summary_stats
    )


def export_daily_report(date: datetime.date, out_path: str, db=None) -> Path:
    """Export records for a single day."""
    return export_by_date_range(date, date, out_path, db)


def export_weekly_report(year: int, week: int, out_path: str, db=None) -> Path:
    """Export records for a specific week."""
    import calendar
    
    # Get the first day of the year
    first_day = datetime.date(year, 1, 1)
    
    # Find the first day of the specified week
    # ISO weeks start on Monday
    start_date = datetime.date(year, 1, 1) + datetime.timedelta(weeks=week-1, days=-datetime.date(year, 1, 1).weekday())
    end_date = start_date + datetime.timedelta(days=6)
    
    period_info = f"Week {week}, {year} ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"
    
    if db is None:
        db = get_db()
    
    all_records = db.get_all_records()
    filtered_records = []
    
    for r in all_records:
        try:
            ts = r.get("timestamp", "")
            if isinstance(ts, str):
                record_date = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00')).date()
            elif isinstance(ts, datetime.datetime):
                record_date = ts.date()
            else:
                continue
            
            if start_date <= record_date <= end_date:
                filtered_records.append(r)
        except Exception:
            continue
    
    summary_stats = {
        'total_records': len(filtered_records),
        'unique_patients': len(set(r.get('patient_id') for r in filtered_records if r.get('patient_id'))),
        'unique_species': len(set(r.get('species') for r in filtered_records if r.get('species')))
    }
    
    confidences = [r.get('confidence') for r in filtered_records if isinstance(r.get('confidence'), (int, float))]
    if confidences:
        summary_stats['avg_confidence'] = sum(confidences) / len(confidences)
    
    return export_records_pdf(
        filtered_records, 
        out_path, 
        title="Weekly Clinical Report",
        period_info=period_info,
        summary_stats=summary_stats
    )


def export_monthly_report(year: int, month: int, out_path: str, db=None) -> Path:
    """Export records for a specific month."""
    import calendar
    
    # Get the last day of the month
    _, last_day = calendar.monthrange(year, month)
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, last_day)
    
    month_name = calendar.month_name[month]
    period_info = f"{month_name} {year}"
    
    if db is None:
        db = get_db()
    
    all_records = db.get_all_records()
    filtered_records = []
    
    for r in all_records:
        try:
            ts = r.get("timestamp", "")
            if isinstance(ts, str):
                record_date = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00')).date()
            elif isinstance(ts, datetime.datetime):
                record_date = ts.date()
            else:
                continue
            
            if start_date <= record_date <= end_date:
                filtered_records.append(r)
        except Exception:
            continue
    
    summary_stats = {
        'total_records': len(filtered_records),
        'unique_patients': len(set(r.get('patient_id') for r in filtered_records if r.get('patient_id'))),
        'unique_species': len(set(r.get('species') for r in filtered_records if r.get('species')))
    }
    
    confidences = [r.get('confidence') for r in filtered_records if isinstance(r.get('confidence'), (int, float))]
    if confidences:
        summary_stats['avg_confidence'] = sum(confidences) / len(confidences)
    
    return export_records_pdf(
        filtered_records, 
        out_path, 
        title="Monthly Clinical Report",
        period_info=period_info,
        summary_stats=summary_stats
    )
