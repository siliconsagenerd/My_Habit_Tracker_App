"""Utility functions and configurations for the application."""
import logging
from config import LOG_FILE, LOG_LEVEL

def setup_logging() -> None:
    """Configures application-wide logging to file and console."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, mode='a'), # Append to the log file
            logging.StreamHandler() # Also print to the console
        ]
    )