# main.py
import sqlite3
import questionary
import db as database_module
from counter import Counter, get_counter
import analyse


# Main function that runs the CLI
def cli():
    """Main function to run the Command Line Interface."""
    if not questionary.confirm("Hi User! Welcome to your Habit Tracking App! Wanna proceed?", qmark="👋").ask():
        print("Okay, goodbye!")
        return

    stop = False
    while not stop:
        db_conn = database_module.get_db()

        # The main menu choice
        choice = questionary.select(
            "What do you want to do?",
            choices=["Create a New Habit", "Increment Habit", "Reset Habit",
                     "Analyse Habits", "Delete Habit", "Exit"],
            qmark="❓"
        ).ask()

        # --- FIX for "Cannot find reference 'ask' in 'None'" ---
        # This check handles when the user presses Ctrl+C to exit.
        if choice is None:
            stop = True
            print("\nExiting application.")
            db_conn.close()
            continue

        try:
            # --- FIX for "Unresolved reference" errors ---
            # These function calls now work because the functions are defined below.
            if choice == "Create a New Habit":
                create_habit(db_conn)
            elif choice == "Increment Habit":
                increment_habit(db_conn)
            elif choice == "Reset Habit":
                reset_habit(db_conn)
            elif choice == "Analyse Habits":
                analyse_habits_menu(db_conn)
            elif choice == "Delete Habit":
                delete_habit_action(db_conn)
            elif choice == "Exit":
                stop = True
                # FIX for "Typo"
                print("Happy Habiting! Goodbye!")
        except Exception as e:
            # A general catch-all for any other unexpected errors.
            print(f"An unexpected error occurred: {e}")
        finally:
            if db_conn:
                db_conn.close()


# --- FIX for "Unresolved reference" errors ---
# All the helper functions are now correctly defined at the top level of the module.

def create_habit(db_conn: sqlite3.Connection):
    """Guides the user through creating a new habit."""
    name = questionary.text("What's the name of your new habit?", validate=lambda text: len(text.strip()) > 0).ask()
    if name is None: return

    if get_counter(db_conn, name.strip()):
        print(f"❗️ Habit '{name.strip()}' already exists.")
        return

    desc = questionary.text("Describe your habit (optional):").ask()
    if desc is None: return

    per = questionary.select("Is this a Daily or a Weekly habit?", choices=["Daily", "Weekly"], qmark="⏳").ask()
    if per is None: return

    new_counter = Counter(name.strip(), desc.strip(), per)
    new_counter.store(db_conn)


def increment_habit(db_conn: sqlite3.Connection):
    """Guides the user through incrementing a habit."""
    habits = database_module.get_habits_list(db_conn)
    if not habits:
        print("No habits created yet. Please create one first.")
        return

    name = questionary.select("Which habit do you want to increment?", choices=habits + ["Cancel"], qmark="🎯").ask()
    if name is None or name == "Cancel": return

    counter = get_counter(db_conn, name)
    if counter:
        counter.increment(db_conn)


def reset_habit(db_conn: sqlite3.Connection):
    """Guides the user through resetting a habit's progress."""
    habits = database_module.get_habits_list(db_conn)
    if not habits: print("No habits to reset."); return

    name = questionary.select("Which habit's progress do you want to reset?", choices=habits + ["Cancel"],
                              qmark="🔄").ask()
    if name is None or name == "Cancel": return

    if questionary.confirm(f"Are you sure? This will delete all completion data for '{name}'.", default=False,
                           qmark="⚠️").ask():
        counter = get_counter(db_conn, name)
        if counter:
            counter.reset(db_conn)
    else:
        print("Reset cancelled.")


def analyse_habits_menu(db_conn: sqlite3.Connection):
    """Shows the analysis sub-menu."""
    analysis_choice = questionary.select(
        "Choose an analysis option:",
        choices=["List all habits (with current & longest streaks)",
                 "List habits by periodicity",
                 "Overall longest streak (across all habits)",
                 "Longest streak for a specific habit",
                 "Current streak for a specific habit",
                 "Back to Main Menu"],
        qmark="📊"
    ).ask()

    if analysis_choice is None or analysis_choice == "Back to Main Menu": return

    print("\n--- Analysis Result ---")
    if analysis_choice == "List all habits (with current & longest streaks)":
        all_habits = analyse.list_all_habits_details(db_conn)
        if not all_habits:
            print("No habits to display.")
        else:
            for habit in all_habits:
                current_s = habit.get_current_streak(db_conn)
                longest_s = habit.get_longest_streak(db_conn)
                print(f"- '{habit.name}' ({habit.periodicity}) | Current Streak: {current_s}, Longest: {longest_s}")
    else:  # Handle other analysis choices
        handle_specific_analysis(db_conn, analysis_choice)
    print("-----------------------\n")


def handle_specific_analysis(db_conn: sqlite3.Connection, analysis_choice: str):
    """Handles the logic for the specific analysis choices to reduce repetition."""
    if "periodicity" in analysis_choice:
        periodicity = questionary.select("Filter by periodicity:", choices=["Daily", "Weekly"], qmark="🗓️").ask()
        if periodicity:
            habits = analyse.list_habits_by_periodicity_details(db_conn, periodicity)
            if not habits:
                print(f"No {periodicity} habits found.")
            else:
                for habit in habits: print(f"  - {habit.name}")
        return

    if "Overall longest streak" in analysis_choice:
        streak = analyse.longest_streak_all_habits(db_conn)
        print(f"The overall longest streak among all habits is: {streak} period(s).")
        return

    # Logic for single-habit analysis
    habits_list = database_module.get_habits_list(db_conn)
    if not habits_list: print("No habits exist."); return

    name = questionary.select("Select the habit:", choices=habits_list + ["Cancel"]).ask()
    if name and name != "Cancel":
        if "Longest streak" in analysis_choice:
            streak = analyse.calculate_longest_streak_for_habit(db_conn, name)
            print(f"The longest streak for '{name}' is: {streak} period(s).")
        elif "Current streak" in analysis_choice:
            streak = analyse.calculate_current_streak_for_habit(db_conn, name)
            print(f"The current streak for '{name}' is: {streak} period(s).")


def delete_habit_action(db_conn: sqlite3.Connection):
    """Guides the user through deleting a habit."""
    habits = database_module.get_habits_list(db_conn)
    if not habits: print("No habits to delete."); return

    name = questionary.select("Which habit do you want to permanently delete?", choices=habits + ["Cancel"],
                              qmark="🗑️").ask()
    if name is None or name == "Cancel": return

    if questionary.confirm(f"Confirm permanent deletion of '{name}' and all its history?", default=False,
                           qmark="⚠️").ask():
        counter = get_counter(db_conn, name)
        if counter:
            counter.delete(db_conn)
    else:
        print("Deletion cancelled.")


if __name__ == "__main__":
    cli()