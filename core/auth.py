#!/usr/bin/env python3
"""
Authentication Module for AI Microscope Application
Provides user authentication and authorization with medical-grade security
"""

import json
import hashlib
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from datetime import datetime

from utils.logger import log_info, log_error, log_warning


class UserRole(Enum):
    """User roles for access control."""
    TECHNICIAN = "technician"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class User:
    """Medical-grade user account with certification tracking."""
    
    def __init__(
        self,
        username: str,
        password_hash: str,
        role: UserRole,
        full_name: str = "",
        email: str = "",
        department: str = "",
        employee_id: str = "",
        created_at: Optional[str] = None,
        last_login: Optional[str] = None,
        is_active: bool = True,
        # Medical-specific fields
        certification_status: str = "pending",
        certification_date: Optional[str] = None,
        certification_expiry: Optional[str] = None,
        last_training_date: Optional[str] = None,
        allowed_operations: List[str] = None,
        signature_image_path: Optional[str] = None,
        session_timeout_minutes: int = 30,
        # Security fields
        failed_login_attempts: int = 0,
        last_password_change: Optional[str] = None,
        password_history: List[str] = None
    ):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.email = email
        self.department = department
        self.employee_id = employee_id
        self.created_at = created_at or datetime.now().isoformat()
        self.last_login = last_login
        self.is_active = is_active
        
        # Medical fields
        self.certification_status = certification_status
        self.certification_date = certification_date
        self.certification_expiry = certification_expiry
        self.last_training_date = last_training_date
        self.allowed_operations = allowed_operations or ["diagnosis", "view_records"]
        self.signature_image_path = signature_image_path
        self.session_timeout_minutes = session_timeout_minutes
        
        # Security fields
        self.failed_login_attempts = failed_login_attempts
        self.last_password_change = last_password_change or datetime.now().isoformat()
        self.password_history = password_history or []
    
    def is_certified(self) -> bool:
        """Check if user has valid certification."""
        if self.certification_status != "certified":
            return False
        
        if self.certification_expiry:
            expiry = datetime.fromisoformat(self.certification_expiry)
            if expiry < datetime.now():
                self.certification_status = "expired"
                return False
        
        return True
    
    def requires_password_change(self) -> bool:
        """Check if password change is required (every 90 days)."""
        last_change = datetime.fromisoformat(self.last_password_change)
        days_since_change = (datetime.now() - last_change).days
        return days_since_change > 90
    
    def can_perform_operation(self, operation: str) -> bool:
        """Check if user is authorized for specific operation."""
        if not self.is_certified():
            return False
        
        role_permissions = {
            UserRole.TECHNICIAN: ["diagnosis", "view_records", "capture_image"],
            UserRole.SUPERVISOR: ["diagnosis", "view_records", "capture_image", 
                                   "export_reports", "review_diagnoses"],
            UserRole.ADMIN: ["all"]
        }
        
        allowed = role_permissions.get(self.role, [])
        return operation in allowed or "all" in allowed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role.value,
            "full_name": self.full_name,
            "email": self.email,
            "department": self.department,
            "employee_id": self.employee_id,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "is_active": self.is_active,
            "certification_status": self.certification_status,
            "certification_date": self.certification_date,
            "certification_expiry": self.certification_expiry,
            "last_training_date": self.last_training_date,
            "allowed_operations": self.allowed_operations,
            "signature_image_path": self.signature_image_path,
            "session_timeout_minutes": self.session_timeout_minutes,
            "failed_login_attempts": self.failed_login_attempts,
            "last_password_change": self.last_password_change,
            "password_history": self.password_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        return cls(
            username=data["username"],
            password_hash=data["password_hash"],
            role=UserRole(data["role"]),
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            department=data.get("department", ""),
            employee_id=data.get("employee_id", ""),
            created_at=data.get("created_at"),
            last_login=data.get("last_login"),
            is_active=data.get("is_active", True),
            certification_status=data.get("certification_status", "pending"),
            certification_date=data.get("certification_date"),
            certification_expiry=data.get("certification_expiry"),
            last_training_date=data.get("last_training_date"),
            allowed_operations=data.get("allowed_operations"),
            signature_image_path=data.get("signature_image_path"),
            session_timeout_minutes=data.get("session_timeout_minutes", 30),
            failed_login_attempts=data.get("failed_login_attempts", 0),
            last_password_change=data.get("last_password_change"),
            password_history=data.get("password_history", [])
        )


class AuthenticationService:
    """Authentication service for user management."""
    
    def __init__(self, users_file: Optional[Path] = None):
        """Initialize authentication service.
        
        Args:
            users_file: Path to users JSON file (default: storage/users.json)
        """
        if users_file is None:
            base_dir = Path(__file__).resolve().parent.parent
            storage_dir = base_dir / "storage"
            storage_dir.mkdir(exist_ok=True)
            users_file = storage_dir / "users.json"
        
        self.users_file = Path(users_file)
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        
        self._load_users()
        self._ensure_default_users()
    
    def _load_users(self) -> None:
        """Load users from file."""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for username, user_data in data.items():
                        self.users[username] = User.from_dict(user_data)
                log_info(f"Loaded {len(self.users)} users from file")
        except Exception as e:
            log_error(f"Failed to load users: {str(e)}", exc_info=True)
    
    def _save_users(self) -> None:
        """Save users to file."""
        try:
            data = {username: user.to_dict() for username, user in self.users.items()}
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            log_info("Users saved to file")
        except Exception as e:
            log_error(f"Failed to save users: {str(e)}", exc_info=True)
    
    def _ensure_default_users(self) -> None:
        """Ensure default users exist."""
        if not self.users:
            # Create default admin user
            default_password = self._hash_password("admin123")
            admin_user = User(
                username="admin",
                password_hash=default_password,
                role=UserRole.ADMIN,
                full_name="System Administrator"
            )
            self.users["admin"] = admin_user
            
            # Create default technician user
            tech_password = self._hash_password("tech123")
            tech_user = User(
                username="technician",
                password_hash=tech_password,
                role=UserRole.TECHNICIAN,
                full_name="Lab Technician"
            )
            self.users["technician"] = tech_user
            
            self._save_users()
            log_warning("Created default users. Change passwords immediately!")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            True if authentication successful, False otherwise
        """
        user = self.users.get(username)
        if not user:
            log_warning(f"Authentication failed: user '{username}' not found")
            return False
        
        if not user.is_active:
            log_warning(f"Authentication failed: user '{username}' is inactive")
            return False
        
        password_hash = self._hash_password(password)
        if password_hash != user.password_hash:
            log_warning(f"Authentication failed: invalid password for '{username}'")
            return False
        
        # Update last login
        user.last_login = datetime.now().isoformat()
        self._save_users()
        
        self.current_user = user
        log_info(f"User '{username}' authenticated successfully as {user.role.value}")
        return user
    
    def logout(self) -> None:
        """Logout current user."""
        if self.current_user:
            log_info(f"User '{self.current_user.username}' logged out")
            self.current_user = None
    
    def get_current_user(self) -> Optional[User]:
        """Get current authenticated user.
        
        Returns:
            Current user or None if not authenticated
        """
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return self.current_user is not None
    
    def has_role(self, role: UserRole) -> bool:
        """Check if current user has specific role.
        
        Args:
            role: Role to check
            
        Returns:
            True if user has role, False otherwise
        """
        if not self.current_user:
            return False
        return self.current_user.role == role
    
    def has_permission(self, required_role: UserRole) -> bool:
        """Check if current user has required permission level.
        
        Permission hierarchy: ADMIN > SUPERVISOR > TECHNICIAN
        
        Args:
            required_role: Required role
            
        Returns:
            True if user has permission, False otherwise
        """
        if not self.current_user:
            return False
        
        role_hierarchy = {
            UserRole.ADMIN: 3,
            UserRole.SUPERVISOR: 2,
            UserRole.TECHNICIAN: 1
        }
        
        return role_hierarchy.get(self.current_user.role, 0) >= role_hierarchy.get(required_role, 0)
    
    def _validate_password_policy(self, password: str) -> Tuple[bool, str]:
        """Enforce medical-grade password policy.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < 12:
            return False, "Password must be at least 12 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain special character"
        
        # Check against common passwords
        common_passwords = ["password", "123456", "qwerty", "admin", "medical", "microscope"]
        if password.lower() in common_passwords:
            return False, "Password is too common"
        
        return True, "Password meets policy"
    
    def change_password(self, username: str, old_password: str, 
                       new_password: str) -> bool:
        """Change password with policy enforcement.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If password policy not met
        """
        # Verify old password
        old_hash = self._hash_password(old_password)
        user = self.users.get(username)
        
        if not user or user.password_hash != old_hash:
            raise ValueError("Current password is incorrect")
        
        # Validate new password policy
        is_valid, message = self._validate_password_policy(new_password)
        if not is_valid:
            raise ValueError(message)
        
        # Check password history
        new_hash = self._hash_password(new_password)
        if new_hash in user.password_history:
            raise ValueError("Cannot reuse recent passwords")
        
        # Update password history (keep last 5)
        user.password_history.append(user.password_hash)
        user.password_history = user.password_history[-5:]
        user.password_hash = new_hash
        user.last_password_change = datetime.now().isoformat()
        
        self._save_users()
        log_info(f"Password changed for user '{username}'")
        return True
    
    def record_failed_login(self, username: str) -> int:
        """Record failed login attempt and return remaining attempts.
        
        Args:
            username: Username
            
        Returns:
            Remaining attempts before lockout
        """
        user = self.users.get(username)
        if user:
            user.failed_login_attempts += 1
            self._save_users()
            return max(0, 5 - user.failed_login_attempts)
        return 0
    
    def reset_failed_attempts(self, username: str) -> None:
        """Reset failed login attempts counter.
        
        Args:
            username: Username
        """
        user = self.users.get(username)
        if user:
            user.failed_login_attempts = 0
            self._save_users()
    
    def is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts.
        
        Args:
            username: Username
            
        Returns:
            True if locked
        """
        user = self.users.get(username)
        if user:
            return user.failed_login_attempts >= 5
        return False
    
    def unlock_account(self, username: str) -> bool:
        """Unlock a locked account (admin only).
        
        Args:
            username: Username to unlock
            
        Returns:
            True if successful
        """
        if not self.has_role(UserRole.ADMIN):
            raise PermissionError("Only administrators can unlock accounts")
        
        user = self.users.get(username)
        if user:
            user.failed_login_attempts = 0
            user.is_active = True
            self._save_users()
            log_info(f"Account unlocked for user '{username}'")
            return True
        return False
    
    def update_user_certification(self, username: str, status: str, 
                                   expiry_date: Optional[str] = None) -> bool:
        """Update user certification status (admin/supervisor only).
        
        Args:
            username: User to update
            status: Certification status (pending, certified, expired)
            expiry_date: Certification expiry date
            
        Returns:
            True if successful
        """
        if not self.has_permission(UserRole.SUPERVISOR):
            raise PermissionError("Insufficient permissions")
        
        user = self.users.get(username)
        if user:
            user.certification_status = status
            user.certification_date = datetime.now().isoformat()
            user.certification_expiry = expiry_date
            self._save_users()
            log_info(f"Certification updated for user '{username}': {status}")
            return True
        return False
    
    def get_all_users_with_details(self) -> Dict[str, Dict]:
        """Get all users with their details for admin view.
        
        Returns:
            Dictionary of username -> user details
        """
        if not self.has_permission(UserRole.SUPERVISOR):
            raise PermissionError("Insufficient permissions")
        
        return {
            username: {
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.value,
                "email": user.email,
                "department": user.department,
                "is_active": user.is_active,
                "certification_status": user.certification_status,
                "certification_expiry": user.certification_expiry,
                "last_login": user.last_login,
                "failed_attempts": user.failed_login_attempts
            }
            for username, user in self.users.items()
        }
    
    def create_user(
        self,
        username: str,
        password: str,
        role: UserRole,
        full_name: str = ""
    ) -> bool:
        """Create a new user.
        
        Args:
            username: Username
            password: Plain text password
            role: User role
            full_name: Full name
            
        Returns:
            True if successful, False otherwise
        """
        if username in self.users:
            log_warning(f"User '{username}' already exists")
            return False
        
        password_hash = self._hash_password(password)
        user = User(
            username=username,
            password_hash=password_hash,
            role=role,
            full_name=full_name
        )
        self.users[username] = user
        self._save_users()
        log_info(f"User '{username}' created with role {role.value}")
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        user = self.users.get(username)
        if not user:
            return False
        
        old_hash = self._hash_password(old_password)
        if old_hash != user.password_hash:
            return False
        
        user.password_hash = self._hash_password(new_password)
        self._save_users()
        log_info(f"Password changed for user '{username}'")
        return True
    
    def get_all_users(self) -> Dict[str, User]:
        """Get all users.
        
        Returns:
            Dictionary of username -> User
        """
        return self.users.copy()
    
    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user.
        
        Args:
            username: Username to deactivate
            
        Returns:
            True if successful, False otherwise
        """
        user = self.users.get(username)
        if not user:
            return False
        
        user.is_active = False
        self._save_users()
        log_info(f"User '{username}' deactivated")
        return True
