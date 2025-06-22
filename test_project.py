import pytest
import sqlite3
import datetime
from freezegun import freeze_time

import db as database_module
from counter import Counter, get_counter
from analyse import (
    calculate_longest_streak_for_habit,
    calculate_current_streak_for_habit,
    longest_streak_all_habits,
    list_habits_by_periodicity_details
)

@pytest.fixture
def db_conn():
    """Pytest fixture for an in-memory SQLite database for each test."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    database_module.create_tables_if_not_exist(conn)
    yield conn
    conn.close()

# --- Core Functionality Tests ---

def test_create_habit_and_store(db_conn):
    """Tests if a new habit can be created and stored correctly."""
    creation_ts = datetime.datetime(2024, 1, 1, 10, 0, 0)
    counter = Counter("Test Habit", "This is a test habit", "Daily", creation_date=creation_ts)
    counter.store(db_conn)
    assert counter.habit_id is not None
    loaded_counter = get_counter(db_conn, "Test Habit")
    assert loaded_counter is not None
    assert loaded_counter.name == "Test Habit"
    assert datetime.datetime.fromisoformat(loaded_counter.creation_date.isoformat()) == creation_ts

def test_increment_habit_adds_to_counters_table(db_conn):
    """Tests if incrementing a habit correctly adds a timestamp to its completion records."""
    counter = Counter("Exercise Daily", "Daily exercise routine", "Daily")
    counter.store(db_conn)
    increment_time = datetime.datetime(2024, 6, 1, 8, 30, 0)
    counter.increment(db_conn, increment_time=increment_time)
    reloaded_counter = get_counter(db_conn, "Exercise Daily")
    reloaded_counter.load_increment_dates(db_conn)
    assert increment_time in reloaded_counter._increment_dates

def test_reset_habit_clears_increments(db_conn):
    """Tests if resetting a habit clears all its completion data but keeps the habit."""
    counter = Counter("Read Every Day", "Daily reading goal", "Daily")
    counter.store(db_conn)
    counter.increment(db_conn, increment_time=datetime.datetime(2024, 6, 1))
    counter.reset(db_conn)
    reloaded_counter = get_counter(db_conn, "Read Every Day")
    reloaded_counter.load_increment_dates(db_conn)
    assert len(reloaded_counter._increment_dates) == 0

def test_delete_habit_removes_from_db(db_conn):
    """Tests if deleting a habit removes it and its associated data completely."""
    counter = Counter("Old Habit", "To be deleted", "Daily")
    counter.store(db_conn)
    habit_id_to_delete = counter.habit_id
    counter.delete(db_conn)
    assert get_counter(db_conn, "Old Habit") is None
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM counters WHERE habit_id = ?", (habit_id_to_delete,))
    assert len(cursor.fetchall()) == 0

# --- Analytics and Streak Logic Tests (Tutor Feedback) ---

@freeze_time("2025-06-22")
def test_weekly_streak_calculation(db_conn):
    """Tests the streak logic specifically for a weekly habit."""
    habit = Counter("Weekly Review", "Review progress", "Weekly", creation_date=datetime.datetime(2025, 5, 1))
    habit.store(db_conn)
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 2))
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 10))
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 18))
    assert calculate_current_streak_for_habit(db_conn, "Weekly Review") == 3
    assert calculate_longest_streak_for_habit(db_conn, "Weekly Review") == 3

@freeze_time("2025-06-22")
def test_broken_streak_logic(db_conn):
    """Tests that streaks are correctly calculated when there is a gap in completions."""
    habit = Counter("Read Daily", "Reading a book", "Daily", creation_date=datetime.datetime(2025, 6, 1))
    habit.store(db_conn)
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 10))
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 11))
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 13))
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 14))
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 15))
    assert calculate_longest_streak_for_habit(db_conn, "Read Daily") == 3
    assert calculate_current_streak_for_habit(db_conn, "Read Daily") == 0

def test_analyse_list_by_periodicity(db_conn):
    """Tests the analytics function for listing habits by periodicity."""
    Counter("Daily Task", "A daily habit", "Daily").store(db_conn)
    Counter("Weekly Task", "A weekly habit", "Weekly").store(db_conn)
    Counter("Another Daily Task", "Another one", "Daily").store(db_conn)
    daily_habits = list_habits_by_periodicity_details(db_conn, "Daily")
    daily_habit_names = [h.name for h in daily_habits]
    assert len(daily_habits) == 2
    assert "Daily Task" in daily_habit_names
    weekly_habits = list_habits_by_periodicity_details(db_conn, "Weekly")
    assert len(weekly_habits) == 1
    assert "Weekly Task" == weekly_habits[0].name

def test_longest_streak_all_habits_logic(db_conn):
    """Tests that the overall longest streak is correctly identified across all habits."""
    habit1 = Counter("Reading", "Books", "Daily", creation_date=datetime.datetime(2024, 6, 1))
    habit1.store(db_conn)
    habit1.increment(db_conn, increment_time=datetime.datetime(2024, 6, 2))
    habit1.increment(db_conn, increment_time=datetime.datetime(2024, 6, 3))
    habit1.increment(db_conn, increment_time=datetime.datetime(2024, 6, 4))
    habit2 = Counter("Workout", "Gym", "Daily", creation_date=datetime.datetime(2024, 6, 1))
    habit2.store(db_conn)
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 2))
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 3))
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 4))
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 5))
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 6))
    assert longest_streak_all_habits(db_conn) == 5

# --- ADDED BACK FOR FULL COVERAGE ---
def test_get_habits_list_from_db(db_conn):
    """Tests the basic db helper function to retrieve all habit names."""
    Counter("Habit Alpha", "Desc A", "Daily").store(db_conn)
    Counter("Habit Beta", "Desc B", "Weekly").store(db_conn)
    habits = database_module.get_habits_list(db_conn)
    assert "Habit Alpha" in habits
    assert "Habit Beta" in habits
    assert len(habits) == 2