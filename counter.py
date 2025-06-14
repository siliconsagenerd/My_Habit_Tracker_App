# counter.py
import datetime
import sqlite3
from typing import List, Optional, Union # <-- Import Union for type hinting

import db as database_module

class Counter:
    """Represents a single habit, encapsulating its data and business logic."""

    def __init__(self, name: str, description: str, periodicity: str,
                 creation_date: Optional[datetime.datetime] = None,
                 habit_id: Optional[int] = None):

        if not name or not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Name cannot be empty and must be a string")
        # Allow empty description
        if not isinstance(description, str):
            raise ValueError("Description must be a string")

        if periodicity not in ['Daily', 'Weekly']:
            raise ValueError("Periodicity must be 'Daily' or 'Weekly'.")

        self.name: str = name.strip()
        self.description: str = description.strip()
        self.periodicity: str = periodicity
        self.creation_date: datetime.datetime = (creation_date or datetime.datetime.now()).replace(microsecond=0)
        self.habit_id: Optional[int] = habit_id
        self._increment_dates: List[datetime.datetime] = []

    def store(self, db: sqlite3.Connection) -> None:
        """Stores the new habit definition in the database."""
        if not db:
            raise ValueError("Database connection is required")

        try:
            database_module.add_habit_to_db(db, self.name, self.description, self.periodicity, self.creation_date)
            self.habit_id = database_module.get_habit_id_by_name(db, self.name)
            if self.habit_id:
                print(f"Habit '{self.name}' stored with ID {self.habit_id}.")
            else:
                raise RuntimeError(f"Failed to retrieve ID for newly stored habit '{self.name}'")
        except Exception as e:
            print(f"Error storing habit '{self.name}': {e}")
            raise

    def increment(self, db: sqlite3.Connection, increment_time: Optional[datetime.datetime] = None) -> None:
        """Records a completion for the habit."""
        if not db:
            raise ValueError("Database connection is required")

        if not self.habit_id:
            self.habit_id = database_module.get_habit_id_by_name(db, self.name)
            if not self.habit_id:
                raise ValueError(f"Cannot increment habit '{self.name}'. Please ensure it is stored correctly.")

        actual_increment_time = (increment_time or datetime.datetime.now()).replace(microsecond=0)
        database_module.add_increment_date_to_db(db, self.habit_id, actual_increment_time)
        self._increment_dates.append(actual_increment_time)
        print(f"Increment recorded for '{self.name}' on {actual_increment_time.strftime('%Y-%m-%d %H:%M')}.")

    def reset(self, db: sqlite3.Connection) -> None:
        """Resets all completion records for this habit."""
        if not db:
            raise ValueError("Database connection is required")

        if not self.habit_id:
            self.habit_id = database_module.get_habit_id_by_name(db, self.name)
            if not self.habit_id:
                raise ValueError(f"Cannot reset habit '{self.name}': ID unknown.")

        database_module.reset_increments_for_habit(db, self.habit_id)
        self._increment_dates = []
        print(f"All increments for habit '{self.name}' have been reset.")

    def delete(self, db: sqlite3.Connection) -> None:
        """Deletes the habit and all its data from the database."""
        if not db:
            raise ValueError("Database connection is required")

        if not self.habit_id:
            self.habit_id = database_module.get_habit_id_by_name(db, self.name)
            if not self.habit_id:
                raise ValueError(f"Cannot delete habit '{self.name}': ID unknown.")

        database_module.delete_habit_from_db(db, self.habit_id)
        print(f"Habit '{self.name}' and all its data deleted.")

    def load_increment_dates(self, db: sqlite3.Connection) -> None:
        """Loads or refreshes completion dates from the DB into the object's internal cache."""
        if not db:
            raise ValueError("Database connection is required")

        if not self.habit_id:
            self.habit_id = database_module.get_habit_id_by_name(db, self.name)
        if self.habit_id:
            self._increment_dates = database_module.get_increment_dates_for_habit(db, self.habit_id)
        else:
            self._increment_dates = []

    @staticmethod
    def _get_normalized_date(dt: datetime.datetime) -> datetime.date:
        """Returns just the date part of a datetime object."""
        return dt.date()

    @staticmethod
    # FIX 1: Updated type hint to accept date or datetime, solving the type error.
    def _get_week_start(dt: Union[datetime.datetime, datetime.date]) -> datetime.date:
        """Returns the date of Monday for the week of the given datetime or date."""
        current_date = dt if isinstance(dt, datetime.date) else dt.date()
        return current_date - datetime.timedelta(days=current_date.weekday())

    def get_current_streak(self, db_conn: sqlite3.Connection,
                           current_system_date: Optional[datetime.datetime] = None) -> int:
        """Calculates the current streak, defined as a consecutive sequence ending on or just before 'today'."""
        if not db_conn:
            raise ValueError("Database connection is required")

        self.load_increment_dates(db_conn)
        if not self._increment_dates:
            return 0

        effective_system_dt = current_system_date or datetime.datetime.now()
        effective_today_normalized = self._get_normalized_date(effective_system_dt)
        normalized_creation_date = self._get_normalized_date(self.creation_date)

        if self.periodicity == "Daily":
            all_unique_completion_periods = sorted(list(set(
                self._get_normalized_date(c) for c in self._increment_dates
                if self._get_normalized_date(c) >= normalized_creation_date
            )))
            delta = datetime.timedelta(days=1)
            min_acceptable_date = effective_today_normalized - delta
        elif self.periodicity == "Weekly":
            effective_today_week_start = self._get_week_start(effective_system_dt)
            normalized_creation_week_start = self._get_week_start(self.creation_date)
            all_unique_completion_periods = sorted(list(set(
                self._get_week_start(c) for c in self._increment_dates
                if self._get_week_start(c) >= normalized_creation_week_start
            )))
            delta = datetime.timedelta(weeks=1)
            # FIX 2: Reused the 'effective_today_week_start' variable here.
            min_acceptable_date = effective_today_week_start - delta
        else:
            return 0

        if not all_unique_completion_periods:
            return 0

        last_relevant_completion = None
        for period_start in reversed(all_unique_completion_periods):
            # FIX 2: Reused the 'effective_today_week_start' variable here.
            check_against_period = effective_today_normalized if self.periodicity == "Daily" else effective_today_week_start
            if period_start <= check_against_period:
                last_relevant_completion = period_start
                break

        if last_relevant_completion is None or last_relevant_completion < min_acceptable_date:
            return 0

        current_streak = 0
        expected_period = last_relevant_completion
        start_index = all_unique_completion_periods.index(last_relevant_completion)

        for i in range(start_index, -1, -1):
            if all_unique_completion_periods[i] == expected_period:
                current_streak += 1
                expected_period -= delta
            else:
                break
        return current_streak

    def get_longest_streak(self, db_conn: sqlite3.Connection) -> int:
        """Calculates the longest streak ever achieved for the habit."""
        if not db_conn:
            raise ValueError("Database connection is required")

        self.load_increment_dates(db_conn)
        if not self._increment_dates:
            return 0

        min_period_start = (self._get_normalized_date(self.creation_date) if self.periodicity == "Daily"
                            else self._get_week_start(self.creation_date))

        if self.periodicity == "Daily":
            processed_periods = sorted(list(set(
                self._get_normalized_date(c) for c in self._increment_dates
                if self._get_normalized_date(c) >= min_period_start
            )))
            delta = datetime.timedelta(days=1)
        elif self.periodicity == "Weekly":
            processed_periods = sorted(list(set(
                self._get_week_start(c) for c in self._increment_dates
                if self._get_week_start(c) >= min_period_start
            )))
            delta = datetime.timedelta(weeks=1)
        else:
            return 0

        if not processed_periods:
            return 0

        max_streak = current_streak = 0
        for i, period in enumerate(processed_periods):
            if i == 0 or period != processed_periods[i - 1] + delta:
                current_streak = 1
            else:
                current_streak += 1
            max_streak = max(max_streak, current_streak)
        return max_streak

    def __str__(self):
        return f"Habit: '{self.name}' ({self.periodicity}), Created: {self.creation_date.strftime('%Y-%m-%d')}"

def get_counter(db_conn: sqlite3.Connection, name: str) -> Optional[Counter]:
    """Helper to fetch habit details from the DB and create a Counter object."""
    if not db_conn:
        raise ValueError("Database connection is required")
    if not name or not isinstance(name, str):
        raise ValueError("Habit name is required and must be a string")

    habit_details = database_module.get_habit_details_by_name(db_conn, name)
    if habit_details:
        return Counter(
            name=habit_details['name'],
            description=habit_details['description'],
            periodicity=habit_details['periodicity'],
            creation_date=datetime.datetime.fromisoformat(habit_details['creation_date']),
            habit_id=habit_details['id']
        )
    return None