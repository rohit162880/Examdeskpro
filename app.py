"""
Main Flask Application for the Examination Scheduling and Result Processing System.
Provides complete routing and database transactions for all academic examination operations.
"""

import datetime
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from config import DB_CONFIG, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY


# ------------------------------------------------------------------------------
# Database Helper
# ------------------------------------------------------------------------------
def get_db():
    """Establish and return a MySQL database connection."""
    return mysql.connector.connect(**DB_CONFIG)


# ------------------------------------------------------------------------------
# Template Filters for formatting dates, times, and decimals
# ------------------------------------------------------------------------------
@app.template_filter('format_time')
def format_time_filter(val):
    """Format time or timedelta values to HH:MM string."""
    if val is None:
        return ''
    if isinstance(val, datetime.timedelta):
        total_seconds = int(val.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    if isinstance(val, (datetime.time, datetime.datetime)):
        return val.strftime('%H:%M')
    return str(val)


@app.template_filter('format_date')
def format_date_filter(val):
    """Format date objects to YYYY-MM-DD string."""
    if val is None:
        return ''
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.strftime('%Y-%m-%d')
    return str(val)


@app.template_filter('format_decimal')
def format_decimal_filter(val, precision=2):
    """Format Decimal or float numbers."""
    if val is None:
        return ''
    try:
        return f"{float(val):.{precision}f}"
    except (ValueError, TypeError):
        return str(val)


# ==============================================================================
# 1. DASHBOARD
# ==============================================================================
@app.route('/')
def index():
    """Dashboard displaying summary statistics across all core database tables."""
    conn = None
    cursor = None
    stats = {
        'programmes': 0,
        'courses': 0,
        'students': 0,
        'rooms': 0,
        'invigilators': 0,
        'exam_sessions': 0,
        'schedules': 0,
        'registrations': 0,
        'marks': 0,
        'results': 0
    }
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        for table in stats.keys():
            try:
                cursor.execute(f"SELECT COUNT(*) AS total FROM `{table}`")
                row = cursor.fetchone()
                if row:
                    stats[table] = row['total']
            except mysql.connector.Error:
                stats[table] = 0

    except Exception as e:
        flash(f"Error fetching dashboard statistics: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('index.html', stats=stats)


# ==============================================================================
# 2. PROGRAMMES (CRUD)
# ==============================================================================
@app.route('/programmes', methods=['GET', 'POST'])
def programmes():
    """List all academic programmes or create a new programme."""
    conn = None
    cursor = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        duration_years = request.form.get('duration_years', 4)
        degree_type = request.form.get('degree_type', '').strip()

        if not name or not degree_type:
            flash("Programme name and degree type are required.", "error")
            return redirect(url_for('programmes'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "INSERT INTO programmes (name, duration_years, degree_type) VALUES (%s, %s, %s)",
                (name, int(duration_years), degree_type)
            )
            conn.commit()
            flash("Programme added successfully!", "success")
        except mysql.connector.IntegrityError as err:
            flash(f"Database error: {err.msg}", "error")
        except Exception as e:
            flash(f"Error adding programme: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('programmes'))

    # GET request
    programmes_list = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM programmes ORDER BY name")
        programmes_list = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading programmes: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('programmes.html', programmes=programmes_list)


@app.route('/programmes/<int:id>/delete', methods=['GET', 'POST'])
def delete_programme(id):
    """Delete an academic programme by ID."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM programmes WHERE programme_id = %s", (id,))
        conn.commit()
        flash("Programme deleted successfully!", "success")
    except mysql.connector.IntegrityError:
        flash("Cannot delete programme: it is currently referenced by courses or students.", "error")
    except Exception as e:
        flash(f"Error deleting programme: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('programmes'))


# ==============================================================================
# 3. COURSES (CRUD)
# ==============================================================================
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    """List all courses with programme names or register a new course."""
    conn = None
    cursor = None
    if request.method == 'POST':
        course_code = request.form.get('course_code', '').strip().upper()
        name = request.form.get('name', '').strip()
        credits = request.form.get('credits')
        programme_id = request.form.get('programme_id')
        semester = request.form.get('semester')

        if not course_code or not name or not credits or not programme_id or not semester:
            flash("All course fields are required.", "error")
            return redirect(url_for('courses'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "INSERT INTO courses (course_code, name, credits, programme_id, semester) VALUES (%s, %s, %s, %s, %s)",
                (course_code, name, int(credits), int(programme_id), int(semester))
            )
            conn.commit()
            flash("Course added successfully!", "success")
        except mysql.connector.IntegrityError as err:
            if err.errno == 1062:
                flash(f"Course code '{course_code}' already exists.", "error")
            else:
                flash(f"Database integrity error: {err.msg}", "error")
        except Exception as e:
            flash(f"Error adding course: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('courses'))

    # GET request
    courses_list = []
    programmes_list = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, p.name AS programme_name 
            FROM courses c 
            JOIN programmes p ON c.programme_id = p.programme_id 
            ORDER BY c.course_code
        """)
        courses_list = cursor.fetchall()

        cursor.execute("SELECT * FROM programmes ORDER BY name")
        programmes_list = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading courses: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('courses.html', courses=courses_list, programmes=programmes_list)


@app.route('/courses/<int:id>/delete', methods=['GET', 'POST'])
def delete_course(id):
    """Delete a course by ID."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM courses WHERE course_id = %s", (id,))
        conn.commit()
        flash("Course deleted successfully!", "success")
    except mysql.connector.IntegrityError:
        flash("Cannot delete course: it is referenced by existing registrations or exam schedules.", "error")
    except Exception as e:
        flash(f"Error deleting course: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('courses'))


# ==============================================================================
# 4. STUDENTS (CRUD)
# ==============================================================================
@app.route('/students', methods=['GET', 'POST'])
def students():
    """List all students or enroll a new student."""
    conn = None
    cursor = None
    if request.method == 'POST':
        roll_number = request.form.get('roll_number', '').strip().upper()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip() or None
        programme_id = request.form.get('programme_id')
        admission_year = request.form.get('admission_year')

        if not roll_number or not name or not email or not programme_id or not admission_year:
            flash("Roll number, name, email, programme, and admission year are required.", "error")
            return redirect(url_for('students'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "INSERT INTO students (roll_number, name, email, phone, programme_id, admission_year) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (roll_number, name, email, phone, int(programme_id), int(admission_year))
            )
            conn.commit()
            flash("Student enrolled successfully!", "success")
        except mysql.connector.IntegrityError as err:
            if err.errno == 1062:
                flash("A student with this roll number or email already exists.", "error")
            else:
                flash(f"Database error: {err.msg}", "error")
        except Exception as e:
            flash(f"Error enrolling student: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('students'))

    # GET request
    students_list = []
    programmes_list = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, p.name AS programme_name 
            FROM students s 
            JOIN programmes p ON s.programme_id = p.programme_id 
            ORDER BY s.roll_number
        """)
        students_list = cursor.fetchall()

        cursor.execute("SELECT * FROM programmes ORDER BY name")
        programmes_list = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading students: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('students.html', students=students_list, programmes=programmes_list)


@app.route('/students/<int:id>/delete', methods=['GET', 'POST'])
def delete_student(id):
    """Delete a student record by ID."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM students WHERE student_id = %s", (id,))
        conn.commit()
        flash("Student record deleted successfully!", "success")
    except mysql.connector.IntegrityError:
        flash("Cannot delete student: registration records or examination marks exist.", "error")
    except Exception as e:
        flash(f"Error deleting student: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('students'))


# ==============================================================================
# 5. ROOMS (CRUD)
# ==============================================================================
@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    """List examination venues or add a new exam room."""
    conn = None
    cursor = None
    if request.method == 'POST':
        room_number = request.form.get('room_number', '').strip()
        building = request.form.get('building', '').strip()
        capacity = request.form.get('capacity')
        has_projector = 1 if 'has_projector' in request.form else 0

        if not room_number or not building or not capacity:
            flash("Room number, building, and capacity are required.", "error")
            return redirect(url_for('rooms'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "INSERT INTO rooms (room_number, building, capacity, has_projector) VALUES (%s, %s, %s, %s)",
                (room_number, building, int(capacity), has_projector)
            )
            conn.commit()
            flash("Room added successfully!", "success")
        except mysql.connector.IntegrityError as err:
            if err.errno == 1062:
                flash(f"Room '{room_number}' already exists.", "error")
            else:
                flash(f"Database error: {err.msg}", "error")
        except Exception as e:
            flash(f"Error adding room: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('rooms'))

    # GET request
    rooms_list = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rooms ORDER BY room_number")
        rooms_list = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading rooms: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('rooms.html', rooms=rooms_list)


@app.route('/rooms/<int:id>/delete', methods=['GET', 'POST'])
def delete_room(id):
    """Delete an examination venue room by ID."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM rooms WHERE room_id = %s", (id,))
        conn.commit()
        flash("Room deleted successfully!", "success")
    except mysql.connector.IntegrityError:
        flash("Cannot delete room: it is scheduled for upcoming examinations.", "error")
    except Exception as e:
        flash(f"Error deleting room: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('rooms'))


# ==============================================================================
# 6. INVIGILATORS (CRUD)
# ==============================================================================
@app.route('/invigilators', methods=['GET', 'POST'])
def invigilators():
    """List invigilators or register a new invigilator."""
    conn = None
    cursor = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        department = request.form.get('department', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip() or None

        if not name or not department or not email:
            flash("Name, department, and email are required.", "error")
            return redirect(url_for('invigilators'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "INSERT INTO invigilators (name, department, email, phone) VALUES (%s, %s, %s, %s)",
                (name, department, email, phone)
            )
            conn.commit()
            flash("Invigilator added successfully!", "success")
        except mysql.connector.IntegrityError as err:
            if err.errno == 1062:
                flash("An invigilator with this email already exists.", "error")
            else:
                flash(f"Database error: {err.msg}", "error")
        except Exception as e:
            flash(f"Error adding invigilator: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('invigilators'))

    # GET request
    invigilators_list = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM invigilators ORDER BY name")
        invigilators_list = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading invigilators: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('invigilators.html', invigilators=invigilators_list)


@app.route('/invigilators/<int:id>/delete', methods=['GET', 'POST'])
def delete_invigilator(id):
    """Delete an invigilator record by ID."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM invigilators WHERE invigilator_id = %s", (id,))
        conn.commit()
        flash("Invigilator deleted successfully!", "success")
    except mysql.connector.IntegrityError:
        flash("Cannot delete invigilator: assigned to active examination schedules.", "error")
    except Exception as e:
        flash(f"Error deleting invigilator: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('invigilators'))


# ==============================================================================
# 7. EXAM SESSIONS (CRUD)
# ==============================================================================
@app.route('/exam-sessions', methods=['GET', 'POST'])
def exam_sessions():
    """List exam sessions or create a new session cycle."""
    conn = None
    cursor = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        session_type = request.form.get('session_type', 'END_SEM')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        is_active = 1 if 'is_active' in request.form else 0

        if not name or not session_type or not start_date or not end_date:
            flash("Name, session type, start date, and end date are required.", "error")
            return redirect(url_for('exam_sessions'))

        if start_date > end_date:
            flash("End date cannot be earlier than start date.", "error")
            return redirect(url_for('exam_sessions'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "INSERT INTO exam_sessions (name, session_type, start_date, end_date, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                (name, session_type, start_date, end_date, is_active)
            )
            conn.commit()
            flash("Exam session created successfully!", "success")
        except mysql.connector.IntegrityError as err:
            flash(f"Database error: {err.msg}", "error")
        except Exception as e:
            flash(f"Error creating exam session: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('exam_sessions'))

    # GET request
    sessions_list = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM exam_sessions ORDER BY start_date DESC")
        sessions_list = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading exam sessions: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('exam_sessions.html', sessions=sessions_list)


@app.route('/exam-sessions/<int:id>/delete', methods=['GET', 'POST'])
def delete_exam_session(id):
    """Delete an exam session cycle by ID."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM exam_sessions WHERE session_id = %s", (id,))
        conn.commit()
        flash("Exam session deleted successfully!", "success")
    except mysql.connector.IntegrityError:
        flash("Cannot delete exam session: schedules, registrations, or grade rules reference it.", "error")
    except Exception as e:
        flash(f"Error deleting exam session: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('exam_sessions'))


# ==============================================================================
# 8. SCHEDULES (Conflict Detection & Scheduling)
# ==============================================================================
@app.route('/schedules', methods=['GET', 'POST'])
def schedules():
    """List exam schedules with assigned invigilators or create a new slot with conflict detection."""
    conn = None
    cursor = None
    if request.method == 'POST':
        session_id = request.form.get('session_id')
        course_id = request.form.get('course_id')
        room_id = request.form.get('room_id')
        exam_date = request.form.get('exam_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        invigilator_ids = request.form.getlist('invigilator_ids')

        if not session_id or not course_id or not room_id or not exam_date or not start_time or not end_time:
            flash("All schedule parameters are required.", "error")
            return redirect(url_for('schedules'))

        if start_time >= end_time:
            flash("End time must be after start time.", "error")
            return redirect(url_for('schedules'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)

            # 1. Room Conflict Check
            # Overlap occurs when: sch.start_time < end_time_new AND sch.end_time > start_time_new
            cursor.execute("""
                SELECT sch.*, r.room_number, r.building 
                FROM schedules sch 
                JOIN rooms r ON sch.room_id = r.room_id 
                WHERE sch.room_id = %s 
                  AND sch.exam_date = %s 
                  AND (sch.start_time < %s AND sch.end_time > %s)
            """, (int(room_id), exam_date, end_time, start_time))
            room_conflict = cursor.fetchone()

            if room_conflict:
                flash(
                    f"Room Conflict: Room {room_conflict['room_number']} ({room_conflict['building']}) "
                    f"is already booked on {exam_date} during {room_conflict['start_time']} - {room_conflict['end_time']}.",
                    "error"
                )
                return redirect(url_for('schedules'))

            # 2. Invigilator Conflict Check
            clean_inv_ids = [int(i) for i in invigilator_ids if i]
            for inv_id in clean_inv_ids:
                cursor.execute("""
                    SELECT i.name, sch.exam_date, sch.start_time, sch.end_time 
                    FROM schedule_invigilators si 
                    JOIN schedules sch ON si.schedule_id = sch.schedule_id 
                    JOIN invigilators i ON si.invigilator_id = i.invigilator_id 
                    WHERE si.invigilator_id = %s 
                      AND sch.exam_date = %s 
                      AND (sch.start_time < %s AND sch.end_time > %s)
                """, (inv_id, exam_date, end_time, start_time))
                inv_conflict = cursor.fetchone()

                if inv_conflict:
                    flash(
                        f"Invigilator Conflict: {inv_conflict['name']} is already assigned on {exam_date} "
                        f"during {inv_conflict['start_time']} - {inv_conflict['end_time']}.",
                        "error"
                    )
                    return redirect(url_for('schedules'))

            # 3. Insert Schedule
            cursor.execute("""
                INSERT INTO schedules (session_id, course_id, room_id, exam_date, start_time, end_time) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (int(session_id), int(course_id), int(room_id), exam_date, start_time, end_time))
            schedule_id = cursor.lastrowid

            # 4. Insert Schedule Invigilators
            for inv_id in clean_inv_ids:
                cursor.execute("""
                    INSERT INTO schedule_invigilators (schedule_id, invigilator_id) 
                    VALUES (%s, %s)
                """, (schedule_id, inv_id))

            conn.commit()
            flash("Exam timetable slot scheduled successfully!", "success")

        except mysql.connector.IntegrityError as err:
            flash(f"Scheduling integrity error: {err.msg}", "error")
        except Exception as e:
            flash(f"Error creating schedule: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('schedules'))

    # GET request
    schedules_list = []
    sessions_list = []
    courses_list = []
    rooms_list = []
    invigilators_list = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                sch.*, 
                c.course_code, 
                c.name AS course_name, 
                r.room_number, 
                r.building, 
                es.name AS session_name, 
                GROUP_CONCAT(i.name SEPARATOR ', ') AS invigilator_names 
            FROM schedules sch 
            JOIN courses c ON sch.course_id = c.course_id 
            JOIN rooms r ON sch.room_id = r.room_id 
            JOIN exam_sessions es ON sch.session_id = es.session_id 
            LEFT JOIN schedule_invigilators si ON sch.schedule_id = si.schedule_id 
            LEFT JOIN invigilators i ON si.invigilator_id = i.invigilator_id 
            GROUP BY sch.schedule_id 
            ORDER BY sch.exam_date, sch.start_time
        """)
        schedules_list = cursor.fetchall()

        # Handle NULL invigilators and format time strings safely
        for s in schedules_list:
            if not s.get('invigilator_names'):
                s['invigilator_names'] = 'None assigned'

        cursor.execute("SELECT * FROM exam_sessions ORDER BY start_date DESC")
        sessions_list = cursor.fetchall()

        cursor.execute("SELECT * FROM courses ORDER BY course_code")
        courses_list = cursor.fetchall()

        cursor.execute("SELECT * FROM rooms ORDER BY room_number")
        rooms_list = cursor.fetchall()

        cursor.execute("SELECT * FROM invigilators ORDER BY name")
        invigilators_list = cursor.fetchall()

    except Exception as e:
        flash(f"Error loading schedules: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'schedules.html',
        schedules=schedules_list,
        sessions=sessions_list,
        courses=courses_list,
        rooms=rooms_list,
        invigilators=invigilators_list
    )


@app.route('/schedules/<int:id>/delete', methods=['GET', 'POST'])
def delete_schedule(id):
    """Delete an exam timetable schedule slot."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        # Explicitly remove linked invigilator assignments if not cascaded
        cursor.execute("DELETE FROM schedule_invigilators WHERE schedule_id = %s", (id,))
        cursor.execute("DELETE FROM schedules WHERE schedule_id = %s", (id,))
        conn.commit()
        flash("Exam schedule deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting schedule: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('schedules'))


# ==============================================================================
# 9. REGISTRATIONS (Course Enrollments for Exam Sessions)
# ==============================================================================
@app.route('/registrations', methods=['GET', 'POST'])
def registrations():
    """List student exam registrations or register a student for a course."""
    conn = None
    cursor = None
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        session_id = request.form.get('session_id')

        if not student_id or not course_id or not session_id:
            flash("Student, course, and session are all required.", "error")
            return redirect(url_for('registrations'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO registrations (student_id, course_id, session_id, registered_date) 
                VALUES (%s, %s, %s, CURDATE())
            """, (int(student_id), int(course_id), int(session_id)))
            conn.commit()
            flash("Student registered for course exam successfully!", "success")
        except mysql.connector.IntegrityError as err:
            if err.errno == 1062:
                flash("Duplicate: Student is already registered for this course in the selected session.", "error")
            else:
                flash(f"Database error: {err.msg}", "error")
        except Exception as e:
            flash(f"Error registering student: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('registrations'))

    # GET request
    registrations_list = []
    students_list = []
    courses_list = []
    sessions_list = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                r.*, 
                s.roll_number, 
                s.name AS student_name, 
                c.course_code, 
                c.name AS course_name, 
                es.name AS session_name 
            FROM registrations r 
            JOIN students s ON r.student_id = s.student_id 
            JOIN courses c ON r.course_id = c.course_id 
            JOIN exam_sessions es ON r.session_id = es.session_id 
            ORDER BY r.registered_date DESC, r.registration_id DESC
        """)
        registrations_list = cursor.fetchall()

        cursor.execute("SELECT * FROM students ORDER BY roll_number")
        students_list = cursor.fetchall()

        cursor.execute("SELECT * FROM courses ORDER BY course_code")
        courses_list = cursor.fetchall()

        # Fetch active exam sessions (or all if none are active)
        cursor.execute("SELECT * FROM exam_sessions WHERE is_active = 1 ORDER BY start_date DESC")
        sessions_list = cursor.fetchall()
        if not sessions_list:
            cursor.execute("SELECT * FROM exam_sessions ORDER BY start_date DESC")
            sessions_list = cursor.fetchall()

    except Exception as e:
        flash(f"Error loading registrations: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'registrations.html',
        registrations=registrations_list,
        students=students_list,
        courses=courses_list,
        sessions=sessions_list
    )


@app.route('/registrations/<int:id>/delete', methods=['GET', 'POST'])
def delete_registration(id):
    """Delete an exam registration."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM registrations WHERE registration_id = %s", (id,))
        conn.commit()
        flash("Registration deleted successfully!", "success")
    except mysql.connector.IntegrityError:
        flash("Cannot delete registration: marks or evaluation records depend on it.", "error")
    except Exception as e:
        flash(f"Error deleting registration: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('registrations'))


# ==============================================================================
# 10. MARKS ENTRY (with Validation)
# ==============================================================================
@app.route('/marks', methods=['GET', 'POST'])
def marks():
    """List entered marks or record evaluation marks for a registration."""
    conn = None
    cursor = None
    if request.method == 'POST':
        registration_id = request.form.get('registration_id')
        marks_obtained_str = request.form.get('marks_obtained', '').strip()
        max_marks = request.form.get('max_marks', 100)

        if not registration_id or not marks_obtained_str:
            flash("Registration and marks obtained are required.", "error")
            return redirect(url_for('marks'))

        try:
            marks_obtained = float(marks_obtained_str)
            max_marks_int = int(max_marks) if max_marks else 100
        except ValueError:
            flash("Please enter valid numeric values for marks.", "error")
            return redirect(url_for('marks'))

        if marks_obtained < 0 or marks_obtained > 100:
            flash("Marks obtained must be between 0 and 100.", "error")
            return redirect(url_for('marks'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO marks (registration_id, marks_obtained, max_marks) 
                VALUES (%s, %s, %s)
            """, (int(registration_id), marks_obtained, max_marks_int))
            conn.commit()
            flash("Marks recorded successfully!", "success")
        except mysql.connector.IntegrityError as err:
            if err.errno == 1062:
                flash("Marks for this registration have already been recorded.", "error")
            else:
                flash(f"Database error: {err.msg}", "error")
        except Exception as e:
            flash(f"Error saving marks: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('marks'))

    # GET request
    marks_list = []
    unmarked_registrations = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                m.*, 
                r.registration_id, 
                s.roll_number, 
                s.name AS student_name, 
                c.course_code, 
                c.name AS course_name, 
                es.name AS session_name 
            FROM marks m 
            JOIN registrations r ON m.registration_id = r.registration_id 
            JOIN students s ON r.student_id = s.student_id 
            JOIN courses c ON r.course_id = c.course_id 
            JOIN exam_sessions es ON r.session_id = es.session_id 
            ORDER BY s.roll_number
        """)
        marks_list = cursor.fetchall()
        for m in marks_list:
            if m.get('marks_obtained') is not None:
                m['marks_obtained'] = float(m['marks_obtained'])

        cursor.execute("""
            SELECT 
                r.registration_id, 
                s.roll_number, 
                s.name AS student_name, 
                c.course_code, 
                c.name AS course_name, 
                es.name AS session_name 
            FROM registrations r 
            JOIN students s ON r.student_id = s.student_id 
            JOIN courses c ON r.course_id = c.course_id 
            JOIN exam_sessions es ON r.session_id = es.session_id 
            WHERE r.registration_id NOT IN (SELECT registration_id FROM marks) 
            ORDER BY s.roll_number
        """)
        unmarked_registrations = cursor.fetchall()

    except Exception as e:
        flash(f"Error loading marks: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('marks.html', marks=marks_list, unmarked_registrations=unmarked_registrations)


@app.route('/marks/<int:id>/delete', methods=['GET', 'POST'])
def delete_mark(id):
    """Delete a marks entry by mark_id."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM marks WHERE mark_id = %s", (id,))
        conn.commit()
        flash("Marks record deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting marks: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('marks'))


# ==============================================================================
# 11. GRADE RULES
# ==============================================================================
@app.route('/grade-rules', methods=['GET', 'POST'])
def grade_rules():
    """List or create session grading policies and cutoffs."""
    conn = None
    cursor = None
    if request.method == 'POST':
        session_id = request.form.get('session_id')
        min_marks = request.form.get('min_marks')
        max_marks = request.form.get('max_marks')
        grade = request.form.get('grade', '').strip().upper()
        grade_point = request.form.get('grade_point')

        if not session_id or min_marks is None or max_marks is None or not grade or grade_point is None:
            flash("All grading rule fields are required.", "error")
            return redirect(url_for('grade_rules'))

        try:
            min_val = float(min_marks)
            max_val = float(max_marks)
            gp_val = float(grade_point)
        except ValueError:
            flash("Min marks, max marks, and grade point must be valid numbers.", "error")
            return redirect(url_for('grade_rules'))

        if min_val > max_val:
            flash("Maximum marks cannot be less than minimum marks.", "error")
            return redirect(url_for('grade_rules'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO grade_rules (session_id, min_marks, max_marks, grade, grade_point) 
                VALUES (%s, %s, %s, %s, %s)
            """, (int(session_id), min_val, max_val, grade, gp_val))
            conn.commit()
            flash("Grade rule added successfully!", "success")
        except mysql.connector.IntegrityError as err:
            if err.errno == 1062:
                flash(f"Grade rule for grade '{grade}' already exists in this exam session.", "error")
            else:
                flash(f"Database error: {err.msg}", "error")
        except Exception as e:
            flash(f"Error adding grade rule: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('grade_rules'))

    # GET request
    rules_list = []
    sessions_list = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT gr.*, es.name AS session_name 
            FROM grade_rules gr 
            JOIN exam_sessions es ON gr.session_id = es.session_id 
            ORDER BY es.name, gr.min_marks DESC
        """)
        rules_list = cursor.fetchall()
        for r in rules_list:
            if r.get('min_marks') is not None:
                r['min_marks'] = float(r['min_marks'])
            if r.get('max_marks') is not None:
                r['max_marks'] = float(r['max_marks'])
            if r.get('grade_point') is not None:
                r['grade_point'] = float(r['grade_point'])

        cursor.execute("SELECT * FROM exam_sessions ORDER BY start_date DESC")
        sessions_list = cursor.fetchall()

    except Exception as e:
        flash(f"Error loading grade rules: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('grade_rules.html', rules=rules_list, sessions=sessions_list)


@app.route('/grade-rules/<int:id>/delete', methods=['GET', 'POST'])
def delete_grade_rule(id):
    """Delete a grade rule by rule_id."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM grade_rules WHERE rule_id = %s", (id,))
        conn.commit()
        flash("Grade rule deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting grade rule: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('grade_rules'))


# ==============================================================================
# 12. RESULTS (Computation & Publishing)
# ==============================================================================
@app.route('/results', methods=['GET'])
def results():
    """List evaluated student results, optionally filtered by session."""
    session_id = request.args.get('session_id')
    results_list = []
    sessions_list = []
    conn = None
    cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                res.*, 
                r.registration_id, 
                s.roll_number, 
                s.name AS student_name, 
                c.course_code, 
                c.name AS course_name, 
                es.session_id, 
                es.name AS session_name, 
                m.marks_obtained 
            FROM results res 
            JOIN registrations r ON res.registration_id = r.registration_id 
            JOIN students s ON r.student_id = s.student_id 
            JOIN courses c ON r.course_id = c.course_id 
            JOIN exam_sessions es ON r.session_id = es.session_id 
            LEFT JOIN marks m ON r.registration_id = m.registration_id
        """
        params = []
        if session_id and session_id.strip():
            query += " WHERE es.session_id = %s"
            params.append(int(session_id))
        query += " ORDER BY s.roll_number, c.course_code"

        cursor.execute(query, params)
        results_list = cursor.fetchall()

        for res in results_list:
            if res.get('grade_point') is not None:
                res['grade_point'] = float(res['grade_point'])
            if res.get('marks_obtained') is not None:
                res['marks_obtained'] = float(res['marks_obtained'])

        cursor.execute("SELECT * FROM exam_sessions ORDER BY start_date DESC")
        sessions_list = cursor.fetchall()

    except Exception as e:
        flash(f"Error loading results: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'results.html',
        results=results_list,
        sessions=sessions_list,
        selected_session=int(session_id) if session_id and session_id.isdigit() else None
    )


@app.route('/results/compute', methods=['POST'])
def compute_results():
    """Compute grades and grade points for all marked registrations in a session."""
    session_id = request.form.get('session_id')
    if not session_id:
        flash("Please select an exam session to compute results.", "error")
        return redirect(url_for('results'))

    conn = None
    cursor = None
    computed_count = 0

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # 1. Fetch registrations with marks for the selected session
        cursor.execute("""
            SELECT r.registration_id, m.marks_obtained 
            FROM registrations r 
            JOIN marks m ON r.registration_id = m.registration_id 
            WHERE r.session_id = %s
        """, (int(session_id),))
        marked_regs = cursor.fetchall()

        if not marked_regs:
            flash("No evaluated registrations found with marks for this session.", "error")
            return redirect(url_for('results', session_id=session_id))

        # 2. Fetch grade rules for this session
        cursor.execute("""
            SELECT min_marks, max_marks, grade, grade_point 
            FROM grade_rules 
            WHERE session_id = %s 
            ORDER BY min_marks DESC
        """, (int(session_id),))
        rules = cursor.fetchall()

        if not rules:
            flash("No grading rules defined for this exam session. Define grade rules first.", "error")
            return redirect(url_for('grade_rules'))

        # 3. Compute and upsert results
        for item in marked_regs:
            score = float(item['marks_obtained'])
            matched_grade = None
            matched_gp = 0.0

            for rule in rules:
                if float(rule['min_marks']) <= score <= float(rule['max_marks']):
                    matched_grade = rule['grade']
                    matched_gp = float(rule['grade_point'])
                    break

            # Fallback if score didn't fall into explicit range
            if not matched_grade:
                matched_grade = 'F'
                matched_gp = 0.0

            cursor.execute("""
                INSERT INTO results (registration_id, grade, grade_point, is_published) 
                VALUES (%s, %s, %s, 0) 
                ON DUPLICATE KEY UPDATE 
                    grade = VALUES(grade), 
                    grade_point = VALUES(grade_point)
            """, (item['registration_id'], matched_grade, matched_gp))
            computed_count += 1

        conn.commit()
        flash(f"Successfully computed {computed_count} results for the session.", "success")

    except Exception as e:
        flash(f"Error computing results: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('results', session_id=session_id))


@app.route('/results/publish', methods=['POST'])
def publish_results():
    """Publish results for an exam session making them publicly visible."""
    session_id = request.form.get('session_id')
    if not session_id:
        flash("Exam session is required to publish results.", "error")
        return redirect(url_for('results'))

    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            UPDATE results 
            SET is_published = 1 
            WHERE registration_id IN (
                SELECT registration_id FROM registrations WHERE session_id = %s
            )
        """, (int(session_id),))
        conn.commit()
        flash("Results published successfully!", "success")
    except Exception as e:
        flash(f"Error publishing results: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('results', session_id=session_id))


# ==============================================================================
# 13. HALL TICKETS
# ==============================================================================
@app.route('/hall-tickets', methods=['GET'])
def hall_tickets():
    """Generate and display student examination hall tickets / admit cards."""
    session_id = request.args.get('session_id')
    student_id = request.args.get('student_id')
    tickets = []
    sessions_list = []
    students_list = []
    conn = None
    cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM exam_sessions ORDER BY start_date DESC")
        sessions_list = cursor.fetchall()

        cursor.execute("SELECT * FROM students ORDER BY roll_number")
        students_list = cursor.fetchall()

        if session_id and session_id.strip():
            query = """
                SELECT 
                    s.student_id, 
                    s.roll_number, 
                    s.name AS student_name, 
                    s.email, 
                    p.name AS programme_name, 
                    c.course_code, 
                    c.name AS course_name, 
                    sch.exam_date, 
                    sch.start_time, 
                    sch.end_time, 
                    r.room_number, 
                    r.building, 
                    es.name AS session_name 
                FROM registrations reg 
                JOIN students s ON reg.student_id = s.student_id 
                JOIN programmes p ON s.programme_id = p.programme_id 
                JOIN courses c ON reg.course_id = c.course_id 
                JOIN exam_sessions es ON reg.session_id = es.session_id 
                LEFT JOIN schedules sch ON (sch.course_id = c.course_id AND sch.session_id = es.session_id) 
                LEFT JOIN rooms r ON sch.room_id = r.room_id 
                WHERE reg.session_id = %s
            """
            params = [int(session_id)]

            if student_id and student_id.strip():
                query += " AND reg.student_id = %s"
                params.append(int(student_id))

            query += " ORDER BY sch.exam_date, sch.start_time, s.roll_number"

            cursor.execute(query, params)
            tickets = cursor.fetchall()

    except Exception as e:
        flash(f"Error loading hall tickets: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'hall_tickets.html',
        tickets=tickets,
        sessions=sessions_list,
        students=students_list,
        selected_session=int(session_id) if session_id and session_id.isdigit() else None,
        selected_student=int(student_id) if student_id and student_id.isdigit() else None
    )


# ==============================================================================
# 14. REPORTS (Analytics & Conflicts)
# ==============================================================================
@app.route('/reports', methods=['GET'])
def reports():
    """Analytical reporting suite for pass percentages, grade distribution, room usage, and conflicts."""
    conn = None
    cursor = None
    pass_percentage = []
    grade_distribution = []
    room_utilization = []
    room_conflicts = []
    invigilator_conflicts = []
    all_conflicts = []

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # a) Pass Percentage per course in published results
        cursor.execute("""
            SELECT 
                es.name AS session_name, 
                c.course_code, 
                c.name AS course_name, 
                COUNT(*) AS total, 
                SUM(CASE WHEN res.grade != 'F' THEN 1 ELSE 0 END) AS passed, 
                ROUND((SUM(CASE WHEN res.grade != 'F' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS pass_percentage 
            FROM results res 
            JOIN registrations r ON res.registration_id = r.registration_id 
            JOIN courses c ON r.course_id = c.course_id 
            JOIN exam_sessions es ON r.session_id = es.session_id 
            WHERE res.is_published = 1 
            GROUP BY es.session_id, es.name, c.course_id, c.course_code, c.name 
            ORDER BY es.name, c.course_code
        """)
        pass_percentage = cursor.fetchall()
        for p in pass_percentage:
            p['total'] = int(p['total'])
            p['passed'] = int(p['passed'])
            p['pass_percentage'] = float(p['pass_percentage']) if p.get('pass_percentage') is not None else 0.0

        # b) Grade Distribution across sessions
        cursor.execute("""
            SELECT 
                es.name AS session_name, 
                res.grade, 
                COUNT(*) AS count 
            FROM results res 
            JOIN registrations r ON res.registration_id = r.registration_id 
            JOIN exam_sessions es ON r.session_id = es.session_id 
            WHERE res.is_published = 1 
            GROUP BY es.session_id, es.name, res.grade 
            ORDER BY es.name, res.grade
        """)
        grade_distribution = cursor.fetchall()

        # c) Room Utilization
        cursor.execute("""
            SELECT 
                r.room_number, 
                r.building, 
                r.capacity, 
                COUNT(sch.schedule_id) AS total_exams 
            FROM rooms r 
            LEFT JOIN schedules sch ON r.room_id = sch.room_id 
            GROUP BY r.room_id, r.room_number, r.building, r.capacity 
            ORDER BY total_exams DESC, r.room_number
        """)
        room_utilization = cursor.fetchall()

        # d) Double-booking Conflicts
        cursor.execute("""
            SELECT 
                r.room_number, 
                r.building, 
                s1.exam_date, 
                s1.start_time AS start_time_1, 
                s1.end_time AS end_time_1, 
                c1.course_code AS course_code_1, 
                s2.start_time AS start_time_2, 
                s2.end_time AS end_time_2, 
                c2.course_code AS course_code_2 
            FROM schedules s1 
            JOIN schedules s2 ON s1.room_id = s2.room_id 
                AND s1.exam_date = s2.exam_date 
                AND s1.schedule_id < s2.schedule_id 
                AND s1.start_time < s2.end_time 
                AND s1.end_time > s2.start_time 
            JOIN rooms r ON s1.room_id = r.room_id 
            JOIN courses c1 ON s1.course_id = c1.course_id 
            JOIN courses c2 ON s2.course_id = c2.course_id
        """)
        room_conflicts = cursor.fetchall()

        cursor.execute("""
            SELECT 
                i.name AS invigilator_name, 
                s1.exam_date, 
                s1.start_time AS start_time_1, 
                s1.end_time AS end_time_1, 
                c1.course_code AS course_code_1, 
                s2.start_time AS start_time_2, 
                s2.end_time AS end_time_2, 
                c2.course_code AS course_code_2 
            FROM schedule_invigilators si1 
            JOIN schedule_invigilators si2 ON si1.invigilator_id = si2.invigilator_id 
                AND si1.schedule_id < si2.schedule_id 
            JOIN schedules s1 ON si1.schedule_id = s1.schedule_id 
            JOIN schedules s2 ON si2.schedule_id = s2.schedule_id 
                AND s1.exam_date = s2.exam_date 
                AND s1.start_time < s2.end_time 
                AND s1.end_time > s2.start_time 
            JOIN invigilators i ON si1.invigilator_id = i.invigilator_id 
            JOIN courses c1 ON s1.course_id = c1.course_id 
            JOIN courses c2 ON s2.course_id = c2.course_id
        """)
        invigilator_conflicts = cursor.fetchall()

        for rc in room_conflicts:
            all_conflicts.append({
                'type': 'Room Conflict',
                'resource': f"Room {rc['room_number']} ({rc['building']})",
                'date': rc['exam_date'],
                'detail': f"{rc['course_code_1']} ({rc['start_time_1']}-{rc['end_time_1']}) vs {rc['course_code_2']} ({rc['start_time_2']}-{rc['end_time_2']})"
            })

        for ic in invigilator_conflicts:
            all_conflicts.append({
                'type': 'Invigilator Conflict',
                'resource': f"Invigilator {ic['invigilator_name']}",
                'date': ic['exam_date'],
                'detail': f"{ic['course_code_1']} ({ic['start_time_1']}-{ic['end_time_1']}) vs {ic['course_code_2']} ({ic['start_time_2']}-{ic['end_time_2']})"
            })

    except Exception as e:
        flash(f"Error calculating reports: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'reports.html',
        pass_percentage=pass_percentage,
        grade_distribution=grade_distribution,
        room_utilization=room_utilization,
        conflicts=all_conflicts,
        room_conflicts=room_conflicts,
        invigilator_conflicts=invigilator_conflicts
    )


# ==============================================================================
# 15. REVALUATIONS (Requests, Approvals, Rejections)
# ==============================================================================
@app.route('/revaluations', methods=['GET', 'POST'])
def revaluations():
    """List student revaluation requests or submit a new review request."""
    conn = None
    cursor = None
    if request.method == 'POST':
        registration_id = request.form.get('registration_id')
        reason = request.form.get('reason', '').strip()

        if not registration_id or not reason:
            flash("Registration ID and reason for revaluation are required.", "error")
            return redirect(url_for('revaluations'))

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO revaluation_requests (registration_id, reason, status, requested_date) 
                VALUES (%s, %s, 'PENDING', CURDATE())
            """, (int(registration_id), reason))
            conn.commit()
            flash("Revaluation request submitted successfully!", "success")
        except Exception as e:
            flash(f"Error submitting revaluation request: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('revaluations'))

    # GET request
    requests_list = []
    registrations_with_marks = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                rv.*, 
                s.roll_number, 
                s.name AS student_name, 
                c.course_code, 
                c.name AS course_name, 
                es.name AS session_name, 
                m.marks_obtained AS original_marks 
            FROM revaluation_requests rv 
            JOIN registrations r ON rv.registration_id = r.registration_id 
            JOIN students s ON r.student_id = s.student_id 
            JOIN courses c ON r.course_id = c.course_id 
            JOIN exam_sessions es ON r.session_id = es.session_id 
            LEFT JOIN marks m ON r.registration_id = m.registration_id 
            ORDER BY rv.requested_date DESC, rv.request_id DESC
        """)
        requests_list = cursor.fetchall()
        for req in requests_list:
            if req.get('original_marks') is not None:
                req['original_marks'] = float(req['original_marks'])
            if req.get('new_marks') is not None:
                req['new_marks'] = float(req['new_marks'])

        cursor.execute("""
            SELECT 
                r.registration_id, 
                s.roll_number, 
                s.name AS student_name, 
                c.course_code, 
                m.marks_obtained 
            FROM registrations r 
            JOIN students s ON r.student_id = s.student_id 
            JOIN courses c ON r.course_id = c.course_id 
            JOIN marks m ON r.registration_id = m.registration_id 
            ORDER BY s.roll_number
        """)
        registrations_with_marks = cursor.fetchall()
        for rm in registrations_with_marks:
            if rm.get('marks_obtained') is not None:
                rm['marks_obtained'] = float(rm['marks_obtained'])

    except Exception as e:
        flash(f"Error loading revaluations: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'revaluations.html',
        requests=requests_list,
        registrations_with_marks=registrations_with_marks
    )


@app.route('/revaluations/<int:id>/approve', methods=['GET', 'POST'])
def approve_revaluation(id):
    """Approve a revaluation request, record new marks, and update marks table."""
    new_marks_val = request.form.get('new_marks') or request.args.get('new_marks')
    if new_marks_val is None or str(new_marks_val).strip() == '':
        flash("New evaluated marks are required to approve revaluation.", "error")
        return redirect(url_for('revaluations'))

    try:
        new_marks = float(new_marks_val)
    except ValueError:
        flash("Invalid marks format.", "error")
        return redirect(url_for('revaluations'))

    if new_marks < 0 or new_marks > 100:
        flash("Marks must be between 0 and 100.", "error")
        return redirect(url_for('revaluations'))

    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            UPDATE revaluation_requests 
            SET status = 'APPROVED', resolved_date = CURDATE(), new_marks = %s 
            WHERE request_id = %s
        """, (new_marks, id))

        cursor.execute("""
            UPDATE marks 
            SET marks_obtained = %s 
            WHERE registration_id = (
                SELECT registration_id FROM revaluation_requests WHERE request_id = %s
            )
        """, (new_marks, id))

        conn.commit()
        flash("Revaluation approved and student marks updated successfully!", "success")
    except Exception as e:
        flash(f"Error approving revaluation: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('revaluations'))


@app.route('/revaluations/<int:id>/reject', methods=['GET', 'POST'])
def reject_revaluation(id):
    """Reject a revaluation request."""
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            UPDATE revaluation_requests 
            SET status = 'REJECTED', resolved_date = CURDATE() 
            WHERE request_id = %s
        """, (id,))
        conn.commit()
        flash("Revaluation request rejected.", "success")
    except Exception as e:
        flash(f"Error rejecting revaluation: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('revaluations'))


# ==============================================================================
# 16. SQL TABLE VIEWER (Secure Schema & Data Inspector)
# ==============================================================================
@app.route('/sql-tables', methods=['GET'])
@app.route('/sql-tables/<table_name>', methods=['GET'])
def sql_tables(table_name=None):
    """Inspect database tables, column structures, and browse live rows."""
    conn = None
    cursor = None
    all_tables = []
    columns = []
    rows = []

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SHOW TABLES")
        table_rows = cursor.fetchall()
        for tr in table_rows:
            all_tables.append(list(tr.values())[0])

        if table_name:
            if table_name not in all_tables:
                flash(f"Security Alert: Table '{table_name}' does not exist or is unauthorized.", "error")
                return redirect(url_for('sql_tables'))

            # Safe parameterized schema inspection
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()

            cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
            rows = cursor.fetchall()

    except Exception as e:
        flash(f"Error querying table viewer: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'sql_tables.html',
        tables=all_tables,
        selected_table=table_name,
        columns=columns,
        rows=rows
    )


# ------------------------------------------------------------------------------
# URL Endpoint Aliases for Compatibility with Templates
# ------------------------------------------------------------------------------
app.add_url_rule('/programmes/<int:id>/delete', endpoint='delete_programmes', view_func=delete_programme, methods=['GET', 'POST'])
app.add_url_rule('/courses/<int:id>/delete', endpoint='delete_courses', view_func=delete_course, methods=['GET', 'POST'])
app.add_url_rule('/students/<int:id>/delete', endpoint='delete_students', view_func=delete_student, methods=['GET', 'POST'])
app.add_url_rule('/rooms/<int:id>/delete', endpoint='delete_rooms', view_func=delete_room, methods=['GET', 'POST'])
app.add_url_rule('/invigilators/<int:id>/delete', endpoint='delete_invigilators', view_func=delete_invigilator, methods=['GET', 'POST'])
app.add_url_rule('/exam-sessions/<int:id>/delete', endpoint='delete_exam_sessions', view_func=delete_exam_session, methods=['GET', 'POST'])
app.add_url_rule('/schedules/<int:id>/delete', endpoint='delete_schedules', view_func=delete_schedule, methods=['GET', 'POST'])
app.add_url_rule('/registrations/<int:id>/delete', endpoint='delete_registrations', view_func=delete_registration, methods=['GET', 'POST'])
app.add_url_rule('/marks/<int:id>/delete', endpoint='delete_marks', view_func=delete_mark, methods=['GET', 'POST'])
app.add_url_rule('/grade-rules/<int:id>/delete', endpoint='delete_grade_rules', view_func=delete_grade_rule, methods=['GET', 'POST'])
app.add_url_rule('/results/compute', endpoint='results_compute', view_func=compute_results, methods=['POST'])
app.add_url_rule('/results/publish', endpoint='results_publish', view_func=publish_results, methods=['POST'])
app.add_url_rule('/revaluations/<int:id>/approve', endpoint='revaluation_approve', view_func=approve_revaluation, methods=['GET', 'POST'])
app.add_url_rule('/revaluations/<int:id>/reject', endpoint='revaluation_reject', view_func=reject_revaluation, methods=['GET', 'POST'])
app.add_url_rule('/sql-tables/<table_name>', endpoint='sql_table_detail', view_func=sql_tables, methods=['GET'])


# ==============================================================================
# Application Entry Point
# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
