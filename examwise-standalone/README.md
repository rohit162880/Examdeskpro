# Examwise — Python + SQLite edition

A standalone version of the examination management assignment. It uses Python's standard library to serve the website and SQLite to store data, so there are no packages or database server to install.

## Run locally

1. Install Python 3.9 or newer.
2. Open this folder in a terminal.
3. Start the app:

   ```powershell
   python app.py
   ```

4. Visit [http://127.0.0.1:8000](http://127.0.0.1:8000).

On Windows, you can also double-click `run.bat`. Stop the server with Ctrl+C.

The app creates `examwise.sqlite3` from `schema.sql` the first time it runs. The database stays local to your copy of the project and is excluded from Git.

## Features

- Schedule exams with room, invigilator, and capacity conflict checks.
- Add students and register them for upcoming exams in their program.
- Record internal and external marks, then calculate totals, grades, and pass/fail results.
- Publish results, generate hall-ticket views, and submit revaluation requests.
- Browse SQLite tables and view or download the SQL schema.

The sample grade bands are A+ (90–100), A (80–89), B (70–79), C (60–69), D (40–59), and F (0–39), with 40 as the pass threshold.
