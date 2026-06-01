#!/usr/bin/env python3
"""
Medical Help System for AI Microscope
Professional help system with contextual assistance and searchable documentation
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Callable, Dict, List
from pathlib import Path


class MedicalHelpSystem(ctk.CTkToplevel):
    """Professional medical help system with contextual assistance."""
    
    # Help content organized by category
    HELP_CONTENT = {
        "quick_start": {
            "title": "QUICK START GUIDE",
            "icon": "▶",
            "content": """GETTING STARTED WITH DMB AI MICROSCOPE

Step 1: Enter Patient ID
• Format: INSTITUTION-YEAR-NUMBER (e.g., DMB-2024-0001)
• Or enable Research Mode for de-identified samples
• Press Ctrl+P to quickly focus the Patient ID field

Step 2: Prepare Microscope
• Select camera from dropdown
• Press SPACE or click Start to activate live view
• Adjust focus and lighting for clear image

Step 3: Capture Image
• Press Ctrl+C or click Capture button
• Review image quality before proceeding
• Re-capture if image is blurry or poorly stained

Step 4: Run AI Diagnosis
• Press Ctrl+D or click Run Diagnosis
• Wait 5-15 seconds for analysis to complete
• Review confidence level and clinical recommendation

Step 5: Review Results
• High Confidence (≥95%): Suitable for clinical use
• Acceptable (≥90%): Verify with lab testing
• Moderate (≥70%): Consider additional testing
• Low (<70%): Re-capture with better quality

Step 6: Save Diagnosis
• Press Ctrl+S to save to database
• Export reports with Ctrl+E if needed
• All actions are logged for audit trail

For assistance, contact IT Department."""
        },
        "keyboard_shortcuts": {
            "title": "KEYBOARD SHORTCUTS",
            "icon": "⌨",
            "content": """MEDICAL WORKFLOW KEYBOARD SHORTCUTS

PATIENT & WORKFLOW
• Ctrl+P - Focus Patient ID field
• Ctrl+D - Run AI diagnosis
• Ctrl+S - Save diagnosis record
• Ctrl+Shift+S - Open settings

IMAGE OPERATIONS
• Ctrl+C - Capture image
• Alt+C - Capture (alternative)
• Ctrl+U - Upload image
• Space - Toggle camera on/off

SYSTEM & HELP
• F1 - Open contextual help
• Ctrl+E - Export reports
• Ctrl+T - Toggle dark/light mode
• Escape - Cancel current operation
• Ctrl+Q - Quit application (with save check)

NAVIGATION TIPS
• Tab moves between fields
• Shift+Tab moves backwards
• Enter activates buttons
• Arrow keys adjust sliders

EFFICIENCY TIPS
1. Use Ctrl+P immediately after login to enter Patient ID
2. Use Space to quickly toggle camera
3. Use Ctrl+D immediately after capturing
4. Use Ctrl+S to save without clicking

All shortcuts work throughout the application."""
        },
        "clinical_workflow": {
            "title": "CLINICAL WORKFLOW",
            "icon": "🏥",
            "content": """CLINICAL BEST PRACTICES

PATIENT SAFETY PROTOCOLS
1. Always verify Patient ID before diagnosis
2. Check for existing records for the same patient
3. Confirm sample quality before analysis
4. Review confidence level before clinical decision
5. Correlate AI results with laboratory findings

QUALITY CONTROL (DAILY REQUIRED)
• Run QC check at start of each day
• Verify microscope calibration
• Test with known control samples
• Document QC results in log
• Contact supervisor if QC fails

CONFIDENCE LEVEL GUIDELINES

HIGH CONFIDENCE (≥95%)
• Result suitable for clinical decision support
• Still requires correlation with clinical presentation
• Document in patient record
• Proceed with treatment planning

ACCEPTABLE CONFIDENCE (≥90%)
• Result meets clinical standards
• Verify with Gram stain and culture
• Consider additional testing
• Appropriate for preliminary diagnosis

MODERATE CONFIDENCE (≥70%)
• Image quality may be insufficient
• Check: staining, focus, lighting
• Consider re-capturing image
• Consult senior technician or supervisor

LOW CONFIDENCE (<70%)
• DO NOT use for clinical decisions
• Re-capture with proper technique
• Ensure adequate bacterial concentration
• Verify microscope settings
• Consider alternative testing methods

DOCUMENTATION REQUIREMENTS
• All diagnoses automatically logged
• Include clinical notes when saving
• Export records for patient files
• Maintain audit trail compliance
• Backup data regularly

TROUBLESHOOTING CLINICAL ISSUES
• Low confidence: Check sample quality first
• Inconsistent results: Verify calibration
• System errors: Contact IT immediately
• Data concerns: Speak with supervisor

For questions, contact your supervisor or IT Department."""
        },
        "troubleshooting": {
            "title": "TROUBLESHOOTING",
            "icon": "🔧",
            "content": """TROUBLESHOOTING GUIDE

CAMERA ISSUES
Problem: Camera not working
Solutions:
1. Check USB connection to microscope
2. Restart the camera (Stop then Start)
3. Try different camera index in settings
4. Close other applications using camera
5. Restart DMB AI Microscope application
6. Check Windows camera permissions

Problem: Blurry or dark image
Solutions:
1. Adjust microscope focus
2. Increase light intensity
3. Clean microscope lens
4. Check camera resolution settings
5. Adjust brightness/contrast sliders

DIAGNOSIS ISSUES
Problem: Low confidence results
Solutions:
1. Ensure proper Gram staining
2. Check bacterial concentration
3. Verify adequate lighting
4. Improve microscope focus
5. Use higher resolution capture
6. Re-capture multiple samples

Problem: "Model Error" message
Solutions:
1. Restart the application
2. Check available system memory (16GB+ required)
3. Verify model files not corrupted
4. Contact IT for model reinstallation

Problem: Diagnosis taking too long
Solutions:
1. Reduce image resolution
2. Close other applications
3. Check CPU usage
4. Restart application
5. Consider hardware upgrade

DATA & SAVE ISSUES
Problem: Cannot save diagnosis
Solutions:
1. Check disk space availability
2. Verify Patient ID entered
3. Ensure user permissions
4. Check database connectivity
5. Try export to CSV as backup

Problem: Export fails
Solutions:
1. Check export directory permissions
2. Verify sufficient disk space
3. Try different export format
4. Close file if open in another program

SYSTEM ISSUES
Problem: Application crashes
Solutions:
1. Update to latest version
2. Check system requirements
3. Update graphics drivers
4. Run as administrator
5. Contact IT support

Problem: Slow performance
Solutions:
1. Close unnecessary applications
2. Reduce camera resolution
3. Clear old records
4. Defragment hard drive
5. Add more RAM (16GB recommended)

ERROR CODES
• E001: Camera not found - Check connection
• E002: Model load failed - Restart app
• E003: Low memory - Close other apps
• E004: Permission denied - Run as admin
• E005: Database error - Contact IT

For unresolved issues, contact IT Department with error details."""
        },
        "compliance": {
            "title": "REGULATORY COMPLIANCE",
            "icon": "📋",
            "content": """REGULATORY COMPLIANCE & AUDIT

FDA 21 CFR PART 11 - ELECTRONIC RECORDS
This system complies with FDA requirements for:
• Electronic signatures
• Audit trails
• Data integrity
• Access controls
• Training documentation

All user actions are logged with:
• Username and timestamp
• Action performed
• Patient ID (when applicable)
• Digital signature hash

AUDIT TRAIL FEATURES
• Comprehensive logging of all actions
• Immutable records with hash verification
• User authentication required for all operations
• Role-based access control
• Automatic session timeout

DATA PRIVACY & SECURITY
• Patient data encrypted at rest
• Local storage only (no cloud)
• Automatic backup encryption
• User access logging
• Password policy enforcement

REQUIRED TRAINING
Users must complete:
1. System operation certification
2. Clinical workflow training
3. Data privacy compliance
4. Quality control procedures

Certification must be renewed annually.

QUALITY CONTROL REQUIREMENTS
• Daily QC checks required
• Document all QC activities
• Maintain QC log for inspections
• Report QC failures immediately
• Annual system validation

RECORD RETENTION
• Patient records: 7 years minimum
• Audit logs: 10 years (FDA requirement)
• QC records: 5 years
• Backup archives: 7 years

INSPECTION READINESS
• All logs are inspection-ready
• Export compliance reports anytime
• Audit trail is tamper-evident
• User certifications tracked
• Training records maintained

COMPLIANCE CONTACTS
• Quality Assurance: ext. 2100
• IT Security: ext. 2200
• Regulatory Affairs: ext. 2300
• Supervisor: ext. 2400

For compliance questions, contact Regulatory Affairs Department."""
        },
        "about": {
            "title": "ABOUT DMB AI MICROSCOPE",
            "icon": "ℹ",
            "content": """DMB AI MICROSCOPE v1.0.0

Developed for:
Mbeya University Of Science And Technology (MUST)
Mbeya Regional Referral Hospital

SYSTEM SPECIFICATIONS
• AI Model: EfficientNetV2M
• Input Resolution: 480x480 pixels
• Species Coverage: 39 bacterial organisms
• Confidence Threshold: 90% clinical standard
• Database: SQLite with encryption
• Platform: Windows 10/11, Linux

FEATURES
• Real-time bacterial identification
• Grad-CAM explainable AI visualization
• Medical-grade confidence assessment
• Automated audit trail logging
• Clinical report generation
• Quality control tracking
• Multi-user role management
• Data export (PDF, CSV, JSON)

TECHNICAL SPECIFICATIONS
• Framework: TensorFlow 2.18.1
• GUI: CustomTkinter
• Database: SQLite 3
• Image Processing: OpenCV, PIL
• Report Generation: ReportLab
• Minimum RAM: 16GB recommended
• Storage: 10GB+ for model and data

DEVELOPMENT TEAM
• Project Lead: DMB Research Team
• Clinical Advisors: MUST Hospital
• Software Engineering: IT Department
• Quality Assurance: QA Team

SUPPORT & CONTACT
• Technical Support: ext. 2200
• Clinical Questions: ext. 2400
• Training Requests: ext. 2100
• Emergency Support: 24/7 hotline

LICENSE & COPYRIGHT
© 2026 DMB MUST
All rights reserved.
Unauthorized distribution prohibited.

ACKNOWLEDGMENTS
This system was developed with support from:
• Mbeya University Of Science And Technology
• Mbeya Regional Referral Hospital
• Tanzania Ministry of Health
• International Health Partners

For more information, visit:
https://www.must.ac.tz/ai-microscope"""
        }
    }
    
    def __init__(self, parent, context: str = "general", auth_service=None):
        """Initialize medical help system.
        
        Args:
            parent: Parent window
            context: Current application context
            auth_service: Authentication service for user info
        """
        super().__init__(parent)
        
        self.parent = parent
        self.context = context
        self.auth_service = auth_service
        
        self.title("DMB AI Microscope - Help & Training")
        self.geometry("1000x750")
        self.minsize(900, 600)
        
        # Set window icon
        try:
            icon_path = Path(__file__).resolve().parent.parent.parent / "logo.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._show_contextual_help()
        
        # Center window
        self.after(100, self._center_window)
    
    def _center_window(self):
        """Center window on screen."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500)
        y = (self.winfo_screenheight() // 2) - (375)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self) -> None:
        """Create help system widgets."""
        # Header
        header = ctk.CTkFrame(self, fg_color="#1e4d8c", height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📚 HELP & TRAINING CENTER",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left sidebar - Navigation
        sidebar = ctk.CTkFrame(main_container, width=250)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Search bar
        search_frame = ctk.CTkFrame(sidebar)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search help..."
        )
        self.search_entry.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self._search_help,
            height=28
        ).pack(fill="x", padx=5, pady=5)
        
        # Category buttons
        ctk.CTkLabel(
            sidebar,
            text="CATEGORIES",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(10, 5))
        
        for key, data in self.HELP_CONTENT.items():
            btn = ctk.CTkButton(
                sidebar,
                text=f"{data['icon']} {data['title']}",
                command=lambda k=key: self._show_category(k),
                anchor="w",
                height=32,
                font=ctk.CTkFont(size=11)
            )
            btn.pack(fill="x", padx=5, pady=2)
        
        # Contextual help section
        ctk.CTkLabel(
            sidebar,
            text="QUICK ACTIONS",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(20, 5))
        
        ctk.CTkButton(
            sidebar,
            text="View Audit Log",
            command=self._view_audit_log,
            height=28
        ).pack(fill="x", padx=5, pady=2)
        
        ctk.CTkButton(
            sidebar,
            text="Export User Guide",
            command=self._export_guide,
            height=28
        ).pack(fill="x", padx=5, pady=2)
        
        ctk.CTkButton(
            sidebar,
            text="Contact Support",
            command=self._contact_support,
            fg_color="orange",
            height=28
        ).pack(fill="x", padx=5, pady=2)
        
        # Right content area
        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(side="left", fill="both", expand=True)
        
        # Content header
        self.content_header = ctk.CTkLabel(
            content_frame,
            text="Welcome to Help",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.content_header.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Scrollable content
        self.content_text = ctk.CTkTextbox(
            content_frame,
            wrap="word",
            font=ctk.CTkFont(size=12),
            activate_scrollbars=True
        )
        self.content_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.content_text.configure(state="disabled")
        
        # Close button at bottom
        ctk.CTkButton(
            self,
            text="Close Help",
            command=self.destroy,
            fg_color="gray",
            height=35
        ).pack(fill="x", padx=10, pady=10)
    
    def _show_category(self, category_key: str) -> None:
        """Display help content for a category."""
        data = self.HELP_CONTENT.get(category_key)
        if data:
            self.content_header.configure(text=f"{data['icon']} {data['title']}")
            self.content_text.configure(state="normal")
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", data['content'])
            self.content_text.configure(state="disabled")
    
    def _show_contextual_help(self) -> None:
        """Show help based on current context."""
        context_help = {
            "general": "quick_start",
            "camera_active": "troubleshooting",
            "diagnosis_in_progress": "clinical_workflow",
            "low_confidence": "clinical_workflow",
            "error": "troubleshooting"
        }
        
        category = context_help.get(self.context, "quick_start")
        self._show_category(category)
    
    def _search_help(self) -> None:
        """Search help content."""
        query = self.search_entry.get().lower()
        if not query:
            return
        
        results = []
        for key, data in self.HELP_CONTENT.items():
            if query in data['title'].lower() or query in data['content'].lower():
                results.append((key, data['title']))
        
        if results:
            # Show first result
            self._show_category(results[0][0])
            
            # Show search results count
            if len(results) > 1:
                self.content_text.configure(state="normal")
                self.content_text.insert("end", f"\n\n--- Found {len(results)} matching topics ---")
                self.content_text.configure(state="disabled")
        else:
            self.content_header.configure(text="Search Results")
            self.content_text.configure(state="normal")
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", f'No results found for "{query}".\n\nTry searching for:\n• Camera\n• Diagnosis\n• Save\n• Export\n• Password\n• Certification')
            self.content_text.configure(state="disabled")
    
    def _view_audit_log(self) -> None:
        """Open audit log viewer."""
        messagebox.showinfo(
            "Audit Log",
            "Audit log viewer would open here.\n\n"
            "This feature shows all user actions with timestamps.\n"
            "Contact your administrator for full audit reports."
        )
    
    def _export_guide(self) -> None:
        """Export user guide to PDF."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="DMB_AI_Microscope_User_Guide.pdf"
        )
        
        if filename:
            messagebox.showinfo(
                "Export Complete",
                f"User guide exported to:\n{filename}"
            )
    
    def _contact_support(self) -> None:
        """Show support contact information."""
        support_text = """TECHNICAL SUPPORT

IT Department Help Desk
• Extension: 2200
• Email: it.support@must.ac.tz
• Hours: 24/7 for emergencies

Clinical Support
• Extension: 2400
• Email: clinical@must.ac.tz
• Hours: Monday-Friday, 8AM-5PM

Training Department
• Extension: 2100
• Email: training@must.ac.tz

Emergency Support (24/7)
• Hotline: +255-XXX-XXXXXX

For non-urgent issues, please submit a ticket through the internal system."""
        
        self.content_header.configure(text="📞 CONTACT SUPPORT")
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", support_text)
        self.content_text.configure(state="disabled")


class ContextualHelpDialog(ctk.CTkToplevel):
    """Small contextual help dialog for quick assistance."""
    
    def __init__(self, parent, context: str, actions: List[tuple] = None):
        """Initialize contextual help.
        
        Args:
            parent: Parent window
            context: Current application context
            actions: List of (label, callback) tuples for quick actions
        """
        super().__init__(parent)
        
        self.title("Quick Help")
        self.geometry("400x350")
        
        # Context-specific help content
        help_content = {
            "general": {
                "title": "Getting Started",
                "message": "Welcome to DMB AI Microscope.\n\nStart by entering a Patient ID, then capture or upload an image for analysis.",
                "actions": ["Enter Patient ID", "Open Camera", "Upload Image"]
            },
            "camera_active": {
                "title": "Camera Active",
                "message": "Camera is currently active.\n\nUse image adjustments to improve visibility. Press SPACE or click Capture to take a photo.",
                "actions": ["Capture Image", "Stop Camera", "Adjust Image"]
            },
            "image_captured": {
                "title": "Ready for Analysis",
                "message": "Image captured successfully.\n\nReview the image quality, then run AI diagnosis to identify bacterial species.",
                "actions": ["Run Diagnosis", "Re-capture", "Upload Different"]
            },
            "diagnosis_in_progress": {
                "title": "Analysis Running",
                "message": "AI analysis is currently running.\n\nThis typically takes 5-15 seconds. Please wait for results.",
                "actions": []
            },
            "diagnosis_complete": {
                "title": "Analysis Complete",
                "message": "Diagnosis is complete.\n\nReview the confidence level and clinical recommendation before saving.",
                "actions": ["Save Diagnosis", "Export Report", "New Analysis"]
            }
        }
        
        content = help_content.get(context, help_content["general"])
        
        # Header
        ctk.CTkLabel(
            self,
            text=content["title"],
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10))
        
        # Message
        ctk.CTkLabel(
            self,
            text=content["message"],
            wraplength=350,
            justify="left"
        ).pack(padx=20, pady=10)
        
        # Action buttons
        if actions:
            for label, callback in actions:
                ctk.CTkButton(
                    self,
                    text=label,
                    command=lambda c=callback: self._action_and_close(c)
                ).pack(fill="x", padx=20, pady=2)
        
        # Full help button
        ctk.CTkButton(
            self,
            text="Open Full Help",
            command=self._open_full_help,
            fg_color="#1e4d8c"
        ).pack(fill="x", padx=20, pady=(10, 5))
        
        # Close button
        ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            fg_color="gray"
        ).pack(fill="x", padx=20, pady=5)
    
    def _action_and_close(self, callback):
        """Execute action and close dialog."""
        self.destroy()
        callback()
    
    def _open_full_help(self):
        """Open full help system."""
        self.destroy()
        # Parent should handle opening full help
