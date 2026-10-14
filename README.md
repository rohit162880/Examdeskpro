# Examination Scheduling and Result Processing System
**Project 24 — DBMS Course Assignment**  
*Author:* **Rohit**

---

## 📌 Project Overview

The **Examination Scheduling and Result Processing System** is a full-featured, database-driven web application engineered to streamline university examination operations. Managing examinations across diverse departments, semesters, and student cohorts requires rigorous coordination to avoid timetable conflicts, room double-bookings, and invigilator overlaps. 

This platform solves these institutional bottlenecks by automating **exam timetable scheduling with room clash prevention**, **invigilator assignment**, **student course registrations**, **hall ticket generation**, **marks entry**, **grade computation based on configurable grading rules**, **result publishing**, **revaluation management**, and **comprehensive reporting with SQL views**.

---

## Python + SQLite edition

For a lightweight local run with no package installs or MySQL server, see the [Examwise Python + SQLite edition](examwise-standalone/README.md). It is kept alongside this Flask + MySQL version.

---
## 🚀 Key Features

### 1. Master Data Management
- **Programmes & Courses:** Maintain degree programmes (e.g., B.Tech CSE, ECE, MECH, CIVIL) and course catalogs with semester mapping, credit weightages (1–6), and unique codes.
- **Students & Enrolments:** Store student profiles, roll numbers, admission years, and programme associations.
- **Venues & Infrastructure:** Manage examination halls with capacity tracking, building info, and projector availability.
- **Invigilator Directory:** Track faculty members by department and contact details for invigilation rosters.

### 2. Exam Scheduling & Conflict Avoidance
- **Exam Cycles & Sessions:** Create Mid-Semester, End-Semester, or Supplementary cycles with date boundaries.
- **Smart Timetable Allocation:** Schedule examinations by mapping course, venue, date, and time slot.
- **Automated Clash Prevention:** Enforces database-level unique constraints (`room_id`, `exam_date`, `start_time`) to prevent dual-booking of rooms.
- **Invigilator Allocation:** Assign invigilators to specific exam slots while preventing duplicate assignments.

### 3. Examination Registration & Hall Tickets
- **Course Registration:** Register eligible students for examinations per course and session.
- **Automated Hall Ticket Generation:** Instantly query and generate personalized student hall tickets with full timetable, date, time slots, room numbers, and venue buildings.

### 4. Marks Entry & Result Processing Engine
- **Marks Capture:** Input marks obtained (0–100 scale) with boundary validation.
- **Configurable Grading Policy:** Define dynamic cut-off ranges for letter grades (O, A+, A, B+, B, C, F) and grade points (0.0–10.0) per exam session.
- **Automated Batch Result Computation:** Calculate student grades and grade points automatically based on defined rules.
- **Result Publication Control:** Keep draft grades private until officially published by the examination authority.

### 5. Revaluation & Grievance Workflow
- **Revaluation Application:** Students can submit revaluation requests stating reasons for discrepancy.
- **Administrative Processing:** Review, approve, or reject requests and update revised marks directly reflecting in updated records.

### 6. Analytics & Institutional Reports
- **Pass Percentage Analysis:** View pass/fail statistics and pass percentages per course.
- **Grade Distribution Breakdown:** Visualize distribution curves across grade bands (O through F).
- **Interactive SQL Table Browser:** Inspect underlying MySQL tables, schema definitions, and row counts directly from the administrative UI.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.x, Flask (Jinja2 templates, session management, RESTful endpoints)
- **Database:** MySQL 8.0 (InnoDB engine, Foreign Keys, CHECK constraints, Composite UNIQUE indexes, SQL Views)
- **Database Driver:** `mysql-connector-python`
- **Frontend:** Bootstrap 5.3, Font Awesome 6, Modern Responsive CSS, HTML5, JavaScript
- **Version Control:** Git

---

## 📋 Prerequisites

Before running the project, ensure you have the following installed:
1. **Python 3.8+** ([Download Python](https://www.python.org/downloads/))
2. **MySQL Server 8.0+** ([Download MySQL](https://dev.mysql.com/downloads/mysql/)) or MySQL via XAMPP / WampServer
3. **Git** ([Download Git](https://git-scm.com/))

---

## ⚙️ Installation & Setup Guide

### Step 1: Clone or Navigate to the Project Directory
```bash
git clone https://github.com/example/exam-scheduling-system.git
cd exam-scheduling-system
```
*(Or navigate to `C:\Users\Rohit\.gemini\antigravity\scratch\exam-scheduling-system`)*

### Step 2: Set Up Virtual Environment & Dependencies
Create an isolated Python virtual environment and install the required packages:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (Linux/macOS)
# source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Configure Database Credentials
Open [`config.py`](file:///C:/Users/Rohit/.gemini/antigravity/scratch/exam-scheduling-system/config.py) and update the MySQL root password to match your local installation:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',  # <-- Enter your MySQL password here
    'database': 'exam_scheduling_db',
    'autocommit': True,
}
```

### Step 4: Import Database Schema
Log in to MySQL and run the DDL script to create the database, tables, constraints, and views:

```bash
mysql -u root -p < database/schema.sql
```
*Alternatively, you can open `database/schema.sql` inside MySQL Workbench or phpMyAdmin and execute it.*

### Step 5: Seed Sample University Data
Populate the database with realistic sample records:

```bash
mysql -u root -p < database/sample_data.sql
```

### Step 6: Launch the Web Application
Run the Flask server:

```bash
python app.py
```

Open your browser and visit:
```
http://127.0.0.1:5000
```

---

## 🖼️ Application Screenshots

| Dashboard Overview | Exam Timetable & Clash Avoidance |
| :---: | :---: |
| *![Dashboard Placeholder](screenshots/dashboard.png)*<br>*(Key Metrics, Quick Links & System Status)* | *![Schedules Placeholder](screenshots/schedules.png)*<br>*(Conflict-free Exam Slots & Room Allotment)* |

| Hall Ticket Generator | Result Processing & Analytics |
| :---: | :---: |
| *![Hall Ticket Placeholder](screenshots/hall_ticket.png)*<br>*(Instant Student Hall Ticket with Timetable)* | *![Results Placeholder](screenshots/results.png)*<br>*(Grade Distribution & Pass Percentage Reports)* |

---

## 🗄️ Database Schema

The database consists of **13 normalized tables** and **5 analytical SQL views** enforcing referential integrity.

### Tables Summary

| # | Table Name | Description | Key Constraints & Rules |
|---|---|---|---|
| 1 | `programmes` | Academic degree streams | `PRIMARY KEY (programme_id)` |
| 2 | `courses` | Departmental courses | `credits BETWEEN 1 AND 6`, `semester BETWEEN 1 AND 8` |
| 3 | `students` | Enrolled student database | `UNIQUE (roll_number)`, `UNIQUE (email)` |
| 4 | `rooms` | Exam venues and lecture halls | `capacity > 0`, `UNIQUE (room_number)` |
| 5 | `invigilators` | Faculty invigilator details | `UNIQUE (email)` |
| 6 | `exam_sessions` | Exam cycles (Mid-Sem, End-Sem) | `CHECK (end_date >= start_date)` |
| 7 | `schedules` | Examination date & room slots | `UNIQUE (room_id, exam_date, start_time)`, `CHECK (end_time > start_time)` |
| 8 | `schedule_invigilators` | Faculty assigned to slots | `UNIQUE (schedule_id, invigilator_id)`, Cascade on delete |
| 9 | `registrations` | Course registrations for exams | `UNIQUE (student_id, course_id, session_id)` |
| 10 | `marks` | Secured examination marks | `marks_obtained BETWEEN 0 AND 100`, `UNIQUE (registration_id)` |
| 11 | `grade_rules` | Session grading scale cutoffs | `UNIQUE (session_id, grade)`, `CHECK (max_marks >= min_marks)` |
| 12 | `results` | Computed final grade outcomes | `UNIQUE (registration_id)`, `is_published` flag |
| 13 | `revaluation_requests`| Student revaluation petitions | Status (`PENDING`, `APPROVED`, `REJECTED`) |

### Database Views

1. **`v_exam_schedule`**: Denormalized exam timetable with session name, course details, date, time, and room number.
2. **`v_student_results`**: Consolidates student roll numbers, names, course details, grades, grade points, and publication status.
3. **`v_hall_tickets`**: Multi-table join connecting registered students to scheduled courses, hall locations, and exam timings.
4. **`v_grade_distribution`**: Aggregates count of awarded letter grades per examination session for distribution curve analysis.
5. **`v_pass_percentage`**: Evaluates total candidates, passed count (`grade != 'F'`), failed count, and pass percentage per course.

---

## 🌐 Application Routes

| Route | HTTP Methods | Description |
|---|---|---|
| `/` | `GET` | Administrative Dashboard displaying total statistics and recent alerts |
| `/programmes` | `GET`, `POST` | List all academic programmes and add new degree programmes |
| `/programmes/<id>/delete` | `POST` | Delete an academic programme (cascades courses) |
| `/courses` | `GET`, `POST` | View courses by programme and register new subjects |
| `/courses/<id>/delete` | `POST` | Remove a course |
| `/students` | `GET`, `POST` | Student directory and new admission enrolment |
| `/students/<id>/delete` | `POST` | Delete student profile |
| `/rooms` | `GET`, `POST` | Lecture hall / room capacity inventory management |
| `/rooms/<id>/delete` | `POST` | Delete room venue |
| `/invigilators` | `GET`, `POST` | Faculty invigilator roster management |
| `/invigilators/<id>/delete` | `POST` | Remove invigilator |
| `/exam-sessions` | `GET`, `POST` | Configure exam terms (Mid-Sem, End-Sem, Supplementary) |
| `/schedules` | `GET`, `POST` | Timetable management with automated room collision validation |
| `/schedules/<id>/delete` | `POST` | Delete exam schedule slot |
| `/schedules/<id>/invigilators` | `POST` | Assign faculty invigilator to exam schedule |
| `/registrations` | `GET`, `POST` | Register students for examination courses |
| `/registrations/<id>/delete` | `POST` | Unregister a student from an exam course |
| `/marks` | `GET`, `POST` | Enter and update marks for registered candidates |
| `/grade-rules` | `GET`, `POST` | Manage grading criteria and grade point cut-offs |
| `/results` | `GET` | View computed student results and publish status |
| `/results/process/<session_id>` | `POST` | Execute batch grade computation engine |
| `/results/publish/<session_id>` | `POST` | Publish computed results to students |
| `/hall-tickets` | `GET` | Hall ticket lookup and printable generation |
| `/revaluations` | `GET`, `POST` | Revaluation filing, approval, and mark revision |
| `/reports` | `GET` | Statistical analytics, course pass percentage & grade distribution |
| `/sql-tables` | `GET` | Built-in database explorer inspecting raw tables and row counts |

---

## 📏 Core Business Rules

1. **Room Double-Booking Prevention:** A room can never host more than one examination at the same date and overlapping time window (`UNIQUE KEY unique_room_slot (room_id, exam_date, start_time)`).
2. **Examination Window Integrity:** Examination `end_time` must strictly succeed `start_time` (`CHECK(end_time > start_time)`).
3. **Session Date Integrity:** An exam session's `end_date` must be greater than or equal to `start_date`.
4. **Registration Uniqueness:** A student cannot register for the same course more than once within the same exam session (`UNIQUE (student_id, course_id, session_id)`).
5. **Marks Bounds Enforcement:** Marks obtained must be between `0.00` and `100.00` (`CHECK(marks_obtained BETWEEN 0 AND 100)`).
6. **Unique Invigilation Duty:** An invigilator cannot be assigned multiple times to the same schedule slot (`UNIQUE KEY unique_assignment (schedule_id, invigilator_id)`).
7. **Grading Exclusivity:** Grade scale rules for a session must not have overlapping letter grades (`UNIQUE KEY unique_grade (session_id, grade)`).
8. **Result Publishing Privacy:** Results are flagged as `is_published = FALSE` until an administrator executes the publishing operation.

---

## 👨‍💻 Author

- **Rohit**  
  *Examination Scheduling and Result Processing System*  
  *DBMS Course Assignment (Project 24)*
