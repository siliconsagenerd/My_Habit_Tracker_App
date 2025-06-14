# Habit Tracking Application

**Course:** Object-Oriented and Functional Programming with Python
**Institution:** IU International University of Applied Sciences

---

## 1. Overview

This project is a command-line interface (CLI) application designed for tracking daily and weekly habits. Developed in Python, it utilizes an SQLite database for persistent storage and an interactive CLI experience powered by the `questionary` library. Users can create, manage, complete (increment), and analyze their habits, with a focus on tracking completion streaks.

The application adheres to object-oriented principles for habit representation (via a `Counter` class) and incorporates functional programming concepts for data analysis tasks.

---

## 2. Core Features

* **Interactive CLI**: User-friendly navigation using arrow keys and prompts via `questionary`.
* **Habit Management**:
    * Create new habits with a name, description, and periodicity (Daily or Weekly).
    * Log habit completions ("Increment Habit").
    * Reset all completion data for a specific habit.
    * Delete habits permanently from the database.
* **Streak Tracking**:
    * Automatic calculation of current and historically longest streaks for each habit.
    * Streaks are based on consecutive periods of completion (days for Daily habits, weeks for Weekly habits).
* **Data Persistence**:
    * All habit definitions and completion timestamps are stored in a local SQLite database (`data/user_habits.db`).
* **Habit Analysis**:
    * List all currently tracked habits with their streak information.
    * Filter and display habits based on their periodicity (Daily/Weekly).
    * View the longest streak achieved across all habits.
    * View the longest and current streak for any specific habit.
* **Predefined Data**:
    * Includes a script (`preload_db.py`) to populate the database with 5 example habits and 4 weeks of sample completion data for demonstration and testing.

---

## 3. Technical Specifications

* **Programming Language**: Python (version 3.7+ recommended)
* **Database**: SQLite (using the built-in `sqlite3` module)
* **Key Libraries**:
    * `questionary`: For building the interactive command-line interface.
    * `datetime`: For all date and time operations.
    * `os`: For operating system interactions like path management.
    * `pytest` & `freezegun`: For automated unit testing and time control during tests.

---

## 4. Installation and Setup Guide

Follow these steps to get the application running on your local machine:

**Prerequisites:**
* Python 3.7 or newer installed.
* `pip` (Python package installer).

**Steps:**

1.  **Download or Clone the Project:**
    * Clone the repository from GitHub using the following commands:
        ```bash
        git clone [https://github.com/siliconsagenerd/My_Habit_Tracker_App](https://github.com/siliconsagenerd/My_Habit_Tracker_App)
        cd My_Habit_Tracker_App
        ```

2.  **Set Up a Virtual Environment** (Recommended for isolating project dependencies):
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
    To create the SQLite database file (`data/user_habits.db`), set up the required tables, and populate it with predefined habits and sample completion data, run the preload script:
    ```bash
    python preload_db.py
    ```
    *This step is crucial for initial setup and to have sample data available for testing and demonstration.*

---

## 5. Usage Instructions

After successful installation and database preloading, start the application:

1.  **Run the Main Application:**
    Ensure your virtual environment is activated and you are in the root directory of the project.
    ```bash
    python main.py
    ```

2.  **Navigating the CLI:**
    The application will launch an interactive menu. Use the **arrow keys** to highlight an option and **Enter** to select it.

    * **Create a New Habit**: Follow prompts to enter the habit's name, a brief description, and choose its periodicity (Daily/Weekly).
    * **Increment Habit (Log Completion)**: Choose a habit you've completed. This records a completion for the current time and updates streak calculations.
    * **Reset Habit**: Choose a habit to clear all its recorded completions. This will reset its streaks to zero.
    * **Analyse Habits**: A sub-menu provides various analysis options, including listing habits, filtering by periodicity, and viewing specific streak data.
    * **Delete Habit**: Choose a habit to remove it and all its associated data from the database.
    * **Exit**: Close the application.

---

## 6. Predefined Example Habits

The `preload_db.py` script populates the database with the following example habits to showcase functionality:

* Study Daily (Daily)
* Read Daily (Daily)
* Daily Workout (Daily)
* Weekly Project Review (Weekly)
* Grocery Shopping (Weekly)

---

## 7. Testing the Application

Automated unit tests are provided to ensure the reliability of core functionalities. The tests utilize the `pytest` framework and `freezegun` for consistent time-based testing.

**Running Tests:**

1.  Ensure `pytest` and `freezegun` are installed (they are included in `requirements.txt`).
2.  From the project's root directory, run:
    ```bash
    pytest
    ```
    For a more detailed (verbose) output:
    ```bash
    pytest -v
    ```
    *(This assumes your test file is named `test_project.py` or `test_habits.py` and is discoverable by `pytest`)*.

---

## 8. Project Structure (Illustrative)

Habit-Tracker-App/
  - data/
    - user_habits.db        # SQLite database file
  - .venv/                    # Virtual environment folder (if created)
  - analyse.py                # Functions for habit analysis
  - counter.py                # Counter class for habit logic
  - db.py                     # Database interaction functions
  - main.py                   # Main application entry point (CLI)
  - preload_db.py             # Script for preloading sample data
  - test_project.py           # Unit tests (example using pytest)
  - README.md                 # This file
  - requirements.txt          # Python package dependencies

---

## 9. Further Development (Optional)

This application serves as a foundational habit tracker. Potential future enhancements could include:
* A graphical user interface (GUI) or web interface.
* More detailed statistical analysis and visualizations.
* User authentication for multi-user support.
* Reminder notifications.
* Export/import functionality for habit data.