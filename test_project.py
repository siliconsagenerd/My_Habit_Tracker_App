# test_habits.py
import pytest
import sqlite3
import datetime
from freezegun import freeze_time

import db as database_module
from counter import Counter, get_counter
from analyse import (
    calculate_longest_streak_for_habit, # Consistent name
    calculate_current_streak_for_habit, # Consistent name
    longest_streak_all_habits
)

@pytest.fixture
def db_conn():
    """Pytest fixture for an in-memory SQLite database for each test."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    database_module.create_tables_if_not_exist(conn)
    yield conn
    conn.close()

def test_create_habit_and_store(db_conn):
    creation_ts = datetime.datetime(2024, 1, 1, 10, 0, 0)
    counter = Counter("Test Habit", "This is a test habit", "Daily", creation_date=creation_ts)
    counter.store(db_conn)
    assert counter.habit_id is not None
    loaded_counter = get_counter(db_conn, "Test Habit")
    assert loaded_counter is not None
    assert loaded_counter.name == "Test Habit"
    assert datetime.datetime.fromisoformat(loaded_counter.creation_date.isoformat()) == creation_ts


def test_increment_habit_adds_to_counters_table(db_conn):
    counter = Counter("Exercise Daily", "Daily exercise routine", "Daily")
    counter.store(db_conn)
    increment_time = datetime.datetime(2024, 6, 1, 8, 30, 0)
    counter.increment(db_conn, increment_time=increment_time)
    reloaded_counter = get_counter(db_conn, "Exercise Daily")
    reloaded_counter.load_increment_dates(db_conn)
    assert increment_time in reloaded_counter._increment_dates

def test_reset_habit_clears_increments(db_conn):
    counter = Counter("Read Every Day", "Daily reading goal", "Daily")
    counter.store(db_conn)
    counter.increment(db_conn, increment_time=datetime.datetime(2024, 6, 1))
    counter.reset(db_conn)
    reloaded_counter = get_counter(db_conn, "Read Every Day")
    reloaded_counter.load_increment_dates(db_conn)
    assert len(reloaded_counter._increment_dates) == 0

def test_delete_habit_removes_from_db(db_conn):
    counter = Counter("Old Habit", "To be deleted", "Daily")
    counter.store(db_conn)
    habit_id_to_delete = counter.habit_id
    counter.delete(db_conn)
    assert get_counter(db_conn, "Old Habit") is None
    cursor = db_conn.cursor() # Check counters directly
    cursor.execute("SELECT * FROM counters WHERE habit_id = ?", (habit_id_to_delete,))
    assert len(cursor.fetchall()) == 0


@freeze_time("2024-06-05 12:00:00")
def test_calculate_longest_streak_for_habit_logic(db_conn): # Renamed test for clarity
    counter = Counter("Daily Read", "Books", "Daily", creation_date=datetime.datetime(2024,6,1))
    counter.store(db_conn)
    counter.increment(db_conn, increment_time=datetime.datetime(2024, 6, 2, 10,0,0))
    counter.increment(db_conn, increment_time=datetime.datetime(2024, 6, 3, 10,0,0))
    counter.increment(db_conn, increment_time=datetime.datetime(2024, 6, 4, 10,0,0))
    streak = calculate_longest_streak_for_habit(db_conn, "Daily Read") # Consistent name
    assert streak == 3

@freeze_time("2024-06-05 12:00:00")
def test_calculate_current_streak_for_habit_logic(db_conn): # New test for current streak
    counter = Counter("Daily Walk", "Walk", "Daily", creation_date=datetime.datetime(2024,6,1))
    counter.store(db_conn)
    counter.increment(db_conn, increment_time=datetime.datetime(2024, 6, 3, 10,0,0)) # Day before yesterday
    counter.increment(db_conn, increment_time=datetime.datetime(2024, 6, 4, 10,0,0)) # Yesterday
    # Today (June 5th) not completed yet
    streak = calculate_current_streak_for_habit(db_conn, "Daily Walk") # Consistent name
    assert streak == 2


@freeze_time("2024-06-05 12:00:00")
def test_longest_streak_all_habits_logic(db_conn): # Renamed test for clarity
    habit1 = Counter("Bookworm", "Reading", "Daily", creation_date=datetime.datetime(2024,6,1))
    habit1.store(db_conn)
    habit1.increment(db_conn, increment_time=datetime.datetime(2024, 6, 2))
    habit1.increment(db_conn, increment_time=datetime.datetime(2024, 6, 3))
    habit1.increment(db_conn, increment_time=datetime.datetime(2024, 6, 4)) # Streak of 3

    habit2 = Counter("Fitness", "Workout", "Daily", creation_date=datetime.datetime(2024,6,1))
    habit2.store(db_conn)
    habit2.increment(db_conn, increment_time=datetime.datetime(2024, 6, 4)) # Streak of 1

    overall_longest = longest_streak_all_habits(db_conn)
    assert overall_longest == 3

# --- Tests for db.py helper functions ---
def test_get_habits_list_from_db(db_conn):
    Counter("Habit Alpha", "Desc A", "Daily").store(db_conn)
    Counter("Habit Beta", "Desc B", "Weekly").store(db_conn)
    habits = database_module.get_habits_list(db_conn)
    assert "Habit Alpha" in habits and "Habit Beta" in habits

def test_habit_by_periodicity_from_db(db_conn):
    Counter("Daily Task X", "Desc DX", "Daily").store(db_conn)
    Counter("Weekly Task Y", "Desc WY", "Weekly").store(db_conn)
    daily_habits = database_module.habit_by_periodicity(db_conn, "Daily")
    assert "Daily Task X" in daily_habits and "Weekly Task Y" not in daily_habits