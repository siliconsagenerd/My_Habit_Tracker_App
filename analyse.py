from datetime import datetime

from db import fetch_all_habit_names

def compute_longest_streak(db, habit_name):
    """
    Calculates the longest consecutive streak of completions for a specific habit.

    Args:
      db: The database connection.
      habit_name: The name of the habit.

    Returns:
      int: The length of the longest streak.
    """

    print('The habit is: ', habit_name)
    cursor = db.cursor()
    cursor.execute('''
        SELECT tracked_at 
        FROM progress_log
        INNER JOIN habits ON progress_log.habit_id = habits.id
        WHERE habits.name = ?
        ORDER BY tracked_at ASC
    ''', (habit_name,))
    completion_dates = cursor.fetchall()

    if not completion_dates:
        return 0

    # Ensure the dates are sorted chronologically
    dates = [
        datetime.strptime(date[0], "%Y-%m-%d %H:%M:%S")
        for date in completion_dates
    ]

    max_streak = 1
    current_streak = 1

    # Ensure the dates are sorted chronologically (this might already be done in your code)
    dates.sort()

    for i in range(0, len(dates)-1):
        if (dates[i+1] - dates[i]).days == 1:  # Increment only for exact one-day difference
            current_streak += 1
            print('The current streak is: ', current_streak)
        elif (dates[i+1] - dates[i]).days > 1:  # Reset only for gaps greater than one day
            max_streak = max(max_streak, current_streak)
            current_streak = 1
        # No need for an else block for same-day entries

    # Update max_streak one last time after the loop
    longest_streak = max(max_streak, current_streak)
    return longest_streak

def compute_longest_streak_overall(db):
    """
    Calculates the longest streak across all habits in the database.

    Args:
      db: The database connection.

    Returns:
      int: The length of the longest streak among all habits.
    """

    all_habits = fetch_all_habit_names(db)
    longest_streak = 0
    for habit in all_habits:
        habit_streak = compute_longest_streak (db, habit)
        if habit_streak > longest_streak:
            longest_streak = habit_streak

    return longest_streak
