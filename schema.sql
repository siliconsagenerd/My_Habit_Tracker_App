CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    periodicity TEXT CHECK(periodicity IN ('Daily', 'Weekly')) NOT NULL,
    creation_date TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS counters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    increment_date TIMESTAMP NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    -- Prevent duplicate increments for the same habit at the exact same second.
    UNIQUE(habit_id, increment_date)
);

-- Indexes to speed up common lookups
CREATE INDEX IF NOT EXISTS idx_habits_name ON habits(name);
CREATE INDEX IF NOT EXISTS idx_counters_habit_id ON counters(habit_id);