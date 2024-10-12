from datetime import datetime
from counter import HabitTracker
from db import initialize_database

def preload_database():
    """
    Preloads the database with predefined habits and their respective tracking dates.
    """

    cursor = db.cursor()

    # Create tables if they do not exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
                           id INTEGER PRIMARY KEY,
                           name TEXT UNIQUE NOT NULL,
                           description TEXT,
                           periodicity TEXT NOT NULL,
                           creation_date TEXT
                       )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS progress_log (
                               id INTEGER PRIMARY KEY,
                               habit_id INTEGER,
                               tracked_at TEXT,
                               FOREIGN KEY (habit_id) REFERENCES habits (id)
                           )''')

    db.commit()

    # Sample habits data
    habits = {
        "study": [
            "2024-10-01", "2024-10-02", "2024-10-03", "2024-10-04", "2024-10-05", "2024-10-06", "2024-10-07",
            "2024-10-08", "2024-10-09", "2024-10-10", "2024-10-11", "2024-10-12", "2024-10-13", "2024-10-14",
            "2024-10-15", "2024-10-16", "2024-10-17", "2024-10-18", "2024-10-19", "2024-10-20", "2024-10-21",
            "2024-10-22", "2024-10-23", "2024-10-24", "2024-10-25", "2024-10-26", "2024-10-27", "2024-10-28",
            "2024-10-29", "2024-10-30", "2024-10-31"
        ],
        "read": [
            "2024-10-01", "2024-10-02", "2024-10-04", "2024-10-06", "2024-10-08", "2024-10-10", "2024-10-12",
            "2024-10-14", "2024-10-16", "2024-10-18", "2024-10-20", "2024-10-22", "2024-10-24", "2024-10-26",
            "2024-10-28", "2024-10-30"
        ],
        "coding": [
            "2024-10-03", "2024-10-07", "2024-10-10", "2024-10-14", "2024-10-17", "2024-10-20", "2024-10-24",
            "2024-10-27", "2024-10-30"
        ],
        "writing": [
            "2024-10-05", "2024-10-12", "2024-10-19", "2024-10-26"
        ],
        "music": [
            "2024-10-02", "2024-10-09", "2024-10-16", "2024-10-23", "2024-10-30"
        ]
        # ... more habits
    }

    for habit_name, dates in habits.items():
        print(f"Processing habit: {habit_name}")
        cursor.execute('SELECT id FROM habits WHERE name = ?', (habit_name,))
        habit_id = cursor.fetchone()

        if not habit_id:
            print(f"  Creating new habit: {habit_name}")
            habit = HabitTracker(habit_name, f"{habit_name} habit",
                                 "Daily" if habit_name != "laundry" else "Weekly")

            try:
                habit.save_to_database(db)
            except Exception as e:
                print(f"  Error saving habit: {e}")
                break

            cursor.execute('SELECT id FROM habits WHERE name = ?', (habit_name,))
            habit_id = cursor.fetchone()[0]
        else:
            habit_id = habit_id[0]

        for date in dates:
            current_time = datetime.strptime(date, "%Y-%m-%d")
            cursor.execute('''INSERT INTO progress_log (habit_id, tracked_at)
                           VALUES (?, ?)''', (habit_id, current_time.strftime("%Y-%m-%d %H:%M:%S")))
            db.commit()

if __name__ == "__main__":
    db = initialize_database()
    preload_database()
    print("Sample data loaded successfully!")
