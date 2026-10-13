-- ExamDesk Pro database schema
-- Relationship overview:
--   courses 1-to-many exams; rooms 1-to-many exams
--   students many-to-many exams through registrations
--   each registration can have one result

PRAGMA foreign_keys = ON;

-- Stores student identity and academic details.
CREATE TABLE IF NOT EXISTS students (
    id       INTEGER PRIMARY KEY,
    roll     TEXT UNIQUE NOT NULL,
    name     TEXT NOT NULL,
    dept     TEXT NOT NULL,
    semester INTEGER NOT NULL,
    email    TEXT DEFAULT ''
);

-- Stores the course catalogue. Each course can have multiple exams.
CREATE TABLE IF NOT EXISTS courses (
    id       INTEGER PRIMARY KEY,
    code     TEXT UNIQUE NOT NULL,
    name     TEXT NOT NULL,
    dept     TEXT NOT NULL,
    semester INTEGER NOT NULL,
    credits  INTEGER NOT NULL DEFAULT 3
);

-- Stores exam halls, labs, and their seating capacity.
CREATE TABLE IF NOT EXISTS rooms (
    id       INTEGER PRIMARY KEY,
    name     TEXT UNIQUE NOT NULL,
    capacity INTEGER NOT NULL,
    location TEXT DEFAULT ''
);

-- Connects a course and a room to an exam date and time slot.
CREATE TABLE IF NOT EXISTS exams (
    id         INTEGER PRIMARY KEY,
    course_id  INTEGER NOT NULL REFERENCES courses(id),
    exam_date  TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time   TEXT NOT NULL,
    room_id    INTEGER NOT NULL REFERENCES rooms(id),
    notes      TEXT DEFAULT ''
);

-- Junction table: a student may register for many exams, and an exam
-- may have many students. The pair must be unique to prevent duplicates.
CREATE TABLE IF NOT EXISTS registrations (
    id         INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    exam_id    INTEGER NOT NULL REFERENCES exams(id),
    UNIQUE (student_id, exam_id)
);

-- Stores marks for a registration. UNIQUE allows at most one result per registration.
CREATE TABLE IF NOT EXISTS results (
    id              INTEGER PRIMARY KEY,
    registration_id INTEGER UNIQUE NOT NULL REFERENCES registrations(id),
    marks           REAL NOT NULL,
    maximum         REAL NOT NULL,
    remarks          TEXT DEFAULT ''
);