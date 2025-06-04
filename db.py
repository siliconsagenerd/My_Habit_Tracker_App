# db.py
import sqlite3
import datetime
import os
from typing import List, Optional

DATABASE_DIR = "data"
DATABASE_NAME = os.path.join(DATABASE_DIR, "user_habits.db") # Renamed for clarity

def ensure_data_dir_exists():
    os.makedirs(DATABASE_DIR, exist_ok=True)

def get_db() -> sqlite3.Connection:
    """Establishes and returns a database connection."""
    ensure_data_dir_exists()
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def create_tables_if_not_exist(db: sqlite3.Connection):
    """Creates habit and counter tables if they don't exist."""
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
                        increment_date TEXT NOT NULL, -- Stores ISO format datetime string
                        FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
                    )''')
    db.commit()
    print("Database tables checked/created.")

# --- Habit Table Functions ---
def add_habit_to_db(db: sqlite3.Connection, name: str, description: str, periodicity: str, creation_date: datetime.datetime):
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO habits (name, description, periodicity, creation_date)
            VALUES (?, ?, ?, ?)
        """, (name, description, periodicity, creation_date.isoformat()))
        db.commit()
    except sqlite3.IntegrityError:
        # This will be caught if habit 'name' is not unique
        print(f"Error: Habit with name '{name}' already exists.")
        raise # Re-raise for the caller to handle if needed

def get_habit_id_by_name(db: sqlite3.Connection, name: str) -> Optional[int]:
    cursor = db.cursor()
    cursor.execute("SELECT id FROM habits WHERE name = ?", (name,))
    result = cursor.fetchone()
    return result['id'] if result else None

def get_habit_details_by_name(db: sqlite3.Connection, name: str) -> Optional[sqlite3.Row]:
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
    cursor = db.cursor()
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    db.commit() # Also deletes related counters due to ON DELETE CASCADE

# --- Counter Table Functions ---
def add_increment_date_to_db(db: sqlite3.Connection, habit_id: int, increment_datetime: datetime.datetime):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO counters (habit_id, increment_date)
        VALUES (?, ?)
    """, (habit_id, increment_datetime.isoformat()))
    db.commit()

def get_increment_dates_for_habit(db: sqlite3.Connection, habit_id: int) -> List[datetime.datetime]:
    """Fetches all increment dates for a habit, sorted."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT increment_date FROM counters
        WHERE habit_id = ? ORDER BY increment_date ASC
    """, (habit_id,))
    return [datetime.datetime.fromisoformat(row['increment_date']) for row in cursor.fetchall()]

def reset_increments_for_habit(db: sqlite3.Connection, habit_id: int):
    """Deletes all increment records for a specific habit."""
    cursor = db.cursor()
    cursor.execute("DELETE FROM counters WHERE habit_id = ?", (habit_id,))
    db.commit()

# Initialize tables when module is loaded (idempotent)
conn = get_db()
create_tables_if_not_exist(conn)
conn.close()
