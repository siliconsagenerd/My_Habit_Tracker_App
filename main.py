# main.py
import sqlite3
import questionary  # Make sure to pip install questionary
import db as database_module  # Renamed import
from counter import Counter, get_counter  # Import helper from counter.py
import analyse  # Import your analyse module
import datetime  # For current date in analysis if needed


# Main function that runs the CLI
def cli():
    # get_db() returns a new connection each time.
    # For operations within a single CLI interaction,
    # it might be better to pass one connection around or use a context manager.
    # However, for simplicity here, each function call might get its own.
    # The Counter methods are updated to optionally accept and manage connections.

    # Greet the user
    # The loop `while not questionary.confirm(...).ask(): pass` means it will keep asking until user confirms.
    # This might be slightly annoying if they accidentally hit no.
    # Consider a simpler welcome or a single confirm.
    if not questionary.confirm("Hi User! Welcome to your Habit Tracking App! Wanna proceed?").ask():
        print("Okay, goodbye!")
        return

    stop = False
    while not stop:
        # Always get a fresh connection for the start of a new choice cycle
        # This is important if previous operations closed their specific connections.
        # However, get_db in the provided file opens a new one each time.
        # For longer operations, it's better to pass a single connection.
        # For this structure, most functions will open/close their own or accept one.

        choice = questionary.select(
            "What do you want to do?",
            choices=["Create a New Habit",
                     "Increment Habit",
                     "Reset Habit",
                     "Analyse Habits",
                     "Delete Habit",
                     "Exit"],
            qmark="❓"
        ).ask()

        if choice is None:  # User pressed Ctrl+C or Escape
            stop = True
            print("Exiting application.")
            continue

        db_conn = database_module.get_db()  # Get a connection for this cycle of operations

        try:
            if choice == "Create a New Habit":
                create_habit(db_conn)
            elif choice == "Increment Habit":
                increment_habit(db_conn)
            elif choice == "Reset Habit":
                reset_habit(db_conn)
            elif choice == "Analyse Habits":
                analyse_habits_menu(db_conn)  # Changed to avoid conflict with module name
            elif choice == "Delete Habit":
                delete_habit_action(db_conn)  # Changed to avoid conflict
            elif choice == "Exit":
                stop = True
                print("Happy Habbiting! Goodbye!")
        finally:
            db_conn.close()  # Ensure connection is closed after operations for this choice


def create_habit(db_conn: sqlite3.Connection):
    name = questionary.text("What's the name of your new habit?",
                            validate=lambda text: len(text) > 0 or "Name cannot be empty.").ask()
    if name is None: return  # User cancelled

    if get_counter(db_conn, name):
        print(f"❗️ Habit '{name}' already exists.")
        return

    desc = questionary.text("How do you wanna describe your habit? (Optional)").ask()
    if desc is None: return  # User cancelled (though it's optional, text allows empty)

    per = questionary.select("Is this a Daily or a Weekly habit?", choices=["Daily", "Weekly"], qmark="⏳").ask()
    if per is None: return  # User cancelled

    new_counter = Counter(name, desc if desc else "", per)  # Use empty string if no desc
    try:
        new_counter.store(db_conn)  # This will set new_counter.habit_id
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # store() already prints an error, but good to catch here too.
        # main.py shouldn't crash the whole app.
        pass


def increment_habit(db_conn: sqlite3.Connection):
    habits = database_module.get_habits_list(db_conn)
    if not habits:
        print("No habits created yet. Please create a habit first.")
        return

    name = questionary.select(
        "What's the name of the habit you want to increment?",
        choices=habits + [questionary.Separator(), "Cancel"], qmark="🎯"
    ).ask()

    if name is None or name == "Cancel": return

    counter = get_counter(db_conn, name)
    if counter:
        counter.increment(db_conn)  # Pass connection
    else:
        print(f"❗️ Habit '{name}' not found (should not happen if selected from list).")


def reset_habit(db_conn: sqlite3.Connection):
    habits = database_module.get_habits_list(db_conn)
    if not habits:
        print("No habits created yet.")
        return

    name = questionary.select(
        "What's the name of the habit you want to reset (deletes all its check-offs)?",
        choices=habits + [questionary.Separator(), "Cancel"], qmark="🔄"
    ).ask()

    if name is None or name == "Cancel": return

    confirm_reset = questionary.confirm(
        f"Are you sure you want to reset all progress for '{name}'? This cannot be undone.", default=False).ask()
    if not confirm_reset:
        print("Reset cancelled.")
        return

    counter = get_counter(db_conn, name)
    if counter:
        counter.reset(db_conn)  # Pass connection
    else:
        print(f"❗️ Habit '{name}' not found.")


def analyse_habits_menu(db_conn: sqlite3.Connection):  # Renamed
    analysis_choice = questionary.select(
        "What analysis would you like to perform?",
        choices=["List all habits (with current streaks)",
                 "List habits by periodicity",
                 "Longest streak of all habits",
                 "Longest streak for a specific habit",
                 "Current streak for a specific habit",
                 questionary.Separator(),
                 "Back to Main Menu"],
        qmark="📊"
    ).ask()

    if analysis_choice is None or analysis_choice == "Back to Main Menu":
        return

    print("\n--- Analysis Result ---")
    if analysis_choice == "List all habits (with current streaks)":
        all_detailed_habits = analyse.list_all_habits_details(db_conn)
        if not all_detailed_habits:
            print("No habits to display.")
        else:
            for counter_obj in all_detailed_habits:
                # To display streaks, the Counter object's __str__ needs to calc or have them pre-calced
                # Or print them explicitly here:
                current_s = counter_obj.get_current_streak(db_conn)
                longest_s = counter_obj.get_longest_streak(db_conn)
                print(
                    f"Habit: '{counter_obj.name}' ({counter_obj.periodicity}) - Current Streak: {current_s}, Longest: {longest_s}")


    elif analysis_choice == "List habits by periodicity":
        periodicity = questionary.select("Select the periodicity", choices=["Daily", "Weekly"], qmark="🗓️").ask()
        if periodicity is None: return

        habits_by_p = analyse.list_habits_by_periodicity_details(db_conn, periodicity)
        if not habits_by_p:
            print(f"No {periodicity} habits found.")
        else:
            print(f"Tracked {periodicity} habits:")
            for counter_obj in habits_by_p:
                current_s = counter_obj.get_current_streak(db_conn)
                longest_s = counter_obj.get_longest_streak(db_conn)
                print(f"  '{counter_obj.name}' - Current Streak: {current_s}, Longest: {longest_s}")

    elif analysis_choice == "Longest streak of all habits":
        streak = analyse.longest_streak_all_habits(db_conn)
        print(f"The overall longest streak among all habits is: {streak} period(s).")

    elif analysis_choice == "Longest streak for a specific habit":
        habits = database_module.get_habits_list(db_conn)
        if not habits: print("No habits exist."); return
        name = questionary.select("Select the habit", choices=habits + ["Cancel"], qmark="🏆").ask()
        if name and name != "Cancel":
            streak = analyse.calculate_longest_streak_for_habit(db_conn, name)
            print(f"The longest streak achieved for habit '{name}' is: {streak} period(s).")

    elif analysis_choice == "Current streak for a specific habit":
        habits = database_module.get_habits_list(db_conn)
        if not habits: print("No habits exist."); return
        name = questionary.select("Select the habit", choices=habits + ["Cancel"], qmark="📈").ask()
        if name and name != "Cancel":
            streak = analyse.calculate_current_streak_for_habit(db_conn, name)
            print(f"The current streak for habit '{name}' is: {streak} period(s).")
    print("-----------------------\n")


def delete_habit_action(db_conn: sqlite3.Connection):  # Renamed
    habits = database_module.get_habits_list(db_conn)
    if not habits:
        print("No habits to delete.")
        return

    name = questionary.select(
        "What's the name of the habit you want to delete?",
        choices=habits + [questionary.Separator(), "Cancel"], qmark="🗑️"
    ).ask()

    if name is None or name == "Cancel": return

    confirm_delete = questionary.confirm(f"Are you sure you want to PERMANENTLY delete '{name}' and all its history?",
                                         default=False).ask()
    if not confirm_delete:
        print("Deletion cancelled.")
        return

    counter = get_counter(db_conn, name)  # Fetch by name to get its ID
    if counter:
        counter.delete(db_conn)  # delete method on Counter instance uses its habit_id
    else:
        print(f"❗️ Habit '{name}' could not be found for deletion.")


if __name__ == "__main__":
    # Ensure tables are created on startup by importing db
    # The db.py script already does this on import.
    print("Initializing database connection and tables...")
    # No need for explicit db_module.create_tables() if db.py does it on import.
    cli()
