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
    # Use :memory: to create a fresh, temporary database for each test function
    conn = sqlite3.connect(':memory:')
    # Row factory allows accessing columns by name
    conn.row_factory = sqlite3.Row
    # Ensure tables are created before each test
    database_module.create_tables_if_not_exist(conn)
    yield conn
    # Teardown: close the connection after the test is done
    conn.close()


# --- Your Existing Tests (Still Important!) ---

def test_create_habit_and_store(db_conn):
    """Tests if a new habit can be created and stored correctly."""
    creation_ts = datetime.datetime(2024, 1, 1, 10, 0, 0)
    counter = Counter("Test Habit", "This is a test habit", "Daily", creation_date=creation_ts)
    counter.store(db_conn)
    assert counter.habit_id is not None, "Stored habit should have an ID"

    loaded_counter = get_counter(db_conn, "Test Habit")
    assert loaded_counter is not None, "Habit should be retrievable from the DB"
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
    assert increment_time in reloaded_counter._increment_dates, "Increment date should be in the list"


def test_reset_habit_clears_increments(db_conn):
    """Tests if resetting a habit clears all its completion data but keeps the habit."""
    counter = Counter("Read Every Day", "Daily reading goal", "Daily")
    counter.store(db_conn)
    counter.increment(db_conn, increment_time=datetime.datetime(2024, 6, 1))
    counter.reset(db_conn)

    reloaded_counter = get_counter(db_conn, "Read Every Day")
    reloaded_counter.load_increment_dates(db_conn)
    assert len(reloaded_counter._increment_dates) == 0, "Increment dates should be empty after reset"


def test_delete_habit_removes_from_db(db_conn):
    """Tests if deleting a habit removes it and its associated data completely."""
    counter = Counter("Old Habit", "To be deleted", "Daily")
    counter.store(db_conn)
    habit_id_to_delete = counter.habit_id

    counter.delete(db_conn)

    assert get_counter(db_conn, "Old Habit") is None, "Deleted habit should not be found"
    # Verify that the associated counters are also gone (due to ON DELETE CASCADE)
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM counters WHERE habit_id = ?", (habit_id_to_delete,))
    assert len(cursor.fetchall()) == 0, "Counters for deleted habit should be removed"


# --- New and Enhanced Tests (To Address Tutor Feedback) ---

@freeze_time("2025-06-22")  # Sunday
def test_weekly_streak_calculation(db_conn):
    """Tests the streak logic specifically for a weekly habit."""
    # This test checks if the app correctly identifies streaks across different weeks.
    habit = Counter("Weekly Review", "Review progress", "Weekly", creation_date=datetime.datetime(2025, 5, 1))
    habit.store(db_conn)

    # Completions for 3 consecutive weeks
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 2))  # Monday of Week 1
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 10))  # Tuesday of Week 2
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 18))  # Wednesday of Week 3 (this week)

    # We are currently in Week 3, so the current streak should be 3
    assert calculate_current_streak_for_habit(db_conn, "Weekly Review") == 3
    assert calculate_longest_streak_for_habit(db_conn, "Weekly Review") == 3


@freeze_time("2025-06-22")
def test_broken_streak_logic(db_conn):
    """Tests that streaks are correctly calculated when there is a gap in completions."""
    habit = Counter("Daily Meditation", "Mindfulness", "Daily", creation_date=datetime.datetime(2025, 6, 1))
    habit.store(db_conn)

    # Streak 1 (length 2)
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 10))
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 11))
    # Gap on June 12
    # Streak 2 (length 3)
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 13))
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 14))
    habit.increment(db_conn, increment_time=datetime.datetime(2025, 6, 15))

    # The longest streak should be 3, not the total of 5.
    assert calculate_longest_streak_for_habit(db_conn, "Daily Meditation") == 3
    # The current streak is 0 because the last completion was on the 15th.
    assert calculate_current_streak_for_habit(db_conn, "Daily Meditation") == 0


def test_analyse_list_by_periodicity(db_conn):
    """Tests the analytics function for listing habits by periodicity."""
    # This directly tests a function from the analyse.py module.
    Counter("Daily Task", "A daily habit", "Daily").store(db_conn)
    Counter("Weekly Task", "A weekly habit", "Weekly").store(db_conn)
    Counter("Another Daily Task", "Another one", "Daily").store(db_conn)

    # Fetch all daily habits
    daily_habits = list_habits_by_periodicity_details(db_conn, "Daily")
    daily_habit_names = [h.name for h in daily_habits]

    assert len(daily_habits) == 2
    assert "Daily Task" in daily_habit_names
    assert "Another Daily Task" in daily_habit_names
    assert "Weekly Task" not in daily_habit_names

    # Fetch all weekly habits
    weekly_habits = list_habits_by_periodicity_details(db_conn, "Weekly")
    weekly_habit_names = [h.name for h in weekly_habits]

    assert len(weekly_habits) == 1
    assert "Weekly Task" in weekly_habit_names
    assert "Daily Task" not in weekly_habit_names


def test_longest_streak_all_habits_logic(db_conn):
    """Tests that the overall longest streak is correctly identified across all habits."""
    # Streak of 3
    habit1 = Counter("Reading", "Books", "Daily", creation_date=datetime.datetime(2024, 6, 1))
    habit1.store(db_conn)
    habit1.increment(db_conn, increment_time=datetime.datetime(2024, 6, 2))
    habit1.increment(db_conn, increment_time=datetime.datetime(2024, 6, 3))
    habit1.increment(db_conn, increment_time=datetime.datetime(2024, 6, 4))

    # Streak of 5
    habit2 = Counter("Workout", "Gym", "Daily", creation_date=datetime.datetime(2024, 6, 1))
    habit2.store(db_conn)
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 2))
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 3))
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 4))
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 5))
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 6))

    assert longest_streak_all_habits(db_conn) == 5