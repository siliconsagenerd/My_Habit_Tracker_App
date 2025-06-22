import sqlite3
import datetime
import random
import os

import db as database_module

# The 5 predefined habits from your original project
PREDEFINED_HABITS = {
    "Study Daily": ("Dedicated study session for courses.", "Daily"),
    "Read Daily": ("Read at least one chapter of a book.", "Daily"),
    "Daily Workout": ("Minimum 30 minutes of physical activity.", "Daily"),
    "Weekly Project Review": ("Review progress and plan for the next week.", "Weekly"),
    "Grocery Shopping": ("Weekly trip to buy groceries.", "Weekly")
}


def run_preload():
    """
    Ensures a completely fresh start by deleting the old database file,
    creating new tables, and then preloading it with 5 habits and 30 days of sample data.
    """
    # Force deletion of the old database file to ensure a clean slate
    db_path = os.path.join("data", "user_habits.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Successfully deleted old database file at: {db_path}")
        except OSError as e:
            print(f"Error deleting file {db_path}: {e}")
            return

    db_conn = None
    try:
        # Get a connection to the new, empty database
        db_conn = database_module.get_db()
        print("Database connection successful. Starting preload...")

        # --- THIS IS THE FIX ---
        # Explicitly create the tables in the new empty database
        database_module.create_tables_if_not_exist(db_conn)
        print("Tables created successfully.")
        # ----------------------

        today = datetime.date.today()
        # Set a fixed creation date for consistency in testing
        creation_date = today - datetime.timedelta(days=35)

        for name, (desc, period) in PREDEFINED_HABITS.items():
            try:
                # Add the habit to the newly created table
                database_module.add_habit_to_db(db_conn, name, desc, period, creation_date)
                habit_id = database_module.get_habit_id_by_name(db_conn, name)
                print(f"Created habit: '{name}'")

                # Generate sample completion data for the last 30 days
                if habit_id:
                    completions = 0
                    for i in range(30):
                        day_to_check = today - datetime.timedelta(days=i)

                        # Use randomness to create a realistic dataset with some broken streaks
                        chance = 0.8 if period == "Daily" else 0.7

                        if random.random() < chance:
                            completion_time = datetime.datetime.combine(day_to_check,
                                                                        datetime.time(random.randint(9, 20)))
                            database_module.add_increment_date_to_db(db_conn, habit_id, completion_time)
                            completions += 1
                    print(f"-> Processed {completions} sample increments for '{name}'.")
            except Exception as e:
                print(f"Error processing '{name}': {e}")
                continue

    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if db_conn:
            db_conn.close()
            print("\nDatabase connection closed. Preload process completed.")


if __name__ == "__main__":
    print("Starting database preload script...")
    run_preload()