#!/usr/bin/env python3
"""
Loading Spinner Component for AI Microscope Application
Provides loading indicators for long-running operations
"""

import customtkinter as ctk
from typing import Optional


class LoadingSpinner(ctk.CTkFrame):
    """Loading spinner component for indicating progress."""
    
    def __init__(
        self,
        parent,
        text: str = "Loading...",
        size: int = 40,
        **kwargs
    ):
        """Initialize loading spinner.
        
        Args:
            parent: Parent widget
            text: Text to display
            size: Size of the spinner
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)
        self.text = text
        self.size = size
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create spinner widgets."""
        # Progress bar as spinner
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=self.size * 2,
            height=self.size,
            mode="indeterminate"
        )
        self.progress_bar.pack(pady=10)
        
        # Text label
        self.label = ctk.CTkLabel(self, text=self.text)
        self.label.pack(pady=5)
        
        # Start animation
        self.progress_bar.start()
    
    def set_text(self, text: str) -> None:
        """Update the text label.
        
        Args:
            text: New text to display
        """
        self.label.configure(text=text)
    
    def start(self) -> None:
        """Start the spinner animation."""
        self.progress_bar.start()
    
    def stop(self) -> None:
        """Stop the spinner animation."""
        self.progress_bar.stop()


class ProgressDialog(ctk.CTkToplevel):
    """Progress dialog with progress bar for long-running operations."""
    
    def __init__(
        self,
        parent,
        title: str = "Processing",
        message: str = "Please wait...",
        total_steps: int = 100
    ):
        """Initialize progress dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Initial message
            total_steps: Total number of steps for progress
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Center dialog
        self.transient(parent)
        self.grab_set()
        
        self.total_steps = total_steps
        self.current_step = 0
        
        self._create_widgets(message)
    
    def _create_widgets(self, message: str) -> None:
        """Create dialog widgets."""
        # Message label
        self.message_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        self.message_label.pack(pady=30)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=300,
            height=20,
            mode="determinate"
        )
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)
        
        # Percentage label
        self.percentage_label = ctk.CTkLabel(self, text="0%")
        self.percentage_label.pack(pady=10)
    
    def update_progress(self, step: int, message: Optional[str] = None) -> None:
        """Update progress.
        
        Args:
            step: Current step number
            message: Optional new message
        """
        self.current_step = step
        progress = step / self.total_steps
        self.progress_bar.set(progress)
        self.percentage_label.configure(text=f"{int(progress * 100)}%")
        
        if message:
            self.message_label.configure(text=message)
        
        self.update_idletasks()
    
    def set_message(self, message: str) -> None:
        """Update the message.
        
        Args:
            message: New message
        """
        self.message_label.configure(text=message)
    
    def close(self) -> None:
        """Close the dialog."""
        self.destroy()
