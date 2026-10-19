# 📝 Habit Tracking Application

**Course:** Object-Oriented and Functional Programming with Python  
**Institution:** IU International University of Applied Sciences

---

## 📌 About

**Habit Tracker** is a command-line application for tracking daily and weekly habits with automatic streak calculation. Built with Python and SQLite, featuring an interactive CLI powered by `questionary`. This project demonstrates object-oriented and functional programming principles, with a clean architecture separating concerns across multiple modules. The application includes comprehensive unit tests with pytest and supports data persistence with automatic streak analytics.

**Topics:** python, sqlite3, object-oriented-programming, functional-programming, cli, questionary, pytest, habit-tracking, streak-calculation, data-persistence, iubh

---

## 🚀 Overview

A command-line application for tracking daily and weekly habits. Built with Python and SQLite, featuring an interactive CLI (via `questionary`).
Track, manage, and analyze your habits and streaks with ease.

---

## ✨ Core Features

- **Interactive CLI:** A user-friendly, menu-driven interface for easy navigation.
- **Habit Management:**
  - Create new habits with a name, description, and periodicity (Daily or Weekly).
  - Log habit completions ("Increment Habit").
  - Reset all completion data for a specific habit.
  - Delete habits permanently from the database.
- **Streak Tracking:**
  - Automatic calculation of current and historically longest streaks for each habit.
- **Data Persistence:**
  - All habit definitions and completion timestamps are stored in a local SQLite database.
- **Habit Analysis:**
  - List all currently tracked habits with their live streak information.
  - Filter and display habits based on their periodicity.
  - View the longest streak achieved across all habits.
  - View the longest and current streak for any specific habit.

---

## 🏗️ Architecture

The application is built with a clean, modular architecture to ensure it is robust and easy to maintain.

- **`main.py` (The Conductor):** Manages the user-friendly command-line interface and orchestrates the application flow.
- **`counter.py` (The Brains):** The object-oriented `Counter` class represents each habit and handles all core logic, including streak calculations.
- **`db.py` (The Memory):** A dedicated layer that manages all interactions with the SQLite database.
- **`analyse.py` (The Analyst):** A functional module that provides all high-level data analysis.

---

## 📁 Project Structure
Habit-Tracker-App/
├── .venv/                  # Virtual environment folder
├── data/
│   └── user_habits.db      # SQLite database file (created on run)
├── logs/
│   └── habit_tracker.log   # Log file (created on run)
├── analyse.py              # Functions for habit analysis
├── config.py               # Application configuration settings
├── counter.py              # Counter class for habit logic
├── db.py                   # Database interaction functions
├── exceptions.py           # Custom exception classes
├── main.py                 # Main application entry point (CLI)
├── preload_db.py           # Script for preloading sample data
├── requirements.txt        # Python package dependencies
├── schema.sql              # Database schema definition
├── test_project.py         # Unit tests
├── utils.py                # Utility functions
├── .gitignore              # Specifies files for Git to ignore
└── README.md               # This file

---

## ⚙️ Installation and Setup

Follow these steps to get the application running on your local machine.

**Prerequisites:**
- Python 3.7 or newer
- `pip` (Python package installer)

**Steps:**

1.  **Clone the Project:**
    ```bash
    git clone [https://github.com/siliconsagenerd/My_Habit_Tracker_App](https://github.com/siliconsagenerd/My_Habit_Tracker_App)
    cd My_Habit_Tracker_App
    ```

2.  **Set Up a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Required Libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Database (Run This Once):**
    *\*For the very first time you use the application, you must run this script to create the database and load sample data.*
    ```bash
    python preload_db.py
    ```

---

## ▶️ Usage and Workflows

### For Personal Use
After the initial setup, run the main application. This will use your existing database and save all your progress.

```bash
python main.py
```
Use arrow keys to navigate, Enter to select.
Follow on-screen prompts for each action.

### Note:
To reset the database to its original state, run:
```bash
python preload_db.py
```
##### Warning:This will delete all your current habits and progress!

---

## 🧪 Testing
Automated unit tests ensure reliability, especially for streak logic.

#### Run all tests:
```bash
python -m pytest
```
#### Verbose output:
```bash
python -m pytest -v
``` 
<hr>
