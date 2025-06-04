# counter.py
import sqlite3
import datetime
from typing import List, Optional
import db as database_module  # Using 'as' to avoid naming conflict if any


class Counter:
    def __init__(self, name: str, description: str, periodicity: str,
                 creation_date: Optional[datetime.datetime] = None,
                 habit_id: Optional[int] = None,
                 db_connection=None):  # Allow passing db connection for efficiency

        if periodicity not in ['Daily', 'Weekly']:
            raise ValueError("Periodicity must be 'Daily' or 'Weekly'.")

        self.name: str = name
        self.description: str = description
        self.periodicity: str = periodicity  # 'Daily' or 'Weekly'
        self.creation_date: datetime.datetime = (creation_date if creation_date
                                                 else datetime.datetime.now()).replace(microsecond=0)
        self.habit_id: Optional[int] = habit_id  # Will be set after storing or when loading

        # This list will be populated when needed, e.g., for streak calculation
        self._increment_dates: List[datetime.datetime] = []

    def store(self, db: Optional[sqlite3.Connection] = None):
        """Stores the new habit definition in the database."""
        close_conn_after = False
        if db is None:
            db = database_module.get_db()
            close_conn_after = True

        try:
            database_module.add_habit_to_db(db, self.name, self.description, self.periodicity, self.creation_date)
            self.habit_id = database_module.get_habit_id_by_name(db, self.name)  # Fetch the assigned ID
            print(f"Habit '{self.name}' stored with ID {self.habit_id}.")
        except Exception as e:
            print(f"Error storing habit '{self.name}': {e}")
            # If it's due to UNIQUE constraint, self.habit_id might not be set correctly.
            # Caller (main.py) should handle this.
            raise
        finally:
            if close_conn_after:
                db.close()

    def increment(self, db: Optional[sqlite3.Connection] = None, increment_time: Optional[datetime.datetime] = None):
        """Records an increment (completion) for the habit for the given time (or now)."""
        if not self.habit_id:
            print(f"Cannot increment habit '{self.name}' without a valid habit_id. Was it stored correctly?")
            return

        close_conn_after = False
        if db is None:
            db = database_module.get_db()
            close_conn_after = True

        actual_increment_time = (increment_time if increment_time
                                 else datetime.datetime.now()).replace(microsecond=0)

        # Optional: Prevent duplicate increments for the same day if it's a daily habit
        # This would require fetching existing increments for the day first.
        # For now, we allow multiple increments per day, streak logic will handle uniqueness by day/week.

        database_module.add_increment_date_to_db(db, self.habit_id, actual_increment_time)
        self._increment_dates.append(actual_increment_time)  # Keep local cache updated
        self._increment_dates.sort()
        print(f"Increment recorded for '{self.name}' on {actual_increment_time.strftime('%Y-%m-%d %H:%M')}.")

        if close_conn_after:
            db.close()

    def reset(self, db: Optional[sqlite3.Connection] = None):
        """Resets all increments for this habit."""
        if not self.habit_id:
            print(f"Cannot reset habit '{self.name}' without a valid habit_id.")
            return

        close_conn_after = False
        if db is None:
            db = database_module.get_db()
            close_conn_after = True

        database_module.reset_increments_for_habit(db, self.habit_id)
        self._increment_dates = []  # Clear local cache
        print(f"All increments for habit '{self.name}' have been reset.")

        if close_conn_after:
            db.close()

    def delete(self, db: Optional[sqlite3.Connection] = None):
        """Deletes the habit and all its increments from the database."""
        if not self.habit_id:
            # Try to fetch ID if not set, maybe it was loaded without it
            temp_db = database_module.get_db() if db is None else db
            fetched_id = database_module.get_habit_id_by_name(temp_db, self.name)
            if fetched_id:
                self.habit_id = fetched_id
            else:
                print(f"Cannot delete habit '{self.name}': ID unknown and not found in DB by name.")
                if db is None and temp_db: temp_db.close()
                return
            if db is None and temp_db: temp_db.close()

        close_conn_after = False
        if db is None:
            db = database_module.get_db()
            close_conn_after = True

        database_module.delete_habit_from_db(db, self.habit_id)
        print(f"Habit '{self.name}' and all its data deleted.")

        if close_conn_after:
            db.close()

    def load_increment_dates(self, db: Optional[sqlite3.Connection] = None):
        """Loads/refreshes increment dates from the DB into the object's internal list."""
        if not self.habit_id:
            print(f"Cannot load increments for '{self.name}' without habit_id.")
            return

        close_conn_after = False
        if db is None:
            db = database_module.get_db()
            close_conn_after = True

        self._increment_dates = database_module.get_increment_dates_for_habit(db, self.habit_id)

        if close_conn_after:
            db.close()

    # --- Streak Calculation Methods (adapted from previous Habit class) ---
    def _get_normalized_date(self, dt: datetime.datetime) -> datetime.date:
        return dt.date()

    def _get_week_start(self, dt: datetime.datetime) -> datetime.date:
        return (dt - datetime.timedelta(days=dt.weekday())).date()

    def get_current_streak(self, db_conn=None, current_system_date: Optional[datetime.datetime] = None) -> int:
        """Calculates current streak. Fetches increments if not already loaded."""
        if not self.habit_id: return 0
        self.load_increment_dates(db_conn)  # Ensure freshest data

        if not self._increment_dates: return 0

        today = self._get_normalized_date(current_system_date if current_system_date else datetime.datetime.now())

        relevant_completions = sorted(list(set(
            self._get_normalized_date(c) for c in self._increment_dates if self._get_normalized_date(c) <= today
        )))
        if self.periodicity == "Weekly":
            relevant_completions = sorted(list(set(
                self._get_week_start(datetime.datetime.combine(c, datetime.time.min)) for c in relevant_completions
            )))

        if not relevant_completions: return 0
        streak = 0

        if self.periodicity == "Daily":
            current_check_date = today
            while current_check_date in relevant_completions:
                streak += 1
                # Ensure we don't go before creation for streak purposes
                if current_check_date == self._get_normalized_date(self.creation_date): break
                current_check_date -= datetime.timedelta(days=1)
                if current_check_date < self._get_normalized_date(self.creation_date): break
        elif self.periodicity == "Weekly":
            current_check_week_start = self._get_week_start(datetime.datetime.combine(today, datetime.time.min))
            while current_check_week_start in relevant_completions:
                streak += 1
                if current_check_week_start == self._get_week_start(self.creation_date): break
                current_check_week_start -= datetime.timedelta(weeks=1)
                if current_check_week_start < self._get_week_start(self.creation_date): break
        return streak

    def get_longest_streak(self, db_conn=None) -> int:
        """Calculates the longest streak ever achieved. Fetches increments if not loaded."""
        if not self.habit_id: return 0
        self.load_increment_dates(db_conn)  # Ensure freshest data

        if not self._increment_dates: return 0

        if self.periodicity == "Daily":
            processed_dates = sorted(list(set(
                self._get_normalized_date(c) for c in self._increment_dates
                if self._get_normalized_date(c) >= self._get_normalized_date(self.creation_date)  # Filter by creation
            )))
            delta = datetime.timedelta(days=1)
        elif self.periodicity == "Weekly":
            processed_dates = sorted(list(set(
                self._get_week_start(c) for c in self._increment_dates
                if self._get_week_start(c) >= self._get_week_start(self.creation_date)  # Filter by creation
            )))
            delta = datetime.timedelta(weeks=1)
        else:
            return 0

        if not processed_dates: return 0
        max_streak = 0
        current_streak = 0

        for i, date_completed in enumerate(processed_dates):
            if i == 0:
                current_streak = 1
            else:
                if date_completed == processed_dates[i - 1] + delta:
                    current_streak += 1
                else:
                    max_streak = max(max_streak, current_streak)
                    current_streak = 1
        max_streak = max(max_streak, current_streak)
        return max_streak

    def __str__(self):
        # For __str__, we might not want to hit DB every time,
        # so it uses locally available info or defaults.
        # For accurate streaks in string, ensure load_increment_dates was called.
        return f"Habit: '{self.name}' ({self.periodicity}), Desc: {self.description}, Created: {self.creation_date.strftime('%Y-%m-%d')}"


# Helper function that your main.py uses, adapted to this structure
def get_counter(db_conn: sqlite3.Connection, name: str) -> Optional[Counter]:
    """Fetches habit details and creates a Counter object."""
    habit_details = database_module.get_habit_details_by_name(db_conn, name)
    if habit_details:
        counter_obj = Counter(
            name=habit_details['name'],
            description=habit_details['description'],
            periodicity=habit_details['periodicity'],
            creation_date=datetime.datetime.fromisoformat(habit_details['creation_date']),
            habit_id=habit_details['id']
        )
        # Optionally load increments here, or let methods do it lazily
        # counter_obj.load_increment_dates(db_conn)
        return counter_obj
    return None
