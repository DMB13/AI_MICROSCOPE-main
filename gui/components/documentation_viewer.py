#!/usr/bin/env python3
"""
Documentation Viewer Component for AI Microscope
Professional, clinical-grade in-app help system with modern UI
"""

import customtkinter as ctk
from tkinter import ttk
from pathlib import Path
from typing import Dict, Optional, Callable
import logging
import json
import re

from utils.markdown_converter import MarkdownToHTMLConverter

logger = logging.getLogger(__name__)


class DocumentationViewer(ctk.CTkToplevel):
    """
    Professional documentation viewer with sidebar navigation
    and clinical-friendly styling.
    """
    
    # Documentation categories and their files
    DOCUMENTATION_STRUCTURE = {
        "Getting Started": {
            "icon": "🚀",
            "file": "getting_started.md",
            "description": "Quick start guide for new users"
        },
        "User Guide": {
            "icon": "📖",
            "file": "user_guide.md",
            "description": "Complete user manual"
        },
        "FAQ": {
            "icon": "❓",
            "file": "faq.md",
            "description": "Frequently asked questions"
        },
        "Troubleshooting": {
            "icon": "🔧",
            "file": "troubleshooting.md",
            "description": "Solve common problems"
        },
        "Clinical Best Practices": {
            "icon": "🏥",
            "file": "clinical_best_practices.md",
            "description": "Clinical guidelines and protocols"
        }
    }
    
    def __init__(
        self,
        parent,
        initial_doc: Optional[str] = None,
        theme: str = "light",
        on_close: Optional[Callable] = None
    ):
        """Initialize the documentation viewer.
        
        Args:
            parent: Parent window
            initial_doc: Initial document to display (filename)
            theme: Theme mode ("light" or "dark")
            on_close: Callback when viewer is closed
        """
        super().__init__(parent)
        
        self.parent = parent
        self.theme = theme
        self.on_close = on_close
        self.converter = MarkdownToHTMLConverter()
        self.docs_dir = Path(__file__).parent.parent.parent / "docs" / "user_facing"
        self.current_doc = initial_doc
        self.last_opened_doc = self._load_last_opened()
        
        # Configure window
        self.title("DMB AI Microscope - Help & Documentation")
        self.geometry("1100x700")
        self.minsize(800, 600)
        
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
        self.focus_force()
        
        # Setup UI
        self._setup_ui()
        self._load_document(initial_doc or self.last_opened_doc or "getting_started.md")
        
        # Center window
        self.after(100, self._center_window)
        
        logger.info("Documentation viewer initialized")
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True)

        # Sidebar (navigation) on left
        self._create_sidebar()

        # Content area on right
        self._create_content_area()

        # Toolbar at bottom
        self._create_toolbar()
    
    def _create_sidebar(self):
        """Create the sidebar navigation on the left side."""
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=220,
            corner_radius=0,
            fg_color=("gray95", "gray15")
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Compact header
        header = ctk.CTkFrame(
            self.sidebar,
            fg_color=("lightblue", "#1a237e"),
            corner_radius=0
        )
        header.pack(fill="x", padx=0, pady=(0, 10))

        title_label = ctk.CTkLabel(
            header,
            text="📚 Help",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "white")
        )
        title_label.pack(anchor="center", padx=10, pady=8)

        # Compact search box
        search_frame = ctk.CTkFrame(self.sidebar, fg_color=("gray95", "gray15"))
        search_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍",
            height=32,
            corner_radius=6,
            border_width=1,
            border_color=("lightblue", "#1a237e")
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # Documentation list with compact styling
        self.doc_list_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            label_text="",
            fg_color=("gray95", "gray15"),
            scrollbar_button_color=("lightblue", "#1a237e"),
            scrollbar_button_hover_color=("skyblue", "#303f9f")
        )
        self.doc_list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Create compact document buttons
        self.doc_buttons = {}
        for doc_name, doc_info in self.DOCUMENTATION_STRUCTURE.items():
            button = ctk.CTkButton(
                self.doc_list_frame,
                text=f"{doc_info['icon']} {doc_name}",
                font=ctk.CTkFont(size=11),
                height=38,
                anchor="w",
                corner_radius=6,
                fg_color=("gray95", "gray20"),
                text_color=("gray20", "gray80"),
                hover_color=("lightblue", "#2a3680"),
                border_width=1,
                border_color=("gray85", "gray30"),
                command=lambda name=doc_name: self._load_document_by_name(name)
            )
            button.pack(fill="x", pady=2)
            self.doc_buttons[doc_name] = button

    def _create_content_area(self):
        """Create the content area on the right side."""
        content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=("gray98", "gray12")
        )
        content_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        # Content text widget for displaying documents
        self.content_text = ctk.CTkTextbox(
            content_frame,
            font=ctk.CTkFont(family="Segoe UI", size=15),
            wrap="word",
            corner_radius=0,
            border_width=3,
            border_color=("lightblue", "#1a237e"),
            fg_color=("white", "#1e1e2e"),
            text_color=("gray20", "gray80"),
            padx=50,
            pady=30
        )
        self.content_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.content_text.configure(state="disabled")

    def _create_toolbar(self):
        """Create the toolbar with action buttons at the bottom of the window."""
        toolbar = ctk.CTkFrame(
            self.main_container,
            height=60,
            fg_color=("gray95", "gray15"),
            corner_radius=0
        )
        toolbar.pack(side="bottom", fill="x", padx=0, pady=0)

        # Center buttons
        button_frame = ctk.CTkFrame(toolbar, fg_color=("gray95", "gray15"))
        button_frame.pack(anchor="center", pady=10)

        # Close button
        close_button = ctk.CTkButton(
            button_frame,
            text="✕ Close",
            width=120,
            height=36,
            font=ctk.CTkFont(size=12, weight="normal"),
            corner_radius=8,
            fg_color=("gray60", "#424242"),
            hover_color=("gray40", "#616161"),
            command=self._close_viewer
        )
        close_button.pack(side="left", padx=5)
    
    def _load_document(self, filename: str):
        """Load and display a document.

        Args:
            filename: Name of the markdown file to load
        """
        doc_path = self.docs_dir / filename

        if not doc_path.exists():
            print(f"Error: Document not found: {filename}")
            return

        try:
            # Read markdown content
            with open(doc_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Convert to formatted text
            formatted_text = self._markdown_to_formatted_text(markdown_content)

            # Update content
            self.content_text.configure(state="normal")
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", formatted_text)
            self.content_text.configure(state="disabled")

            # Highlight current button
            doc_name = self._get_doc_name_from_filename(filename)
            self._highlight_current_doc(doc_name)

            # Save last opened
            self._save_last_opened(filename)

            self.current_doc = filename
            print(f"DEBUG: Loaded document: {filename}, content length: {len(formatted_text)}")
            logger.info(f"Loaded document: {filename}")

        except Exception as e:
            logger.error(f"Error loading document: {e}")
            print(f"Error loading document: {str(e)}")
    
    def _load_document_by_name(self, doc_name: str):
        """Load a document by its display name.

        Args:
            doc_name: Display name of the document
        """
        if doc_name in self.DOCUMENTATION_STRUCTURE:
            filename = self.DOCUMENTATION_STRUCTURE[doc_name]["file"]
            self._load_document(filename)

    def _markdown_to_formatted_text(self, markdown: str) -> str:
        """Convert markdown to formatted text for CTkTextbox.
        
        Args:
            markdown: Markdown content
            
        Returns:
            Formatted text with CTk tags
        """
        lines = markdown.split('\n')
        result = []
        
        for line in lines:
            # Headers
            if line.startswith('# '):
                result.append(f"\n{'='*60}\n{line[2:]}\n{'='*60}\n\n")
            elif line.startswith('## '):
                result.append(f"\n{'─'*60}\n{line[3:]}\n{'─'*60}\n\n")
            elif line.startswith('### '):
                result.append(f"\n▸ {line[4:]}\n\n")
            
            # Horizontal rules
            elif line.strip() == '---':
                result.append(f"\n{'─'*60}\n\n")
            
            # Bold
            elif '**' in line:
                line = line.replace('**', '')
                result.append(f"{line}\n")
            
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                result.append(f"  • {line[2:]}\n")
            elif re.match(r'^\d+\.', line):
                result.append(f"  {line}\n")
            
            # Regular paragraphs
            elif line.strip():
                result.append(f"{line}\n")
            else:
                result.append("\n")
        
        return ''.join(result)
    
    def _get_doc_name_from_filename(self, filename: str) -> str:
        """Get display name from filename.
        
        Args:
            filename: Markdown filename
            
        Returns:
            Display name
        """
        for doc_name, doc_info in self.DOCUMENTATION_STRUCTURE.items():
            if doc_info["file"] == filename:
                return doc_name
        return filename
    
    def _highlight_current_doc(self, doc_name: str):
        """Highlight the currently selected document in sidebar with enhanced styling.

        Args:
            doc_name: Display name of current document
        """
        for name, button in self.doc_buttons.items():
            if name == doc_name:
                button.configure(
                    fg_color=("lightblue", "#1a237e"),
                    text_color=("gray10", "white"),
                    border_width=2,
                    border_color=("skyblue", "#303f9f")
                )
            else:
                button.configure(
                    fg_color=("gray95", "gray20"),
                    text_color=("gray20", "gray80"),
                    border_width=1,
                    border_color=("gray85", "gray30")
                )
    
    def _on_search(self, event):
        """Handle search in documentation.
        
        Args:
            event: Key event
        """
        query = self.search_entry.get().lower()
        
        if not query:
            # Show all buttons
            for button in self.doc_buttons.values():
                button.pack(fill="x", pady=2)
            return
        
        # Filter buttons based on search
        for doc_name, button in self.doc_buttons.items():
            if query in doc_name.lower():
                button.pack(fill="x", pady=2)
            else:
                button.pack_forget()

    def _save_last_opened(self, filename: str):
        """Save the last opened document to preferences.
        
        Args:
            filename: Document filename
        """
        try:
            config_file = Path(__file__).parent.parent.parent / "storage" / "doc_viewer_config.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                "last_opened": filename,
                "theme": self.theme
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            logger.warning(f"Could not save last opened document: {e}")
    
    def _load_last_opened(self) -> Optional[str]:
        """Load the last opened document from preferences.
        
        Returns:
            Filename of last opened document, or None
        """
        try:
            config_file = Path(__file__).parent.parent.parent / "storage" / "doc_viewer_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return config.get("last_opened")
        except Exception as e:
            logger.warning(f"Could not load last opened document: {e}")
        return None
    
    def _center_window(self):
        """Center the window on the parent."""
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _close_viewer(self):
        """Close the documentation viewer."""
        if self.on_close:
            self.on_close()
        self.destroy()


def show_documentation(
    parent,
    initial_doc: Optional[str] = None,
    theme: str = "light"
):
    """Convenience function to show the documentation viewer.
    
    Args:
        parent: Parent window
        initial_doc: Initial document to display
        theme: Theme mode
    """
    viewer = DocumentationViewer(parent, initial_doc, theme)
    return viewer


if __name__ == "__main__":
    # Test the documentation viewer
    import re
    root = ctk.CTk()
    root.geometry("200x200")
    
    def open_help():
        show_documentation(root)
    
    ctk.CTkButton(root, text="Open Help", command=open_help).pack(padx=20, pady=20)
    
    root.mainloop()
