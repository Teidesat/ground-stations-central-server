"""
Centralized logging configuration for the entire application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_type: str = "simple"
) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging to file
        format_type: 'simple' or 'verbose' format
    """
    log_level = getattr(logging, level.upper())
    
    # Define formatters
    formatters = {
        'simple': logging.Formatter(
            '%(levelname)s %(asctime)s %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ),
        'verbose': logging.Formatter(
            '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d - %(message)s'
        )
    }
    
    formatter = formatters.get(format_type, formatters['simple'])
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logging.info(f"Logging configured with level={level}, format={format_type}")