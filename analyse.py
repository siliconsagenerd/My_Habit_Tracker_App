import sqlite3
from typing import List
import db as database_module
from counter import get_counter, Counter

def list_all_habits_details(db_conn: sqlite3.Connection) -> List[Counter]:
    """Returns a list of Counter objects for all habits."""
    habit_names = database_module.get_habits_list(db_conn)
    return [get_counter(db_conn, name) for name in habit_names if get_counter(db_conn, name) is not None]

def list_habits_by_periodicity_details(db_conn: sqlite3.Connection, periodicity: str) -> List[Counter]:
    """Returns a list of Counter objects for habits of a given periodicity."""
    habit_names = database_module.habit_by_periodicity(db_conn, periodicity)
    return [get_counter(db_conn, name) for name in habit_names if get_counter(db_conn, name) is not None]

def longest_streak_all_habits(db_conn: sqlite3.Connection) -> int:
    """Calculates the longest streak among all habits."""
    all_habit_names = database_module.get_habits_list(db_conn)
    if not all_habit_names:
        return 0
    streaks = [counter.get_longest_streak(db_conn) for name in all_habit_names if (counter := get_counter(db_conn, name))]
    return max(streaks) if streaks else 0

def calculate_longest_streak_for_habit(db_conn: sqlite3.Connection, name: str) -> int:
    """Calculates the longest streak for a specific habit by name."""
    counter = get_counter(db_conn, name)
    return counter.get_longest_streak(db_conn) if counter else 0

def calculate_current_streak_for_habit(db_conn: sqlite3.Connection, name: str) -> int:
    """Calculates the current streak for a specific habit by name."""
    counter = get_counter(db_conn, name)
    return counter.get_current_streak(db_conn) if counter else 0