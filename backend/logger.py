"""
Logging module for the Dark Web Monitoring Tool.
Provides a centralized logging configuration.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import config

# Create logs directory if it doesn't exist
log_dir = Path(os.path.dirname(config.LOG_FILE))
log_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
def setup_logger(name):
    """Set up and return a logger with the given name"""
    logger = logging.getLogger(name)
    
    # Set log level based on configuration
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Create main logger
logger = setup_logger('darkweb')

# Log startup message
logger.info("Dark Web Monitoring Tool starting up")
logger.info(f"Log level: {config.LOG_LEVEL}")
logger.info(f"Development mode: {config.DEV_MODE}")

# Function to get a module-specific logger
def get_logger(module_name):
    """Get a logger for a specific module"""
    return setup_logger(f'darkweb.{module_name}')