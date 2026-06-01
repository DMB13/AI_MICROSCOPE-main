#!/usr/bin/env python3
"""
Login Dialog for AI Microscope Application
Provides user authentication interface with login and register functionality
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Callable

from core.auth import AuthenticationService, UserRole


class LoginDialog(ctk.CTkToplevel):
    """Login dialog for user authentication with register option."""
    
    def __init__(
        self,
        parent,
        auth_service: AuthenticationService,
        on_login_success: Optional[Callable] = None
    ):
        """Initialize login dialog.
        
        Args:
            parent: Parent window
            auth_service: Authentication service instance
            on_login_success: Callback when login succeeds
        """
        super().__init__(parent)
        self.auth_service = auth_service
        self.on_login_success = on_login_success
        self.is_register_mode = False
        
        self.title("DMB AI Microscope - Login")
        self.geometry("480x500")
        self.resizable(False, False)
        
        # Set window icon
        try:
            from pathlib import Path
            icon_path = Path(__file__).resolve().parent.parent.parent / "logo.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        # Center dialog
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="🔐 LOGIN",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(30, 20))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Enter your credentials to continue",
            font=ctk.CTkFont(size=14)
        )
        self.subtitle_label.pack(pady=(0, 20))
        
        # Username
        self.username_frame = ctk.CTkFrame(self)
        self.username_frame.pack(pady=10, padx=40, fill="x")
        
        ctk.CTkLabel(self.username_frame, text="Username:").pack(anchor="w", padx=10, pady=(10, 5))
        self.username_entry = ctk.CTkEntry(self.username_frame, placeholder_text="Enter username")
        self.username_entry.pack(padx=10, pady=(0, 10), fill="x")
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        
        # Password
        self.password_frame = ctk.CTkFrame(self)
        self.password_frame.pack(pady=10, padx=40, fill="x")
        
        ctk.CTkLabel(self.password_frame, text="Password:").pack(anchor="w", padx=10, pady=(10, 5))
        self.password_entry = ctk.CTkEntry(
            self.password_frame,
            placeholder_text="Enter password",
            show="•"
        )
        self.password_entry.pack(padx=10, pady=(0, 10), fill="x")
        self.password_entry.bind("<Return>", lambda e: self._on_login())
        
        # Full name (only shown in register mode)
        self.full_name_frame = ctk.CTkFrame(self)
        ctk.CTkLabel(self.full_name_frame, text="Full Name:").pack(anchor="w", padx=10, pady=(10, 5))
        self.full_name_entry = ctk.CTkEntry(self.full_name_frame, placeholder_text="Enter full name")
        self.full_name_entry.pack(padx=10, pady=(0, 10), fill="x")
        
        # Confirm password (only shown in register mode)
        self.confirm_password_frame = ctk.CTkFrame(self)
        ctk.CTkLabel(self.confirm_password_frame, text="Confirm Password:").pack(anchor="w", padx=10, pady=(10, 5))
        self.confirm_password_entry = ctk.CTkEntry(
            self.confirm_password_frame,
            placeholder_text="Confirm password",
            show="•"
        )
        self.confirm_password_entry.pack(padx=10, pady=(0, 10), fill="x")
        self.confirm_password_entry.bind("<Return>", lambda e: self._on_register())
        
        # Role selection (only shown in register mode)
        self.role_frame = ctk.CTkFrame(self)
        ctk.CTkLabel(self.role_frame, text="Role:").pack(anchor="w", padx=10, pady=(10, 5))
        self.role_var = ctk.StringVar(value="technician")
        self.role_dropdown = ctk.CTkOptionMenu(
            self.role_frame,
            values=["technician", "admin", "lab_manager"],
            variable=self.role_var
        )
        self.role_dropdown.pack(padx=10, pady=(0, 10), fill="x")
        
        # Hide register-only fields initially
        self.full_name_frame.pack_forget()
        self.confirm_password_frame.pack_forget()
        self.role_frame.pack_forget()
        
        # Error message
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=11)
        )
        self.error_label.pack(pady=5)
        
        # Login/Register button
        self.action_button = ctk.CTkButton(
            self,
            text="Login",
            command=self._on_login,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.action_button.pack(pady=20, padx=40, fill="x")
        
        # Toggle between login and register
        self.toggle_button = ctk.CTkButton(
            self,
            text="Don't have an account? Register",
            command=self._toggle_mode,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            text_color="blue"
        )
        self.toggle_button.pack(pady=(0, 10))
        
        # Default credentials hint (only shown in login mode)
        self.hint_label = ctk.CTkLabel(
            self,
            text="Default: admin/admin123 or technician/tech123",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.hint_label.pack(pady=(10, 20))
        
        # Focus on username
        self.username_entry.focus()
    
    def _on_login(self) -> None:
        """Handle login button click with medical-grade security."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.configure(text="Please enter both username and password")
            return
        
        # Check for account lockout
        if self.auth_service.is_account_locked(username):
            messagebox.showerror(
                "Account Locked",
                "Account is temporarily locked due to too many failed login attempts.\n\n"
                "Please contact an administrator to unlock your account."
            )
            return
        
        # Attempt authentication
        user = self.auth_service.authenticate(username, password)
        
        if user:
            # Reset failed attempts on successful login
            self.auth_service.reset_failed_attempts(username)
            
            # Note: Certification check removed - all users can login
            
            # Check password age (optional security feature)
            if user.requires_password_change():
                self._show_password_change_required(username)
                return
            
            # Success - proceed with login
            self.error_label.configure(text="")
            
            if self.on_login_success:
                self.on_login_success(user)
            
            self.destroy()
        else:
            # Track failed attempt
            remaining = self.auth_service.record_failed_login(username)
            
            if remaining == 0:
                messagebox.showerror(
                    "Account Locked",
                    "Too many failed attempts. Your account has been locked.\n\n"
                    "Contact an administrator to unlock your account."
                )
                self.error_label.configure(text="Account locked")
            else:
                self.error_label.configure(text=f"Invalid credentials. {remaining} attempts remaining")
            
            self.password_entry.delete(0, "end")
            self.password_entry.focus()
    
    def _show_password_change_required(self, username: str) -> None:
        """Show password change dialog when password is expired."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Password Change Required")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="Password Change Required",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="orange"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text="Your password is over 90 days old and must be changed for security.",
            wraplength=350,
            justify="center"
        ).pack(pady=10)
        
        ctk.CTkLabel(dialog, text="New Password:").pack(anchor="w", padx=20, pady=(10, 0))
        new_pass = ctk.CTkEntry(dialog, show="*")
        new_pass.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(dialog, text="Confirm Password:").pack(anchor="w", padx=20, pady=(10, 0))
        confirm_pass = ctk.CTkEntry(dialog, show="*")
        confirm_pass.pack(fill="x", padx=20, pady=5)
        
        error_label = ctk.CTkLabel(dialog, text="", text_color="red", font=ctk.CTkFont(size=10))
        error_label.pack(pady=5)
        
        def on_change():
            if new_pass.get() != confirm_pass.get():
                error_label.configure(text="Passwords do not match")
                return
            
            try:
                # Get current password (user just logged in, so we need to re-verify)
                # For simplicity, we're using the current password from the login form
                current = self.password_entry.get()
                self.auth_service.change_password(username, current, new_pass.get())
                messagebox.showinfo("Success", "Password changed successfully! Please log in again.")
                dialog.destroy()
                self.password_entry.delete(0, "end")
                self.password_entry.insert(0, new_pass.get())
                self._on_login()  # Re-login with new password
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
    
    def _toggle_mode(self) -> None:
        """Toggle between login and register mode."""
        self.is_register_mode = not self.is_register_mode
        self.error_label.configure(text="")
        
        if self.is_register_mode:
            # Switch to register mode
            self.title_label.configure(text="📝 REGISTER")
            self.subtitle_label.configure(text="Create a new account")
            self.action_button.configure(text="Register", command=self._on_register)
            self.toggle_button.configure(text="Already have an account? Login")
            self.hint_label.pack_forget()
            
            # Show register fields
            self.full_name_frame.pack(pady=10, padx=40, fill="x")
            self.confirm_password_frame.pack(pady=10, padx=40, fill="x")
            self.role_frame.pack(pady=10, padx=40, fill="x")
            
            # Update password binding
            self.password_entry.bind("<Return>", lambda e: self.full_name_entry.focus())
            self.geometry("450x550")
        else:
            # Switch to login mode
            self.title_label.configure(text="🔐 LOGIN")
            self.subtitle_label.configure(text="Enter your credentials to continue")
            self.action_button.configure(text="Login", command=self._on_login)
            self.toggle_button.configure(text="Don't have an account? Register")
            self.hint_label.pack(pady=(10, 20))
            
            # Hide register fields
            self.full_name_frame.pack_forget()
            self.confirm_password_frame.pack_forget()
            self.role_frame.pack_forget()
            
            # Update password binding
            self.password_entry.bind("<Return>", lambda e: self._on_login())
            self.geometry("450x450")
        
        # Clear all fields
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.full_name_entry.delete(0, "end")
        self.confirm_password_entry.delete(0, "end")
        self.username_entry.focus()
    
    def _on_register(self) -> None:
        """Handle register button click."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        full_name = self.full_name_entry.get().strip()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not username or not password or not full_name or not confirm_password:
            self.error_label.configure(text="Please fill in all fields")
            return
        
        if password != confirm_password:
            self.error_label.configure(text="Passwords do not match")
            return
        
        if len(password) < 6:
            self.error_label.configure(text="Password must be at least 6 characters")
            return
        
        # Check if user already exists
        if username in self.auth_service.get_all_users():
            self.error_label.configure(text="Username already exists")
            return
        
        # Create new user with selected role
        role_map = {
            "technician": UserRole.TECHNICIAN,
            "admin": UserRole.ADMIN,
            "lab_manager": UserRole.LAB_MANAGER
        }
        selected_role = role_map.get(self.role_var.get(), UserRole.TECHNICIAN)
        
        success = self.auth_service.create_user(
            username=username,
            password=password,
            role=selected_role,
            full_name=full_name
        )
        
        if success:
            self.error_label.configure(text="", text_color="green")
            # Auto-login after successful registration
            if self.auth_service.authenticate(username, password):
                if self.on_login_success:
                    self.on_login_success(self.auth_service.get_current_user())
                self.destroy()
        else:
            self.error_label.configure(text="Registration failed. Please try again.", text_color="red")
