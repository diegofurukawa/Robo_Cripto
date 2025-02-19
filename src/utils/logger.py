# src/utils/logger.py
from datetime import datetime
from typing import Optional, TextIO, Any
import logging
import sys

class Logger:
    """Centralized logging system"""
    def __init__(self, log_file: str, log_level: int = logging.INFO):
        self.setup_logger(log_file, log_level)
        self.gui_callback = None
        
    def setup_logger(self, log_file: str, log_level: int) -> None:
        """Setup logging configuration"""
        # Create logger
        self.logger = logging.getLogger('CryptoBot')
        self.logger.setLevel(log_level)
        
        # Create handlers
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Create formatters
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set formatters
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def set_gui_callback(self, callback: callable) -> None:
        """Set callback for GUI updates"""
        self.gui_callback = callback
        
    def log(self, message: str, level: int = logging.INFO) -> None:
        """Log a message with optional GUI update"""
        self.logger.log(level, message)
        
        if self.gui_callback:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.gui_callback(f"[{timestamp}] {message}")
            
    def error(self, message: str) -> None:
        """Log an error message"""
        self.log(message, logging.ERROR)
        
    def warning(self, message: str) -> None:
        """Log a warning message"""
        self.log(message, logging.WARNING)
        
    def debug(self, message: str) -> None:
        """Log a debug message"""
        self.log(message, logging.DEBUG)