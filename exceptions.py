"""Custom exceptions for the habit tracking application."""

class HabitError(Exception):
    """Base exception for all custom errors in this application."""
    pass

class DatabaseError(HabitError):
    """Raised for database-related errors, like connection or query failures."""
    pass

class ValidationError(HabitError):
    """Raised for validation errors, like invalid periodicity or empty names."""
    pass

class NotFoundError(HabitError):
    """Raised when a requested resource (e.g., a habit) is not found."""
    pass