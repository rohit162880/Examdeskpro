-- =============================================================================
-- Examination Scheduling and Result Processing System
-- Database Definition Script
-- Database: exam_scheduling_db
-- =============================================================================

CREATE DATABASE IF NOT EXISTS exam_scheduling_db;
USE exam_scheduling_db;

-- -----------------------------------------------------------------------------
-- Drop Views (in reverse dependency order)
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS v_pass_percentage;
DROP VIEW IF EXISTS v_grade_distribution;
DROP VIEW IF EXISTS v_hall_tickets;
DROP VIEW IF EXISTS v_student_results;
DROP VIEW IF EXISTS v_exam_schedule;

-- -----------------------------------------------------------------------------
-- Drop Tables (in reverse foreign key dependency order)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS revaluation_requests;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS grade_rules;
DROP TABLE IF EXISTS marks;
DROP TABLE IF EXISTS registrations;
DROP TABLE IF EXISTS schedule_invigilators;
DROP TABLE IF EXISTS schedules;
DROP TABLE IF EXISTS exam_sessions;
DROP TABLE IF EXISTS invigilators;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS programmes;

-- =============================================================================
-- Table 1: programmes
-- Academic programmes offered by the institution
-- =============================================================================
CREATE TABLE programmes (
    programme_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    duration_years INT NOT NULL DEFAULT 4,
    degree_type VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- =============================================================================
-- Table 2: courses
-- Courses/subjects under each academic programme
-- =============================================================================
CREATE TABLE courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    credits INT NOT NULL CHECK(credits BETWEEN 1 AND 6),
    programme_id INT NOT NULL,
    semester INT NOT NULL CHECK(semester BETWEEN 1 AND 8),
    FOREIGN KEY (programme_id) REFERENCES programmes(programme_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- Table 3: students
-- Enrolled students in various programmes
-- =============================================================================
CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    roll_number VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    programme_id INT NOT NULL,
    admission_year INT NOT NULL,
    FOREIGN KEY (programme_id) REFERENCES programmes(programme_id)
) ENGINE=InnoDB;

-- =============================================================================
-- Table 4: rooms
-- Examination venues and lecture halls
-- =============================================================================
CREATE TABLE rooms (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(20) NOT NULL UNIQUE,
    building VARCHAR(50) NOT NULL,
    capacity INT NOT NULL CHECK(capacity > 0),
    has_projector BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB;

-- =============================================================================
-- Table 5: invigilators
-- Faculty members and staff assigned for invigilation duties
-- =============================================================================
CREATE TABLE invigilators (
    invigilator_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15)
) ENGINE=InnoDB;

-- =============================================================================
-- Table 6: exam_sessions
-- Academic exam cycles (e.g., Mid-Sem, End-Sem, Supplementary)
-- =============================================================================
CREATE TABLE exam_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    session_type ENUM('MID_SEM', 'END_SEM', 'SUPPLEMENTARY') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    CHECK(end_date >= start_date)
) ENGINE=InnoDB;

-- =============================================================================
-- Table 7: schedules
-- Timetable allocation mapping course, room, date, and time slot
-- =============================================================================
CREATE TABLE schedules (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    course_id INT NOT NULL,
    room_id INT NOT NULL,
    exam_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (session_id) REFERENCES exam_sessions(session_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    UNIQUE KEY unique_room_slot (room_id, exam_date, start_time),
    CHECK(end_time > start_time)
) ENGINE=InnoDB;

-- =============================================================================
-- Table 8: schedule_invigilators
-- Assignment of invigilators to specific exam schedules
-- =============================================================================
CREATE TABLE schedule_invigilators (
    id INT PRIMARY KEY AUTO_INCREMENT,
    schedule_id INT NOT NULL,
    invigilator_id INT NOT NULL,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE,
    FOREIGN KEY (invigilator_id) REFERENCES invigilators(invigilator_id),
    UNIQUE KEY unique_assignment (schedule_id, invigilator_id)
) ENGINE=InnoDB;

-- =============================================================================
-- Table 9: registrations
-- Course registrations for students in a specific exam session
-- =============================================================================
CREATE TABLE registrations (
    registration_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    session_id INT NOT NULL,
    registered_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (session_id) REFERENCES exam_sessions(session_id),
    UNIQUE KEY unique_reg (student_id, course_id, session_id)
) ENGINE=InnoDB;

-- =============================================================================
-- Table 10: marks
-- Evaluated scores secured by students in their registered courses
-- =============================================================================
CREATE TABLE marks (
    mark_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_id INT NOT NULL UNIQUE,
    marks_obtained DECIMAL(5,2) NOT NULL CHECK(marks_obtained BETWEEN 0 AND 100),
    max_marks INT NOT NULL DEFAULT 100,
    FOREIGN KEY (registration_id) REFERENCES registrations(registration_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- Table 11: grade_rules
-- Grading policy and cutoffs defined for exam sessions
-- =============================================================================
CREATE TABLE grade_rules (
    rule_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    min_marks DECIMAL(5,2) NOT NULL,
    max_marks DECIMAL(5,2) NOT NULL,
    grade VARCHAR(2) NOT NULL,
    grade_point DECIMAL(3,1) NOT NULL,
    FOREIGN KEY (session_id) REFERENCES exam_sessions(session_id),
    UNIQUE KEY unique_grade (session_id, grade),
    CHECK(max_marks >= min_marks)
) ENGINE=InnoDB;

-- =============================================================================
-- Table 12: results
-- Processed grade and grade point outcomes for registered courses
-- =============================================================================
CREATE TABLE results (
    result_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_id INT NOT NULL UNIQUE,
    grade VARCHAR(2) NOT NULL,
    grade_point DECIMAL(3,1) NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (registration_id) REFERENCES registrations(registration_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- Table 13: revaluation_requests
-- Requests submitted by students for review or re-evaluation of marks
-- =============================================================================
CREATE TABLE revaluation_requests (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_id INT NOT NULL,
    reason TEXT NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
    requested_date DATE DEFAULT (CURRENT_DATE),
    resolved_date DATE NULL,
    new_marks DECIMAL(5,2) NULL,
    FOREIGN KEY (registration_id) REFERENCES registrations(registration_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- Performance Optimization Indexes
-- =============================================================================
CREATE INDEX idx_students_programme ON students(programme_id);
CREATE INDEX idx_courses_programme ON courses(programme_id);
CREATE INDEX idx_schedules_session ON schedules(session_id);
CREATE INDEX idx_schedules_date ON schedules(exam_date);
CREATE INDEX idx_registrations_student ON registrations(student_id);
CREATE INDEX idx_registrations_session ON registrations(session_id);
CREATE INDEX idx_marks_registration ON marks(registration_id);
CREATE INDEX idx_results_published ON results(is_published);

-- =============================================================================
-- Database Views
-- =============================================================================

-- View 1: v_exam_schedule
-- Overview of scheduled examinations with course and venue details
CREATE OR REPLACE VIEW v_exam_schedule AS
SELECT 
    s.schedule_id,
    es.name AS session_name,
    c.course_code,
    c.name AS course_name,
    r.room_number,
    r.building,
    s.exam_date,
    s.start_time,
    s.end_time
FROM schedules s
JOIN courses c ON s.course_id = c.course_id
JOIN rooms r ON s.room_id = r.room_id
JOIN exam_sessions es ON s.session_id = es.session_id;

-- View 2: v_student_results
-- Consolidated student marks, grades, and publication status
CREATE OR REPLACE VIEW v_student_results AS
SELECT 
    st.roll_number,
    st.name AS student_name,
    c.course_code,
    c.name AS course_name,
    es.name AS session_name,
    res.grade,
    res.grade_point,
    res.is_published
FROM results res
JOIN registrations reg ON res.registration_id = reg.registration_id
JOIN students st ON reg.student_id = st.student_id
JOIN courses c ON reg.course_id = c.course_id
JOIN exam_sessions es ON reg.session_id = es.session_id;

-- View 3: v_hall_tickets
-- Hall ticket view linking registered students to their specific exam schedules
CREATE OR REPLACE VIEW v_hall_tickets AS
SELECT 
    reg.registration_id,
    st.student_id,
    st.roll_number,
    st.name AS student_name,
    st.email,
    p.name AS programme_name,
    es.session_id,
    es.name AS session_name,
    c.course_id,
    c.course_code,
    c.name AS course_name,
    sch.schedule_id,
    sch.exam_date,
    sch.start_time,
    sch.end_time,
    rm.room_number,
    rm.building
FROM registrations reg
JOIN students st ON reg.student_id = st.student_id
JOIN programmes p ON st.programme_id = p.programme_id
JOIN courses c ON reg.course_id = c.course_id
JOIN exam_sessions es ON reg.session_id = es.session_id
JOIN schedules sch ON sch.course_id = reg.course_id AND sch.session_id = reg.session_id
JOIN rooms rm ON sch.room_id = rm.room_id;

-- View 4: v_grade_distribution
-- Aggregate breakdown of awarded grades across exam sessions
CREATE OR REPLACE VIEW v_grade_distribution AS
SELECT 
    es.session_id,
    es.name AS session_name,
    res.grade,
    COUNT(*) AS count
FROM results res
JOIN registrations reg ON res.registration_id = reg.registration_id
JOIN exam_sessions es ON reg.session_id = es.session_id
GROUP BY es.session_id, es.name, res.grade;

-- View 5: v_pass_percentage
-- Performance statistics per course and exam session
CREATE OR REPLACE VIEW v_pass_percentage AS
SELECT 
    es.session_id,
    es.name AS session_name,
    c.course_id,
    c.course_code,
    c.name AS course_name,
    COUNT(res.result_id) AS total_students,
    SUM(CASE WHEN res.grade != 'F' THEN 1 ELSE 0 END) AS passed_students,
    SUM(CASE WHEN res.grade = 'F' THEN 1 ELSE 0 END) AS failed_students,
    ROUND((SUM(CASE WHEN res.grade != 'F' THEN 1 ELSE 0 END) * 100.0) / COUNT(res.result_id), 2) AS pass_percentage
FROM results res
JOIN registrations reg ON res.registration_id = reg.registration_id
JOIN exam_sessions es ON reg.session_id = es.session_id
JOIN courses c ON reg.course_id = c.course_id
GROUP BY es.session_id, es.name, c.course_id, c.course_code, c.name;
