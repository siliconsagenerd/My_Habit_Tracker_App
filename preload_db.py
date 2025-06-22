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
        db_conn = database_module.get_db()
        print("Database connection successful. Starting preload...")

        database_module.create_tables_if_not_exist(db_conn)
        print("Tables created successfully.")

        today = datetime.date.today()

        # --- THIS IS THE FIX ---
        # 1. Create a date object as before
        creation_date_only = today - datetime.timedelta(days=35)
        # 2. Convert the date object into a datetime object by adding a time component (midnight)
        creation_datetime = datetime.datetime.combine(creation_date_only, datetime.time(0, 0))
        # ----------------------

        for name, (desc, period) in PREDEFINED_HABITS.items():
            try:
                # 3. Use the new datetime object when adding to the database
                database_module.add_habit_to_db(db_conn, name, desc, period, creation_datetime)
                habit_id = database_module.get_habit_id_by_name(db_conn, name)
                print(f"Created habit: '{name}'")

                if habit_id:
                    completions = 0
                    for i in range(30):
                        day_to_check = today - datetime.timedelta(days=i)
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