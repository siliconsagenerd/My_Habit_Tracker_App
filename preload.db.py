from datetime import datetime

from counter import HabitTracker
from db import initialize_database

def preload_db(db):  # Add db as an argument
    """
    Preloads the database with predefined habits and their respective increment dates.
    """
    cursor = db.cursor()

    # ... (rest of your table creation code) ...

    # Updated dates for October 2024
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
        "coding": [  # New habit: coding
            "2024-10-03", "2024-10-07", "2024-10-10", "2024-10-14", "2024-10-17", "2024-10-20", "2024-10-24",
            "2024-10-27", "2024-10-30"
        ],
        "writing": [  # New habit: writing
            "2024-10-05", "2024-10-12", "2024-10-19", "2024-10-26"
        ],
        "music": [  # New habit: music
            "2024-10-02", "2024-10-09", "2024-10-16", "2024-10-23", "2024-10-30"
        ],
        # ... (rest of your habits data) ...
    }

    for habit_name, dates in habits.items():
        habit = HabitTracker(name=habit_name, description=f"{habit_name} habit", periodicity="Daily" if habit_name != "laundry" else "Weekly")
        habit.save_to_database(db)

        for date_str in dates:
            progress_date = datetime.strptime(date_str, "%Y-%m-%d")
            habit.log_progress(db, progress_date)  # Pass progress_date to log_progress

if __name__ == "__main__":
    db = initialize_database()
    preload_db(db)  # Pass the database connection to the function
    print("Sample data loaded successfully!")
