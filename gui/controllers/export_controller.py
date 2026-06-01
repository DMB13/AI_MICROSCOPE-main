#!/usr/bin/env python3
"""
Export Controller for AI Microscope
Manages export operations and bridges GUI with storage layer
"""

from typing import Optional, Callable
from pathlib import Path
import datetime
from tkinter import filedialog, messagebox

from storage.repository import PatientRecordRepository
from storage.export import ExportService
from utils.logger import log_info, log_error


class ExportController:
    """Controller for export operations."""
    
    def __init__(
        self,
        repository: Optional[PatientRecordRepository] = None,
        export_service: Optional[ExportService] = None,
        settings_manager=None
    ):
        """Initialize export controller.
        
        Args:
            repository: PatientRecordRepository instance
            export_service: ExportService instance
            settings_manager: SettingsManager instance for export directory
        """
        self.repository = repository or PatientRecordRepository()
        self.export_service = export_service or ExportService(self.repository)
        self.settings_manager = settings_manager
        self.on_export_complete: Optional[Callable] = None
        self.on_export_error: Optional[Callable] = None
    
    def export_to_csv(self, output_path: Optional[str] = None) -> Optional[str]:
        """Export all records to CSV.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to exported file or None if failed
        """
        try:
            log_info("Starting CSV export")
            result = self.export_service.export_to_csv(output_path)
            
            if result:
                log_info(f"CSV export successful: {result}")
                if self.on_export_complete:
                    self.on_export_complete(result, "CSV")
                return result
            else:
                log_error("CSV export failed")
                if self.on_export_error:
                    self.on_export_error("CSV export failed")
                return None
                
        except Exception as e:
            log_error(f"CSV export error: {str(e)}", exc_info=True)
            if self.on_export_error:
                self.on_export_error(str(e))
            return None
    
    def export_to_json(self, output_path: Optional[str] = None) -> Optional[str]:
        """Export all records to JSON.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to exported file or None if failed
        """
        try:
            log_info("Starting JSON export")
            result = self.export_service.export_to_json(output_path)
            
            if result:
                log_info(f"JSON export successful: {result}")
                if self.on_export_complete:
                    self.on_export_complete(result, "JSON")
                return result
            else:
                log_error("JSON export failed")
                if self.on_export_error:
                    self.on_export_error("JSON export failed")
                return None
                
        except Exception as e:
            log_error(f"JSON export error: {str(e)}", exc_info=True)
            if self.on_export_error:
                self.on_export_error(str(e))
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
            log_info(f"Starting patient CSV export for {patient_id}")
            result = self.export_service.export_patient_to_csv(patient_id, output_path)
            
            if result:
                log_info(f"Patient CSV export successful: {result}")
                if self.on_export_complete:
                    self.on_export_complete(result, "Patient CSV")
                return result
            else:
                log_error("Patient CSV export failed")
                if self.on_export_error:
                    self.on_export_error("Patient CSV export failed")
                return None
                
        except Exception as e:
            log_error(f"Patient CSV export error: {str(e)}", exc_info=True)
            if self.on_export_error:
                self.on_export_error(str(e))
            return None
    
    def get_record_count(self) -> int:
        """Get total number of records.
        
        Returns:
            Number of records in database
        """
        try:
            records = self.repository.get_all_records()
            return len(records)
        except Exception as e:
            log_error(f"Failed to get record count: {str(e)}")
            return 0
    
    def set_export_complete_callback(self, callback: Callable) -> None:
        """Set callback for when export completes.
        
        Args:
            callback: Function to call with export path and format
        """
        self.on_export_complete = callback
    
    def export_all_records(self, parent_window=None) -> Optional[str]:
        """Export all records with user dialog for format, time period, filename and location.
        
        Args:
            parent_window: Parent window for the export dialog
            
        Returns:
            Path to exported file or None if failed
        """
        try:
            from model.db import get_db
            from model import report as report_utils
            from gui.components.export_dialog import ExportDialog
            import datetime
            
            db = get_db()
            
            # Get default export directory
            default_dir = None
            try:
                if self.settings_manager:
                    default_dir = self.settings_manager.get_export_directory()
                else:
                    from config.constants import EXPORT_DIR
                    default_dir = EXPORT_DIR
            except Exception:
                default_dir = Path.home() / "Documents"
            
            result = {"path": None, "format": None, "period_options": None}
            
            def on_export_confirmed(format_type: str, filepath: str, period_options: dict):
                result["path"] = filepath
                result["format"] = format_type
                result["period_options"] = period_options
            
            # Show export dialog
            dialog = ExportDialog(
                parent=parent_window,
                default_dir=default_dir,
                on_export=on_export_confirmed
            )
            
            # Wait for dialog to close
            parent_window.wait_window(dialog)
            
            if not result["path"] or not result["format"]:
                return None
            
            save_path = result["path"]
            format_type = result["format"]
            period_options = result["period_options"] or {"type": "all"}
            
            # Perform export based on selected format and period
            try:
                if format_type == "PDF":
                    # Use period-aware PDF export
                    self._export_pdf_with_period(save_path, period_options, db)
                    messagebox.showinfo("Export Successful", f"PDF report exported to:\n{save_path}")
                    log_info(f"PDF export successful: {save_path}")
                    if self.on_export_complete:
                        self.on_export_complete(save_path, "PDF")
                    return save_path
                    
                elif format_type == "JSON":
                    # Filter by period if needed
                    records = self._get_records_by_period(period_options, db)
                    if records:
                        self.export_service.export_to_json(save_path)
                    else:
                        messagebox.showwarning("No Records", "No records found for the selected period.")
                        return None
                    messagebox.showinfo("Export Successful", f"JSON data exported to:\n{save_path}")
                    log_info(f"JSON export successful: {save_path}")
                    if self.on_export_complete:
                        self.on_export_complete(save_path, "JSON")
                    return save_path
                    
                else:  # CSV
                    # Filter by period if needed
                    records = self._get_records_by_period(period_options, db)
                    if records:
                        db.export_csv(save_path)
                    else:
                        messagebox.showwarning("No Records", "No records found for the selected period.")
                        return None
                    messagebox.showinfo("Export Successful", f"CSV records exported to:\n{save_path}")
                    log_info(f"CSV export successful: {save_path}")
                    if self.on_export_complete:
                        self.on_export_complete(save_path, "CSV")
                    return save_path
                    
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export {format_type}:\n{str(e)}")
                log_error(f"{format_type} export failed: {str(e)}", exc_info=True)
                if self.on_export_error:
                    self.on_export_error(str(e))
                return None
                
        except Exception as e:
            log_error(f"Export all records error: {str(e)}", exc_info=True)
            if self.on_export_error:
                self.on_export_error(str(e))
            return None
    
    def _get_records_by_period(self, period_options: dict, db=None) -> list:
        """Get records filtered by period options."""
        if db is None:
            from model.db import get_db
            db = get_db()
        
        period_type = period_options.get("type", "all")
        
        if period_type == "all":
            return db.get_all_records()
        
        elif period_type == "daily":
            date_str = period_options.get("date")
            if date_str:
                date = datetime.datetime.fromisoformat(date_str).date()
                return self._filter_records_by_date_range(db, date, date)
        
        elif period_type == "range":
            start_str = period_options.get("start_date")
            end_str = period_options.get("end_date")
            if start_str and end_str:
                start_date = datetime.datetime.fromisoformat(start_str).date()
                end_date = datetime.datetime.fromisoformat(end_str).date()
                return self._filter_records_by_date_range(db, start_date, end_date)
        
        return db.get_all_records()
    
    def _filter_records_by_date_range(self, db, start_date: datetime.date, end_date: datetime.date) -> list:
        """Filter records by date range."""
        all_records = db.get_all_records()
        filtered = []
        
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
                    filtered.append(r)
            except Exception:
                continue
        
        return filtered
    
    def _export_pdf_with_period(self, save_path: str, period_options: dict, db=None):
        """Export PDF with period filtering."""
        from model import report as report_utils
        import datetime
        
        if db is None:
            from model.db import get_db
            db = get_db()
        
        period_type = period_options.get("type", "all")
        
        if period_type == "daily":
            date_str = period_options.get("date")
            if date_str:
                date = datetime.datetime.fromisoformat(date_str).date()
                return report_utils.export_daily_report(date, save_path, db)
        
        elif period_type == "range":
            start_str = period_options.get("start_date")
            end_str = period_options.get("end_date")
            if start_str and end_str:
                start_date = datetime.datetime.fromisoformat(start_str).date()
                end_date = datetime.datetime.fromisoformat(end_str).date()
                return report_utils.export_by_date_range(start_date, end_date, save_path, db)
        
        # Default: export recent
        return report_utils.export_recent_pdf(db=db, out_path=save_path)
    
    def export_csv(self):
        """Export clinical records to CSV with timestamp."""
        try:
            from model.db import get_db
            db = get_db()
            csv_path = f"clinical_records_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            exported = db.export_csv(csv_path)
            if exported:
                messagebox.showinfo("Export Successful", f"Records exported to:\n{exported}")
                log_info(f"CSV export successful: {exported}")
                if self.on_export_complete:
                    self.on_export_complete(exported, "CSV")
                return exported
            else:
                messagebox.showerror("Export Failed", "Could not export records.")
                log_error("CSV export failed: no records exported")
                if self.on_export_error:
                    self.on_export_error("Could not export records")
                return None
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")
            log_error(f"CSV export error: {str(e)}", exc_info=True)
            if self.on_export_error:
                self.on_export_error(str(e))
            return None
    
    def set_export_error_callback(self, callback: Callable) -> None:
        """Set callback for when export fails.
        
        Args:
            callback: Function to call with error message
        """
        self.on_export_error = callback
