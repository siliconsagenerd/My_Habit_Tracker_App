# analyse.py
import sqlite3
from typing import List
import db as database_module  # Renamed import
from counter import Counter, get_counter  # Import Counter class and the helper


def list_all_habits_details(db_conn: sqlite3.Connection) -> List[Counter]:
    """Returns a list of Counter objects for all habits, with streaks calculated."""
    habit_names = database_module.get_habits_list(db_conn)
    detailed_habits = []
    for name in habit_names:
        counter_obj = get_counter(db_conn, name)
        if counter_obj:
            # Streaks will be calculated when __str__ is called or explicitly by get_X_streak
            detailed_habits.append(counter_obj)
    return detailed_habits


def list_habits_by_periodicity_details(db_conn: sqlite3.Connection, periodicity: str) -> List[Counter]:
    """Returns a list of Counter objects for habits of a given periodicity."""
    habit_names = database_module.habit_by_periodicity(db_conn, periodicity)
    detailed_habits = []
    for name in habit_names:
        counter_obj = get_counter(db_conn, name)
        if counter_obj:
            detailed_habits.append(counter_obj)
    return detailed_habits


def longest_streak_all_habits(db_conn: sqlite3.Connection) -> int:
    """Calculates the longest streak among all habits."""
    all_habit_names = database_module.get_habits_list(db_conn)
    if not all_habit_names:
        return 0

    max_overall_streak = 0
    for name in all_habit_names:
        counter = get_counter(db_conn, name)
        if counter:
            # Pass db_conn so that get_longest_streak can load fresh data
            max_overall_streak = max(max_overall_streak, counter.get_longest_streak(db_conn=db_conn))
    return max_overall_streak


def calculate_longest_streak_for_habit(db_conn: sqlite3.Connection, name: str) -> int:
    """Calculates the longest streak for a specific habit by name."""
    counter = get_counter(db_conn, name)
    if counter:
        # Pass db_conn so that get_longest_streak can load fresh data
        return counter.get_longest_streak(db_conn=db_conn)
    return 0


def calculate_current_streak_for_habit(db_conn: sqlite3.Connection, name: str) -> int:
    """Calculates the current streak for a specific habit by name."""
    counter = get_counter(db_conn, name)
    if counter:
        # Pass db_conn so that get_current_streak can load fresh data
        return counter.get_current_streak(db_conn=db_conn)
    return 0
