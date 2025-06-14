import db as database_module
import datetime
import random


def run_preload():
    """Preloads the database with predefined habits and sample completion data."""
    db_conn = database_module.get_db()

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
                         "2023-07-29", "2023-07-30", "2023-07-31"]),
        "Read Daily": ("Read at least one chapter of a book.", "Daily",
                       ["2023-07-01", "2023-07-02", "2023-07-03", "2023-07-05", "2023-07-06", "2023-07-07",
                        "2023-07-08",
                        "2023-07-09", "2023-07-10", "2023-07-11", "2023-07-12", "2023-07-14", "2023-07-15",
                        "2023-07-16",
                        "2023-07-17", "2023-07-18", "2023-07-19", "2023-07-20", "2023-07-21", "2023-07-22",
                        "2023-07-23",
                        "2023-07-25", "2023-07-26", "2023-07-27", "2023-07-28", "2023-07-29", "2023-07-30",
                        "2023-07-31"]),
        "Daily Workout": ("Minimum 30 minutes of physical activity.", "Daily",
                          ["2023-07-01", "2023-07-03", "2023-07-05", "2023-07-07", "2023-07-09", "2023-07-11",
                           "2023-07-13",
                           "2023-07-15", "2023-07-17", "2023-07-19", "2023-07-21", "2023-07-23", "2023-07-25",
                           "2023-07-27",
                           "2023-07-29", "2023-07-31"]),
        "Weekly Project Review": ("Review progress and plan for the next week.", "Weekly",
                                  ["2023-07-02", "2023-07-09", "2023-07-16", "2023-07-23", "2023-07-30"]),
        "Grocery Shopping": ("Weekly trip to buy groceries.", "Weekly",
                             ["2023-07-01", "2023-07-08", "2023-07-15", "2023-07-22", "2023-07-29"])
    }
    creation_date = datetime.datetime(2023, 6, 15, 12, 0, 0)

    for name, (desc, period, dates) in habits_data.items():
        habit_id = database_module.get_habit_id_by_name(db_conn, name)
        if not habit_id:
            try:
                database_module.add_habit_to_db(db_conn, name, desc, period, creation_date)
                habit_id = database_module.get_habit_id_by_name(db_conn, name)
                print(f"Created habit: {name}")
            except Exception as e:
                print(f"Error creating '{name}': {e}");
                continue

        # This part adds increments even if the habit already existed.
        # For a true "preload once", you might clear old increments first.
        for date_str in dates:
            completion_time = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(
                hour=random.randint(9, 17), minute=random.randint(0, 59)
            )
            database_module.add_increment_date_to_db(db_conn, habit_id, completion_time)
        print(f"Processed increments for '{name}'.")

    db_conn.close()
    print("\nPreload process completed.")


# This ensures the script only runs when executed directly, not when imported.
if __name__ == "__main__":
    print("Starting database preload script...")
    run_preload()