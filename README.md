# Habit Tracking Application

**Course:** Object-Oriented and Functional Programming with Python
**Institution:** IU International University of Applied Sciences

---

## 1. Overview

This project is a command-line interface (CLI) application designed for tracking daily and weekly habits. Developed in Python, it utilizes an SQLite database for persistent storage and an interactive CLI experience powered by the `questionary` library. Users can create, manage, complete (increment), and analyze their habits, with a focus on tracking completion streaks.

The application adheres to object-oriented principles for habit representation (via a `Counter` class) and incorporates functional programming concepts for data analysis tasks. It is built with a focus on maintainability and robustness, featuring a modular structure, a centralized configuration, custom error handling, and a formal logging system.

---

## 2. Core Features

* **Interactive CLI**: A user-friendly, menu-driven interface for easy navigation.
* **Habit Management**:
    * Create new habits with a name, description, and periodicity (Daily or Weekly).
    * Log habit completions ("Increment Habit").
    * Reset all completion data for a specific habit.
    * Delete habits permanently from the database.
* **Streak Tracking**:
    * Automatic calculation of current and historically longest streaks for each habit.
    * Streaks are based on consecutive periods of completion (days for Daily habits, weeks for Weekly habits), respecting each habit's creation date.
* **Data Persistence**:
    * All habit definitions and completion timestamps are stored in a local SQLite database.
    * The database schema includes indexes for performance and `UNIQUE` constraints for data integrity.
* **Habit Analysis**:
    * List all currently tracked habits with their live streak information.
    * Filter and display habits based on their periodicity.
    * View the longest streak achieved across all habits.
    * View the longest and current streak for any specific habit.
* **Predefined Data**:
    * Includes a script (`preload_db.py`) to populate the database with 5 example habits and 4 weeks of sample completion data for demonstration and testing.

---

## 3. Technical Specifications

* **Programming Language**: Python (3.7+ recommended)
* **Database**: SQLite (via the built-in `sqlite3` module)
* **Key Libraries**:
    * `questionary`: For building the interactive command-line interface.
    * `datetime`: For all date and time operations.
    * `pytest` & `freezegun`: For automated unit testing and time control.
* **Development Tooling**: The project is structured to be used with standard Python development tools like `black` (code formatter), `flake8` (linter), and `mypy` (type checker) for maintaining high code quality.

---

## 4. Installation and Setup Guide

Follow these steps to get the application running on your local machine.

**Prerequisites:**
* Python 3.7 or newer installed.
* `pip` (Python package installer).

**Steps:**

1.  **Clone the Project:**
    * Clone the repository from GitHub using the following commands:
        ```bash
        git clone https://github.com/siliconsagenerd/My_Habit_Tracker_App
        cd My_Habit_Tracker_App
        ```

2.  **Set Up a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    ```
    Activate the environment:
    * **macOS/Linux:** `source venv/bin/activate`
    * **Windows:** `venv\Scripts\activate`

3.  **Install Required Libraries:**
    All necessary Python packages are listed in `requirements.txt`. Install them using:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize and Preload the Database:**
    To create the SQLite database file and populate it with predefined habits and sample data, run the preload script:
    ```bash
    python preload_db.py
    ```
    *This step is crucial for initial setup and to have sample data available.*

---

## 5. Usage Instructions

After successful installation and database preloading, start the application.

1.  **Run the Main Application:**
    Ensure your virtual environment is activated and you are in the root directory of the project.
    ```bash
    python main.py
    ```

2.  **Navigating the CLI:**
    The application will launch an interactive menu. Use the **arrow keys** to navigate and **Enter** to select an option. Follow the on-screen prompts for each action.

---

## 6. Predefined Example Habits

The `preload_db.py` script populates the database with the following five example habits:

* Study Daily (Daily)
* Read Daily (Daily)
* Daily Workout (Daily)
* Weekly Project Review (Weekly)
* Grocery Shopping (Weekly)

---

## 7. Testing the Application

Automated unit tests are provided to ensure the reliability of core functionalities, especially the complex streak calculation logic.

**Running Tests:**

1.  Ensure all development dependencies from `requirements.txt` are installed.
2.  From the project's root directory, run:
    ```bash
    pytest
    ```
    For a more detailed (verbose) output:
    ```bash
    pytest -v
    ```

---

## 8. Project Structure

Habit-Tracker-App/
  - data/
    - user_habits.db        # SQLite database file
  - logs/
    - habit_tracker.log     # Log file for debugging and events
  - .venv/                    # Virtual environment folder
  - analyse.py                # Functions for habit analysis
  - config.py                 # Application configuration settings
  - counter.py                # Counter class for habit logic
  - db.py                     # Database interaction functions
  - exceptions.py             # Custom exception classes
  - main.py                   # Main application entry point (CLI)
  - preload_db.py             # Script for preloading sample data
  - requirements.txt          # Python package dependencies
  - schema.sql                # Database schema definition
  - test_project.py           # Unit tests
  - utils.py                  # Utility functions (e.g., logging setup)
  - README.md                 # This file

---