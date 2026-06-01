#!/usr/bin/env python3
"""
Logging System for AI Microscope Application
Provides centralized logging with file and console handlers with log rotation
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime


class AppLogger:
    """Centralized logging system for the AI Microscope application."""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup the logger with file and console handlers with rotation."""
        self._logger = logging.getLogger("AI_Microscope")
        self._logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self._logger.handlers:
            return
        
        # Create logs directory
        log_dir = Path(__file__).resolve().parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        # File handler with rotation - 10MB max, keep 5 backups
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler - info level and above
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        
        self._logger.info("Logger initialized with log rotation (10MB max, 5 backups)")
    
    @property
    def logger(self):
        """Get the logger instance."""
        return self._logger
    
    def debug(self, message):
        """Log debug message."""
        self._logger.debug(message)
    
    def info(self, message):
        """Log info message."""
        self._logger.info(message)
    
    def warning(self, message):
        """Log warning message."""
        self._logger.warning(message)
    
    def error(self, message, exc_info=False):
        """Log error message."""
        self._logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=False):
        """Log critical message."""
        self._logger.critical(message, exc_info=exc_info)


# Global logger instance
_logger = AppLogger()


def get_logger():
    """Get the global logger instance."""
    return _logger.logger


def log_debug(message):
    """Log debug message."""
    _logger.debug(message)


def log_info(message):
    """Log info message."""
    _logger.info(message)


def log_warning(message):
    """Log warning message."""
    _logger.warning(message)


def log_error(message, exc_info=False):
    """Log error message."""
    _logger.error(message, exc_info=exc_info)


def log_critical(message, exc_info=False):
    """Log critical message."""
    _logger.critical(message, exc_info=exc_info)
