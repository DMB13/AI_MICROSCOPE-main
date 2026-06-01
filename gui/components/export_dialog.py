#!/usr/bin/env python3
"""
Export Dialog for AI Microscope
Provides a user-friendly interface for selecting export format, filename, directory, and time period
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import datetime


class ExportDialog(ctk.CTkToplevel):
    """Export dialog for choosing format, filename, directory, and time period."""
    
    EXPORT_FORMATS = {
        "CSV": {"ext": ".csv", "desc": "CSV (Comma Separated Values)"},
        "PDF": {"ext": ".pdf", "desc": "PDF Report (with images)"},
        "JSON": {"ext": ".json", "desc": "JSON (Structured Data)"}
    }
    
    PERIOD_TYPES = {
        "all": "All Records",
        "today": "Today",
        "week": "This Week",
        "month": "This Month",
        "custom": "Custom Date Range"
    }
    
    def __init__(
        self,
        parent,
        default_dir: Optional[Path] = None,
        on_export: Optional[Callable[[str, str, Dict[str, Any]], None]] = None,
        on_cancel: Optional[Callable] = None
    ):
        """Initialize export dialog.
        
        Args:
            parent: Parent window
            default_dir: Default export directory
            on_export: Callback when export is confirmed (format, filepath, period_options)
            on_cancel: Callback when dialog is cancelled
        """
        super().__init__(parent)
        
        self.default_dir = default_dir or Path.home() / "Documents"
        self.on_export = on_export
        self.on_cancel = on_cancel
        self.selected_path: Optional[str] = None
        self.selected_format: str = "PDF"  # Default to PDF for better reports
        self.period_options: Dict[str, Any] = {"type": "all"}
        
        self.title("DMB AI Microscope - Export Reports")
        self.geometry("550x650")
        self.resizable(False, False)
        
        # Set window icon
        try:
            from pathlib import Path
            icon_path = Path(__file__).resolve().parent.parent.parent / "logo.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        # Center dialog on parent
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # Set default values
        self._update_filename()
        self._update_preview()
        self._on_period_change()
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        # Create scrollable frame for all content
        scroll_frame = ctk.CTkScrollableFrame(self, width=510, height=580)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            scroll_frame,
            text="📤 Export Clinical Reports",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(10, 5))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            scroll_frame,
            text="Select format, time period, filename, and destination",
            font=ctk.CTkFont(size=13)
        )
        subtitle.pack(pady=(0, 15))
        
        # ===== TIME PERIOD SECTION =====
        period_frame = ctk.CTkFrame(scroll_frame)
        period_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(
            period_frame,
            text="📅 Time Period",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1e4d8c"
        ).pack(anchor="w", padx=12, pady=(12, 8))
        
        # Period type dropdown
        self.period_var = ctk.StringVar(value="all")
        
        period_row = ctk.CTkFrame(period_frame, fg_color="transparent")
        period_row.pack(fill="x", padx=12, pady=5)
        
        ctk.CTkLabel(period_row, text="Select Period:", font=ctk.CTkFont(size=11)).pack(side="left")
        
        self.period_dropdown = ctk.CTkOptionMenu(
            period_row,
            values=list(self.PERIOD_TYPES.values()),
            command=self._on_period_dropdown_change,
            width=200
        )
        self.period_dropdown.pack(side="right", padx=(10, 0))
        # Map display values to keys
        self._period_display_to_key = {v: k for k, v in self.PERIOD_TYPES.items()}
        
        # Custom date range frame (hidden by default)
        self.custom_date_frame = ctk.CTkFrame(period_frame)
        
        ctk.CTkLabel(self.custom_date_frame, text="Start Date (YYYY-MM-DD):", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=12, pady=(10, 2))
        self.start_date_entry = ctk.CTkEntry(self.custom_date_frame, placeholder_text="2024-01-01")
        self.start_date_entry.pack(fill="x", padx=12, pady=2)
        
        ctk.CTkLabel(self.custom_date_frame, text="End Date (YYYY-MM-DD):", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=12, pady=(8, 2))
        self.end_date_entry = ctk.CTkEntry(self.custom_date_frame, placeholder_text="2024-12-31")
        self.end_date_entry.pack(fill="x", padx=12, pady=2)
        
        # Quick buttons for common periods
        quick_frame = ctk.CTkFrame(period_frame, fg_color="transparent")
        quick_frame.pack(fill="x", padx=12, pady=(10, 8))
        
        ctk.CTkLabel(quick_frame, text="Quick Select:", font=ctk.CTkFont(size=10)).pack(side="left")
        
        today_btn = ctk.CTkButton(quick_frame, text="Today", width=60, height=24, font=ctk.CTkFont(size=9), command=lambda: self._set_quick_period("today"))
        today_btn.pack(side="left", padx=(8, 4))
        
        week_btn = ctk.CTkButton(quick_frame, text="This Week", width=70, height=24, font=ctk.CTkFont(size=9), command=lambda: self._set_quick_period("week"))
        week_btn.pack(side="left", padx=4)
        
        month_btn = ctk.CTkButton(quick_frame, text="This Month", width=75, height=24, font=ctk.CTkFont(size=9), command=lambda: self._set_quick_period("month"))
        month_btn.pack(side="left", padx=4)
        
        # Export button after selecting time period
        export_btn_frame = ctk.CTkFrame(period_frame, fg_color="transparent")
        export_btn_frame.pack(fill="x", padx=12, pady=(15, 10))
        
        self.export_period_btn = ctk.CTkButton(
            export_btn_frame,
            text="📤 Export Records",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1e4d8c",
            hover_color="#2a5aa0",
            height=40,
            command=self._on_export
        )
        self.export_period_btn.pack(fill="x")
        
        # ===== FORMAT SECTION =====
        format_frame = ctk.CTkFrame(scroll_frame)
        format_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(
            format_frame,
            text="📄 Export Format",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1e4d8c"
        ).pack(anchor="w", padx=12, pady=(12, 8))
        
        self.format_var = ctk.StringVar(value="PDF")
        
        for format_key, format_info in self.EXPORT_FORMATS.items():
            radio = ctk.CTkRadioButton(
                format_frame,
                text=format_info["desc"],
                variable=self.format_var,
                value=format_key,
                command=self._on_format_change
            )
            radio.pack(anchor="w", padx=25, pady=4)
        
        # ===== FILENAME SECTION =====
        filename_frame = ctk.CTkFrame(scroll_frame)
        filename_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(
            filename_frame,
            text="💾 Filename",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1e4d8c"
        ).pack(anchor="w", padx=12, pady=(12, 8))
        
        self.filename_entry = ctk.CTkEntry(
            filename_frame,
            placeholder_text="Enter filename"
        )
        self.filename_entry.pack(fill="x", padx=12, pady=5)
        self.filename_entry.bind("<KeyRelease>", lambda e: self._update_preview())
        
        # ===== DIRECTORY SECTION =====
        dir_frame = ctk.CTkFrame(scroll_frame)
        dir_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(
            dir_frame,
            text="📁 Save Location",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1e4d8c"
        ).pack(anchor="w", padx=12, pady=(12, 8))
        
        dir_row = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_row.pack(fill="x", padx=12, pady=5)
        
        self.dir_entry = ctk.CTkEntry(
            dir_row,
            placeholder_text="Select directory"
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.dir_entry.insert(0, str(self.default_dir))
        
        browse_btn = ctk.CTkButton(
            dir_row,
            text="Browse",
            width=80,
            command=self._browse_directory
        )
        browse_btn.pack(side="right")
        
        # ===== PREVIEW SECTION =====
        preview_frame = ctk.CTkFrame(scroll_frame)
        preview_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(
            preview_frame,
            text="👁️ Preview",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1e4d8c"
        ).pack(anchor="w", padx=12, pady=(12, 5))
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="",
            font=ctk.CTkFont(size=12),
            wraplength=460
        )
        self.preview_label.pack(anchor="w", padx=12, pady=(0, 12))
        
        # Error message (below scroll frame)
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=13)
        )
        self.error_label.pack(pady=5)
        
        # Buttons (below scroll frame)
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            fg_color="gray",
            hover_color="darkgray",
            command=self._on_cancel
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        export_btn = ctk.CTkButton(
            button_frame,
            text="Export Report",
            width=120,
            fg_color="green",
            hover_color="darkgreen",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_export
        )
        export_btn.pack(side="right")
    
    def _on_format_change(self) -> None:
        """Handle format selection change."""
        self.selected_format = self.format_var.get()
        self._update_filename()
        self._update_preview()
    
    def _on_period_dropdown_change(self, selected_value: str) -> None:
        """Handle period type dropdown change."""
        period_key = self._period_display_to_key.get(selected_value, "all")
        self.period_var.set(period_key)
        self._on_period_change()
    
    def _on_period_change(self) -> None:
        """Handle period type change - show/hide custom date fields."""
        period_type = self.period_var.get()
        
        if period_type == "custom":
            self.custom_date_frame.pack(fill="x", padx=12, pady=5, after=self.period_dropdown.master)
        else:
            self.custom_date_frame.pack_forget()
        
        # Update period options
        today = datetime.date.today()
        
        if period_type == "today":
            self.period_options = {
                "type": "daily",
                "date": today.isoformat()
            }
        elif period_type == "week":
            # Get current week
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            self.period_options = {
                "type": "range",
                "start_date": start_of_week.isoformat(),
                "end_date": end_of_week.isoformat()
            }
        elif period_type == "month":
            # Get current month
            start_of_month = today.replace(day=1)
            import calendar
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_of_month = today.replace(day=last_day)
            self.period_options = {
                "type": "range",
                "start_date": start_of_month.isoformat(),
                "end_date": end_of_month.isoformat()
            }
        elif period_type == "custom":
            self.period_options = {"type": "custom"}
        else:  # all
            self.period_options = {"type": "all"}
        
        self._update_preview()
    
    def _set_quick_period(self, period: str) -> None:
        """Set period via quick select buttons."""
        display_value = self.PERIOD_TYPES.get(period, "All Records")
        self.period_dropdown.set(display_value)
        self.period_var.set(period)
        self._on_period_change()
        
        # If custom, set default dates
        if period == "custom":
            today = datetime.date.today()
            self.start_date_entry.delete(0, "end")
            self.start_date_entry.insert(0, today.isoformat())
            self.end_date_entry.delete(0, "end")
            self.end_date_entry.insert(0, today.isoformat())
    
    def _validate_custom_dates(self) -> bool:
        """Validate custom date range."""
        try:
            start_str = self.start_date_entry.get().strip()
            end_str = self.end_date_entry.get().strip()
            
            if not start_str or not end_str:
                self.error_label.configure(text="Please enter both start and end dates")
                return False
            
            start_date = datetime.date.fromisoformat(start_str)
            end_date = datetime.date.fromisoformat(end_str)
            
            if end_date < start_date:
                self.error_label.configure(text="End date must be after start date")
                return False
            
            self.period_options = {
                "type": "range",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            return True
        except ValueError:
            self.error_label.configure(text="Invalid date format. Use YYYY-MM-DD")
            return False
    
    def _update_filename(self) -> None:
        """Update filename based on selected format."""
        current_name = self.filename_entry.get().strip()
        format_ext = self.EXPORT_FORMATS[self.selected_format]["ext"]
        
        # If filename is empty or has different extension, set default
        if not current_name:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename_entry.delete(0, "end")
            self.filename_entry.insert(0, f"clinical_export_{timestamp}{format_ext}")
        else:
            # Replace extension
            base_name = Path(current_name).stem
            self.filename_entry.delete(0, "end")
            self.filename_entry.insert(0, f"{base_name}{format_ext}")
    
    def _update_preview(self) -> None:
        """Update the full path preview with period info."""
        directory = self.dir_entry.get().strip()
        filename = self.filename_entry.get().strip()
        
        lines = []
        
        # Period info
        period_type = self.period_var.get()
        period_desc = self.PERIOD_TYPES.get(period_type, "All Records")
        lines.append(f"📅 Period: {period_desc}")
        
        if period_type == "custom" and self.period_options.get("type") == "range":
            lines.append(f"   From: {self.period_options.get('start_date', 'N/A')} To: {self.period_options.get('end_date', 'N/A')}")
        
        # Format
        lines.append(f"📄 Format: {self.format_var.get()}")
        
        # Path
        if directory and filename:
            full_path = Path(directory) / filename
            lines.append(f"💾 Save to: {full_path}")
        else:
            lines.append("💾 Save to: [Please enter directory and filename]")
        
        self.preview_label.configure(text="\n".join(lines))
    
    def _browse_directory(self) -> None:
        """Open directory browser dialog."""
        current_dir = self.dir_entry.get().strip()
        if not current_dir or not Path(current_dir).exists():
            current_dir = str(self.default_dir)
        
        selected_dir = filedialog.askdirectory(
            title="Select Export Directory",
            initialdir=current_dir
        )
        
        if selected_dir:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, selected_dir)
            self._update_preview()
    
    def _on_export(self) -> None:
        """Handle export button click."""
        directory = self.dir_entry.get().strip()
        filename = self.filename_entry.get().strip()
        format_type = self.format_var.get()
        
        # Validation
        if not directory:
            self.error_label.configure(text="Please select a directory")
            return
        
        if not filename:
            self.error_label.configure(text="Please enter a filename")
            return
        
        # Handle custom date validation if needed
        if self.period_var.get() == "custom":
            if not self._validate_custom_dates():
                return
        
        # Ensure directory exists
        dir_path = Path(directory)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.error_label.configure(text=f"Cannot create directory: {str(e)}")
                return
        
        # Ensure correct extension
        expected_ext = self.EXPORT_FORMATS[format_type]["ext"]
        if not filename.lower().endswith(expected_ext.lower()):
            filename += expected_ext
        
        # Check if file exists
        full_path = dir_path / filename
        if full_path.exists():
            overwrite = messagebox.askyesno(
                "File Exists",
                f"'{filename}' already exists.\nDo you want to overwrite it?"
            )
            if not overwrite:
                return
        
        self.selected_path = str(full_path)
        self.selected_format = format_type
        
        if self.on_export:
            self.on_export(format_type, self.selected_path, self.period_options)
        
        self.destroy()
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        if self.on_cancel:
            self.on_cancel()
        self.destroy()
    
    def get_selected_path(self) -> Optional[str]:
        """Get the selected export path."""
        return self.selected_path
    
    def get_selected_format(self) -> str:
        """Get the selected export format."""
        return self.selected_format
    
    def get_period_options(self) -> Dict[str, Any]:
        """Get the selected period options."""
        return self.period_options
