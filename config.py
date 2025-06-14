"""Configuration settings for the habit tracking application."""
import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# --- Database Configuration ---
# Use environment variable if set, otherwise default to a local file.
DB_FILE = os.environ.get('HABIT_DB_PATH', BASE_DIR / 'data' / 'user_habits.db')

# --- Logging Configuration ---
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'habit_tracker.log'
LOG_LEVEL = os.environ.get('HABIT_LOG_LEVEL', 'INFO')

# --- Application Settings ---
ALLOWED_PERIODICITIES = ['Daily', 'Weekly']
MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500

# Ensure required directories exist for database and logs
DB_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)