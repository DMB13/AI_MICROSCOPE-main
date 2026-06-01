#!/usr/bin/env python3
"""
User Profile Dialog for AI Microscope
Medical-grade user profile management with certification tracking
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Callable


class UserProfileDialog(ctk.CTkToplevel):
    """User profile management with medical certification tracking."""
    
    def __init__(self, parent, auth_service, on_password_changed: Optional[Callable] = None):
        """Initialize user profile dialog.
        
        Args:
            parent: Parent window
            auth_service: Authentication service instance
            on_password_changed: Callback when password is changed
        """
        super().__init__(parent)
        
        self.auth_service = auth_service
        self.on_password_changed = on_password_changed
        self.user = auth_service.current_user
        
        if not self.user:
            messagebox.showerror("Error", "No user logged in")
            self.destroy()
            return
        
        self.title("DMB AI Microscope - My Profile")
        self.geometry("520x700")
        self.resizable(False, False)
        
        # Set window icon
        try:
            from pathlib import Path
            icon_path = Path(__file__).resolve().parent.parent.parent / "logo.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        # Header with user info
        header = ctk.CTkFrame(self, fg_color="#1e4d8c")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header, 
            text=self.user.full_name or self.user.username,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            header,
            text=f"Role: {self.user.role.value.title()}",
            text_color="white"
        ).pack()
        
        if self.user.department:
            ctk.CTkLabel(
                header,
                text=f"Department: {self.user.department}",
                text_color="white"
            ).pack(pady=(0, 10))
        else:
            header.pack(pady=(0, 10))
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(self, height=500)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Certification Status Section
        cert_frame = ctk.CTkFrame(scroll_frame)
        cert_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            cert_frame, 
            text="CERTIFICATION STATUS",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Status indicator
        status_colors = {
            "certified": ("green", "✓ Certified"),
            "pending": ("orange", "⏳ Pending"),
            "expired": ("red", "✗ Expired"),
        }
        color, display_text = status_colors.get(
            self.user.certification_status, 
            ("gray", self.user.certification_status)
        )
        
        status_label = ctk.CTkLabel(
            cert_frame,
            text=display_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=color
        )
        status_label.pack()
        
        if self.user.certification_date:
            ctk.CTkLabel(
                cert_frame,
                text=f"Certified: {self.user.certification_date[:10]}",
                font=ctk.CTkFont(size=12)
            ).pack()
        
        if self.user.certification_expiry:
            expiry_text = f"Expires: {self.user.certification_expiry[:10]}"
            ctk.CTkLabel(cert_frame, text=expiry_text, font=ctk.CTkFont(size=12)).pack()
        
        if not self.user.is_certified():
            warning_text = (
                "Your certification has expired or is pending.\n"
                "Please complete required training before using the system."
            )
            ctk.CTkLabel(
                cert_frame,
                text=warning_text,
                font=ctk.CTkFont(size=12),
                text_color="red",
                wraplength=400
            ).pack(pady=5)
            
            if self.user.certification_status == "expired":
                ctk.CTkButton(
                    cert_frame,
                    text="Request Recertification",
                    fg_color="orange",
                    command=self._request_recertification
                ).pack(pady=10)
        
        # Account Information Section
        info_frame = ctk.CTkFrame(scroll_frame)
        info_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            info_frame,
            text="ACCOUNT INFORMATION",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        info_grid = ctk.CTkFrame(info_frame)
        info_grid.pack(fill="x", padx=10, pady=5)
        
        # Username
        ctk.CTkLabel(info_grid, text="Username:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", pady=2)
        ctk.CTkLabel(info_grid, text=self.user.username).grid(row=0, column=1, sticky="w", padx=10, pady=2)
        
        # Email
        ctk.CTkLabel(info_grid, text="Email:", font=ctk.CTkFont(size=13)).grid(row=1, column=0, sticky="w", pady=2)
        ctk.CTkLabel(info_grid, text=self.user.email or "Not set").grid(row=1, column=1, sticky="w", padx=10, pady=2)
        
        # Employee ID
        ctk.CTkLabel(info_grid, text="Employee ID:", font=ctk.CTkFont(size=13)).grid(row=2, column=0, sticky="w", pady=2)
        ctk.CTkLabel(info_grid, text=self.user.employee_id or "Not set").grid(row=2, column=1, sticky="w", padx=10, pady=2)
        
        # Last login
        ctk.CTkLabel(info_grid, text="Last Login:", font=ctk.CTkFont(size=13)).grid(row=3, column=0, sticky="w", pady=2)
        last_login = self.user.last_login[:16].replace("T", " ") if self.user.last_login else "Never"
        ctk.CTkLabel(info_grid, text=last_login).grid(row=3, column=1, sticky="w", padx=10, pady=2)
        
        # Session timeout
        ctk.CTkLabel(info_grid, text="Session Timeout:", font=ctk.CTkFont(size=13)).grid(row=4, column=0, sticky="w", pady=2)
        ctk.CTkLabel(info_grid, text=f"{self.user.session_timeout_minutes} minutes").grid(row=4, column=1, sticky="w", padx=10, pady=2)
        
        # Security Section
        security_frame = ctk.CTkFrame(scroll_frame)
        security_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            security_frame,
            text="SECURITY",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Password age warning
        if self.user.requires_password_change():
            ctk.CTkLabel(
                security_frame,
                text="⚠ Password change required (over 90 days old)",
                font=ctk.CTkFont(size=13),
                text_color="orange"
            ).pack(pady=5)
        
        ctk.CTkButton(
            security_frame,
            text="Change Password",
            command=self._show_change_password_dialog
        ).pack(fill="x", padx=10, pady=5)
        
        # Recent Activity Section
        activity_frame = ctk.CTkFrame(scroll_frame)
        activity_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            activity_frame,
            text="RECENT ACTIVITY",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            activity_frame,
            text="Activity tracking is available in the Audit Log",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=5)
        
        # Permissions Section
        perm_frame = ctk.CTkFrame(scroll_frame)
        perm_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            perm_frame,
            text="PERMISSIONS",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        permissions = {
            "diagnosis": "Run AI Diagnosis",
            "view_records": "View Patient Records",
            "capture_image": "Capture Images",
            "export_reports": "Export Reports",
            "review_diagnoses": "Review Diagnoses"
        }
        
        for op, label in permissions.items():
            has_perm = self.user.can_perform_operation(op)
            color = "green" if has_perm else "gray"
            symbol = "✓" if has_perm else "✗"
            ctk.CTkLabel(
                perm_frame,
                text=f"{symbol} {label}",
                font=ctk.CTkFont(size=12),
                text_color=color
            ).pack(anchor="w", padx=20, pady=1)
        
        # Close button
        ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            fg_color="gray"
        ).pack(fill="x", padx=10, pady=10)
    
    def _request_recertification(self) -> None:
        """Request recertification."""
        messagebox.showinfo(
            "Recertification Request",
            "Your request for recertification has been submitted to your supervisor.\n\n"
            "You will be notified when your certification is renewed."
        )
    
    def _show_change_password_dialog(self) -> None:
        """Show password change dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Password")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="Change Password",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10))
        
        # Password policy note
        policy_text = (
            "Password must:\n"
            "• Be at least 12 characters\n"
            "• Include uppercase and lowercase\n"
            "• Include at least one number\n"
            "• Include at least one special character\n"
            "• Not be a common password"
        )
        ctk.CTkLabel(
            dialog,
            text=policy_text,
            font=ctk.CTkFont(size=9),
            text_color="gray"
        ).pack(pady=(0, 10))
        
        # Current password
        ctk.CTkLabel(dialog, text="Current Password:").pack(anchor="w", padx=20, pady=(10, 0))
        current_entry = ctk.CTkEntry(dialog, show="*")
        current_entry.pack(fill="x", padx=20, pady=5)
        
        # New password
        ctk.CTkLabel(dialog, text="New Password:").pack(anchor="w", padx=20, pady=(10, 0))
        new_entry = ctk.CTkEntry(dialog, show="*")
        new_entry.pack(fill="x", padx=20, pady=5)
        
        # Confirm password
        ctk.CTkLabel(dialog, text="Confirm New Password:").pack(anchor="w", padx=20, pady=(10, 0))
        confirm_entry = ctk.CTkEntry(dialog, show="*")
        confirm_entry.pack(fill="x", padx=20, pady=5)
        
        error_label = ctk.CTkLabel(dialog, text="", text_color="red", font=ctk.CTkFont(size=12))
        error_label.pack(pady=5)
        
        def on_change():
            current = current_entry.get()
            new = new_entry.get()
            confirm = confirm_entry.get()
            
            if new != confirm:
                error_label.configure(text="New passwords do not match")
                return
            
            try:
                self.auth_service.change_password(self.user.username, current, new)
                messagebox.showinfo("Success", "Password changed successfully!")
                if self.on_password_changed:
                    self.on_password_changed()
                dialog.destroy()
            except ValueError as e:
                error_label.configure(text=str(e))
            except Exception as e:
                error_label.configure(text=f"Error: {str(e)}")
        
        ctk.CTkButton(
            dialog,
            text="Change Password",
            fg_color="green",
            command=on_change
        ).pack(pady=20)
