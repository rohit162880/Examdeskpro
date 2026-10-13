EXAMDESK PRO — fresh replacement project
========================================
This is a new Flask + SQLite project to replace the broken website.

RUN ON WINDOWS IN VS CODE
1. Extract ExamDesk_Pro.zip.
2. In VS Code: File > Open Folder > select ExamDesk_Pro.
3. Open Terminal > New Terminal (PowerShell; WSL is not needed).
4. Run:
   python -m pip install -r requirements.txt
   python app.py
   If python is not recognized, use `py -m pip install -r requirements.txt` and `py app.py`.
5. Open http://127.0.0.1:5000

Keep the terminal open while using the website. Press Ctrl+C to stop it.
Features: dashboard, students, courses, rooms, exam schedule with room-conflict checks,
registrations with duplicate/capacity checks, results entry/update, SQLite local storage.
Demo records are inserted only when the tables are empty. Database is examdesk.db.
Do not delete examdesk.db if you need to preserve records. Local academic demo only.
