# db.py
import sqlite3
import datetime
import os
from typing import List, Optional

DATABASE_DIR = "data"
DATABASE_NAME = os.path.join(DATABASE_DIR, "user_habits.db")

def ensure_data_dir_exists():
    """Creates the data directory if it doesn't already exist."""
    os.makedirs(DATABASE_DIR, exist_ok=True)

def get_db() -> sqlite3.Connection:
    """Gets a new database connection."""
    ensure_data_dir_exists()
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables_if_not_exist(db: sqlite3.Connection):
    """Creates the habit and counter tables if they aren't already present."""
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        periodicity TEXT NOT NULL CHECK(periodicity IN ('Daily', 'Weekly')),
                        creation_date TEXT NOT NULL
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS counters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        habit_id INTEGER NOT NULL,
                        increment_date TEXT NOT NULL,
                        FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
                    )''')
    db.commit()

# --- Habit Table Functions ---
def add_habit_to_db(db: sqlite3.Connection, name: str, description: str, periodicity: str, creation_date: datetime.datetime):
    """Adds a new habit to the database."""
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO habits (name, description, periodicity, creation_date) VALUES (?, ?, ?, ?)",
                       (name, description, periodicity, creation_date.isoformat()))
        db.commit()
    except sqlite3.IntegrityError:
        print(f"Error: Habit with name '{name}' already exists.")
        raise

def get_habit_id_by_name(db: sqlite3.Connection, name: str) -> Optional[int]:
    """Retrieves a habit's ID by its name."""
    cursor = db.cursor()
    cursor.execute("SELECT id FROM habits WHERE name = ?", (name,))
    result = cursor.fetchone()
    return result['id'] if result else None

def get_habit_details_by_name(db: sqlite3.Connection, name: str) -> Optional[sqlite3.Row]:
    """Retrieves all details for a habit by its name."""
    cursor = db.cursor()
    cursor.execute("SELECT id, name, description, periodicity, creation_date FROM habits WHERE name = ?", (name,))
    return cursor.fetchone()

def get_habits_list(db: sqlite3.Connection) -> List[str]:
    """Returns a list of all habit names."""
    cursor = db.cursor()
    cursor.execute("SELECT name FROM habits ORDER BY name")
    return [row['name'] for row in cursor.fetchall()]

def habit_by_periodicity(db: sqlite3.Connection, periodicity: str) -> List[str]:
    """Returns a list of habit names for a given periodicity."""
    cursor = db.cursor()
    cursor.execute("SELECT name FROM habits WHERE periodicity = ? ORDER BY name", (periodicity,))
    return [row['name'] for row in cursor.fetchall()]

def delete_habit_from_db(db: sqlite3.Connection, habit_id: int):
    """Deletes a habit from the database. Associated counters are deleted by CASCADE constraint."""
    cursor = db.cursor()
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    db.commit()

# --- Counter Table Functions ---
def add_increment_date_to_db(db: sqlite3.Connection, habit_id: int, increment_datetime: datetime.datetime):
    """Adds a single completion record for a habit."""
    cursor = db.cursor()
    cursor.execute("INSERT INTO counters (habit_id, increment_date) VALUES (?, ?)",
                   (habit_id, increment_datetime.isoformat()))
    db.commit()

def get_increment_dates_for_habit(db: sqlite3.Connection, habit_id: int) -> List[datetime.datetime]:
    """Fetches all completion timestamps for a specific habit, sorted chronologically."""
    cursor = db.cursor()
    # FIX: Removed the redundant 'ASC' from the ORDER BY clause.
    cursor.execute("SELECT increment_date FROM counters WHERE habit_id = ? ORDER BY increment_date", (habit_id,))
    return [datetime.datetime.fromisoformat(row['increment_date']) for row in cursor.fetchall()]

def reset_increments_for_habit(db: sqlite3.Connection, habit_id: int):
    """Deletes all completion records for a specific habit."""
    cursor = db.cursor()
    cursor.execute("DELETE FROM counters WHERE habit_id = ?", (habit_id,))
    db.commit()

# FIX: Replaced the global variable with a self-contained 'with' block.
# This eliminates all the "Shadows name 'conn' from outer scope" warnings.
def initialize_database():
    """Ensures the database and its tables are created upon first import."""
    try:
        with get_db() as conn:
            print("Database connection successful. Checking for tables...")
            create_tables_if_not_exist(conn)
    except sqlite3.Error as e:
        print(f"Fatal database error on initialization: {e}")
        # Depending on the app's needs, you might want to exit or handle this more gracefully.

# Run initialization when this module is first imported.
initialize_database()