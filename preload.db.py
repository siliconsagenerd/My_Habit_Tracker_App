# preload_db.py
import db as database_module
from counter import Counter
import datetime
import random # <<< ADD THIS LINE
import uuid # Was in my previous example, ensure it's there if you use it

# ... rest of your preload_db.py code

def run_preload():
    """
    Preload the database with predefined habits and their respective increment dates.
    This version tries to be more robust about existing data.
    """
    # Get a single connection for all preload operations
    db_conn = database_module.get_db()

    # Tables are created on import of database_module, but an explicit call here is fine too.
    # database_module.create_tables_if_not_exist(db_conn)

    # Predefined habits: {name: (description, periodicity, [list_of_completion_date_strings])}
    habits_data = {
        "Study Daily": ("Dedicated study session for courses.", "Daily",
                        ["2023-07-01", "2023-07-02", "2023-07-03", "2023-07-04", "2023-07-05", "2023-07-06",
                         "2023-07-07",
                         "2023-07-08", "2023-07-09", "2023-07-10", "2023-07-11", "2023-07-12", "2023-07-13",
                         "2023-07-14",
                         "2023-07-15", "2023-07-16", "2023-07-17", "2023-07-18", "2023-07-19", "2023-07-20",
                         "2023-07-21",
                         "2023-07-22", "2023-07-23", "2023-07-24", "2023-07-25", "2023-07-26", "2023-07-27",
                         "2023-07-28",
                         "2023-07-29", "2023-07-30", "2023-07-31"]),  # All days in July
        "Read Daily": ("Read at least one chapter or for 30 minutes.", "Daily",
                       ["2023-07-01", "2023-07-02", "2023-07-03", "2023-07-05", "2023-07-06", "2023-07-07",
                        "2023-07-08",
                        "2023-07-09", "2023-07-10", "2023-07-11", "2023-07-12", "2023-07-14", "2023-07-15",
                        "2023-07-16",
                        "2023-07-17", "2023-07-18", "2023-07-19", "2023-07-20", "2023-07-21", "2023-07-22",
                        "2023-07-23",
                        "2023-07-25", "2023-07-26", "2023-07-27", "2023-07-28", "2023-07-29", "2023-07-30",
                        "2023-07-31"]),  # Most days
        "Daily Workout": ("Minimum 30 minutes of physical activity.", "Daily",
                          ["2023-07-01", "2023-07-03", "2023-07-05", "2023-07-07", "2023-07-09", "2023-07-11",
                           "2023-07-13",
                           "2023-07-15", "2023-07-17", "2023-07-19", "2023-07-21", "2023-07-23", "2023-07-25",
                           "2023-07-27",
                           "2023-07-29", "2023-07-31"]),  # Every other day
        "Weekly Laundry": ("Wash and fold laundry.", "Weekly",
                           ["2023-07-01", "2023-07-08", "2023-07-15", "2023-07-22", "2023-07-29"]),  # Once a week
        "Plan Week Ahead": ("Review last week and plan tasks for the upcoming week.", "Weekly",
                            ["2023-07-02", "2023-07-09", "2023-07-16", "2023-07-23", "2023-07-30"])  # Sundays
    }

    # Fixed creation date for all predefined habits for consistency (e.g., start of sample data period)
    # Let's assume the sample data starts from 2023-07-01, so creation date is before that.
    predefined_creation_date = datetime.datetime(2023, 6, 15, 12, 0, 0)  # An arbitrary date before sample data

    for habit_name, details in habits_data.items():
        description, periodicity, completion_date_strings = details

        habit_id = database_module.get_habit_id_by_name(db_conn, habit_name)
        if not habit_id:
            try:
                print(f"Creating habit: {habit_name}")
                database_module.add_habit_to_db(db_conn, habit_name, description, periodicity, predefined_creation_date)
                habit_id = database_module.get_habit_id_by_name(db_conn, habit_name)  # Get the new ID
                if not habit_id:
                    print(f"Error: Could not retrieve ID for newly created habit '{habit_name}'. Skipping increments.")
                    continue
            except Exception as e:
                print(f"Error creating predefined habit '{habit_name}': {e}. Skipping.")
                continue
        else:
            print(f"Habit '{habit_name}' already exists with ID {habit_id}. Will add/check its increments.")

        # Add increments for this habit
        for date_str in completion_date_strings:
            # Convert date string to datetime object (assuming start of day for simplicity, or add random time)
            completion_datetime = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(
                hour=random.randint(9, 17), minute=random.randint(0, 59)  # Add some random time
            )

            # Optional: Check if this exact increment already exists to avoid duplicates if script is run multiple times
            # This would require a new db function: get_specific_increment(habit_id, datetime)
            # For now, we'll add them; streak logic should handle unique dates per period.
            try:
                database_module.add_increment_date_to_db(db_conn, habit_id, completion_datetime)
            except Exception as e:
                print(f"Error adding increment for '{habit_name}' on {date_str}: {e}")
        print(f"Added/checked increments for '{habit_name}'.")

    db_conn.close()  # Close the connection once all operations are done
    print("\nPreload process completed.")
    print("Four weeks of sample data (from 2023-07-01 to 2023-07-31) have been processed for predefined habits.")


if __name__ == "__main__":
    # This makes the script runnable directly.
    # It ensures the 'data' directory and tables exist before attempting to preload.
    print("Starting database preload script...")
    database_module.ensure_data_dir_exists()  # From db.py
    # Tables are created when db.py is imported due to the global scope call there.

    run_preload()
