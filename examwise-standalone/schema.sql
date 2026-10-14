PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS programs (
  program_id INTEGER PRIMARY KEY,
  program_name TEXT NOT NULL UNIQUE CHECK (length(trim(program_name)) > 0),
  department TEXT NOT NULL CHECK (length(trim(department)) > 0)
);

CREATE TABLE IF NOT EXISTS courses (
  course_id INTEGER PRIMARY KEY,
  course_code TEXT NOT NULL UNIQUE,
  course_name TEXT NOT NULL,
  credits INTEGER NOT NULL CHECK (credits > 0),
  program_id INTEGER NOT NULL REFERENCES programs(program_id)
);

CREATE INDEX IF NOT EXISTS idx_courses_program ON courses(program_id);

CREATE TABLE IF NOT EXISTS students (
  student_id INTEGER PRIMARY KEY,
  roll_number TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL CHECK (length(trim(full_name)) > 0),
  email TEXT NOT NULL UNIQUE,
  program_id INTEGER NOT NULL REFERENCES programs(program_id),
  semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 12)
);

CREATE INDEX IF NOT EXISTS idx_students_program ON students(program_id);

CREATE TABLE IF NOT EXISTS rooms (
  room_id INTEGER PRIMARY KEY,
  room_name TEXT NOT NULL UNIQUE,
  building TEXT NOT NULL,
  capacity INTEGER NOT NULL CHECK (capacity > 0)
);

CREATE TABLE IF NOT EXISTS invigilators (
  invigilator_id INTEGER PRIMARY KEY,
  full_name TEXT NOT NULL,
  department TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS exam_sessions (
  session_id INTEGER PRIMARY KEY,
  course_id INTEGER NOT NULL REFERENCES courses(course_id),
  exam_date TEXT NOT NULL,
  start_time TEXT NOT NULL,
  end_time TEXT NOT NULL,
  room_id INTEGER NOT NULL REFERENCES rooms(room_id),
  invigilator_id INTEGER NOT NULL REFERENCES invigilators(invigilator_id),
  CHECK (start_time < end_time)
);

CREATE INDEX IF NOT EXISTS idx_sessions_date ON exam_sessions(exam_date);
CREATE INDEX IF NOT EXISTS idx_sessions_room_date ON exam_sessions(room_id, exam_date);
CREATE INDEX IF NOT EXISTS idx_sessions_invigilator_date ON exam_sessions(invigilator_id, exam_date);

CREATE TRIGGER IF NOT EXISTS trg_session_room_no_overlap
BEFORE INSERT ON exam_sessions
WHEN EXISTS (
  SELECT 1 FROM exam_sessions e
  WHERE e.exam_date = NEW.exam_date
    AND e.room_id = NEW.room_id
    AND NEW.start_time < e.end_time
    AND NEW.end_time > e.start_time
)
BEGIN
  SELECT RAISE(ABORT, 'Room is already allocated during this time');
END;

CREATE TRIGGER IF NOT EXISTS trg_session_invigilator_no_overlap
BEFORE INSERT ON exam_sessions
WHEN EXISTS (
  SELECT 1 FROM exam_sessions e
  WHERE e.exam_date = NEW.exam_date
    AND e.invigilator_id = NEW.invigilator_id
    AND NEW.start_time < e.end_time
    AND NEW.end_time > e.start_time
)
BEGIN
  SELECT RAISE(ABORT, 'Invigilator is already allocated during this time');
END;

CREATE TRIGGER IF NOT EXISTS trg_session_room_no_overlap_update
BEFORE UPDATE ON exam_sessions
WHEN EXISTS (
  SELECT 1 FROM exam_sessions e
  WHERE e.session_id <> NEW.session_id
    AND e.exam_date = NEW.exam_date
    AND e.room_id = NEW.room_id
    AND NEW.start_time < e.end_time
    AND NEW.end_time > e.start_time
)
BEGIN
  SELECT RAISE(ABORT, 'Room is already allocated during this time');
END;

CREATE TRIGGER IF NOT EXISTS trg_session_invigilator_no_overlap_update
BEFORE UPDATE ON exam_sessions
WHEN EXISTS (
  SELECT 1 FROM exam_sessions e
  WHERE e.session_id <> NEW.session_id
    AND e.exam_date = NEW.exam_date
    AND e.invigilator_id = NEW.invigilator_id
    AND NEW.start_time < e.end_time
    AND NEW.end_time > e.start_time
)
BEGIN
  SELECT RAISE(ABORT, 'Invigilator is already allocated during this time');
END;

CREATE TABLE IF NOT EXISTS registrations (
  registration_id INTEGER PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES students(student_id),
  session_id INTEGER NOT NULL REFERENCES exam_sessions(session_id),
  registration_date TEXT NOT NULL DEFAULT CURRENT_DATE,
  status TEXT NOT NULL DEFAULT 'registered' CHECK (status IN ('registered', 'withdrawn')),
  UNIQUE (student_id, session_id)
);

CREATE INDEX IF NOT EXISTS idx_registrations_session ON registrations(session_id);
CREATE INDEX IF NOT EXISTS idx_registrations_student ON registrations(student_id);

CREATE TRIGGER IF NOT EXISTS trg_registration_program_match
BEFORE INSERT ON registrations
WHEN (
  SELECT s.program_id FROM students s WHERE s.student_id = NEW.student_id
) <> (
  SELECT c.program_id
  FROM exam_sessions e JOIN courses c ON c.course_id = e.course_id
  WHERE e.session_id = NEW.session_id
)
BEGIN
  SELECT RAISE(ABORT, 'Student is not enrolled in this course program');
END;

CREATE TRIGGER IF NOT EXISTS trg_registration_capacity
BEFORE INSERT ON registrations
WHEN (
  SELECT COUNT(*) FROM registrations r WHERE r.session_id = NEW.session_id
) >= (
  SELECT room.capacity
  FROM exam_sessions e JOIN rooms room ON room.room_id = e.room_id
  WHERE e.session_id = NEW.session_id
)
BEGIN
  SELECT RAISE(ABORT, 'Room capacity exceeded');
END;

CREATE TABLE IF NOT EXISTS grade_rules (
  grade_rule_id INTEGER PRIMARY KEY,
  grade_label TEXT NOT NULL UNIQUE,
  min_mark INTEGER NOT NULL CHECK (min_mark BETWEEN 0 AND 100),
  max_mark INTEGER NOT NULL CHECK (max_mark BETWEEN min_mark AND 100)
);

CREATE TRIGGER IF NOT EXISTS trg_grade_range_no_overlap
BEFORE INSERT ON grade_rules
WHEN EXISTS (
  SELECT 1 FROM grade_rules g
  WHERE NEW.min_mark <= g.max_mark AND NEW.max_mark >= g.min_mark
)
BEGIN
  SELECT RAISE(ABORT, 'Grade ranges may not overlap');
END;

CREATE TRIGGER IF NOT EXISTS trg_grade_range_no_overlap_update
BEFORE UPDATE ON grade_rules
WHEN EXISTS (
  SELECT 1 FROM grade_rules g
  WHERE g.grade_rule_id <> NEW.grade_rule_id
    AND NEW.min_mark <= g.max_mark AND NEW.max_mark >= g.min_mark
)
BEGIN
  SELECT RAISE(ABORT, 'Grade ranges may not overlap');
END;

CREATE TABLE IF NOT EXISTS marks (
  mark_id INTEGER PRIMARY KEY,
  registration_id INTEGER NOT NULL UNIQUE REFERENCES registrations(registration_id),
  internal_marks REAL NOT NULL CHECK (internal_marks BETWEEN 0 AND 20),
  external_marks REAL NOT NULL CHECK (external_marks BETWEEN 0 AND 80),
  entered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS session_publications (
  session_id INTEGER PRIMARY KEY REFERENCES exam_sessions(session_id),
  published_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS revaluation_requests (
  request_id INTEGER PRIMARY KEY,
  registration_id INTEGER NOT NULL UNIQUE REFERENCES registrations(registration_id),
  request_date TEXT NOT NULL DEFAULT CURRENT_DATE,
  reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected'))
);

CREATE VIEW IF NOT EXISTS results AS
SELECT
  reg.registration_id,
  st.student_id,
  st.roll_number,
  st.full_name AS student_name,
  e.session_id,
  c.course_code,
  c.course_name,
  m.internal_marks,
  m.external_marks,
  m.internal_marks + m.external_marks AS total_marks,
  gr.grade_label AS grade,
  CASE WHEN (m.internal_marks + m.external_marks) >= 40 THEN 'PASS' ELSE 'FAIL' END AS outcome
FROM marks m
JOIN registrations reg ON reg.registration_id = m.registration_id
JOIN students st ON st.student_id = reg.student_id
JOIN exam_sessions e ON e.session_id = reg.session_id
JOIN courses c ON c.course_id = e.course_id
LEFT JOIN grade_rules gr
  ON (m.internal_marks + m.external_marks) BETWEEN gr.min_mark AND gr.max_mark;

INSERT OR IGNORE INTO programs VALUES
  (1, 'B.Sc. Computer Science', 'School of Computing');

INSERT OR IGNORE INTO courses VALUES
  (101, 'CS301', 'Database Management Systems', 4, 1),
  (102, 'CS302', 'Web Engineering', 4, 1),
  (103, 'CS303', 'Data Structures', 4, 1);

INSERT OR IGNORE INTO students VALUES
  (1, 'CS2026-001', 'Aarav Mehta', 'aarav.mehta@campus.edu', 1, 5),
  (2, 'CS2026-002', 'Ananya Rao', 'ananya.rao@campus.edu', 1, 5),
  (3, 'CS2026-003', 'Kabir Shah', 'kabir.shah@campus.edu', 1, 5),
  (4, 'CS2026-004', 'Mira Iyer', 'mira.iyer@campus.edu', 1, 5),
  (5, 'CS2026-005', 'Dev Patel', 'dev.patel@campus.edu', 1, 5);

INSERT OR IGNORE INTO rooms VALUES
  (1, 'Main Hall A', 'Block A', 60),
  (2, 'Innovation Lab', 'Block C', 30),
  (3, 'Seminar Hall', 'Block B', 40);

INSERT OR IGNORE INTO invigilators VALUES
  (1, 'Dr. Priya Menon', 'Computer Science', 'p.menon@campus.edu'),
  (2, 'Prof. Arjun Rao', 'Computer Science', 'a.rao@campus.edu'),
  (3, 'Dr. Neha Kapoor', 'Computer Science', 'n.kapoor@campus.edu');

INSERT OR IGNORE INTO exam_sessions VALUES
  (1, 101, '2026-10-08', '09:30', '12:30', 1, 1),
  (2, 102, '2026-10-10', '09:30', '12:30', 2, 2),
  (3, 103, '2026-10-20', '09:30', '12:30', 1, 3),
  (4, 101, '2026-10-22', '13:30', '16:30', 2, 2);

INSERT OR IGNORE INTO registrations VALUES
  (1, 1, 1, '2026-10-01', 'registered'),
  (2, 2, 1, '2026-10-01', 'registered'),
  (3, 3, 1, '2026-10-01', 'registered'),
  (4, 4, 1, '2026-10-01', 'registered'),
  (5, 5, 1, '2026-10-01', 'registered'),
  (6, 1, 2, '2026-10-01', 'registered'),
  (7, 2, 2, '2026-10-01', 'registered'),
  (8, 3, 2, '2026-10-01', 'registered'),
  (9, 4, 2, '2026-10-01', 'registered'),
  (10, 5, 2, '2026-10-01', 'registered'),
  (11, 1, 3, '2026-10-01', 'registered'),
  (12, 2, 3, '2026-10-01', 'registered'),
  (13, 3, 3, '2026-10-01', 'registered'),
  (14, 4, 3, '2026-10-01', 'registered'),
  (15, 5, 3, '2026-10-01', 'registered');

INSERT OR IGNORE INTO grade_rules VALUES
  (1, 'A+', 90, 100),
  (2, 'A', 80, 89),
  (3, 'B', 70, 79),
  (4, 'C', 60, 69),
  (5, 'D', 40, 59),
  (6, 'F', 0, 39);

INSERT OR IGNORE INTO marks VALUES
  (1, 1, 18, 66, '2026-10-09'),
  (2, 2, 17, 58, '2026-10-09'),
  (3, 3, 15, 52, '2026-10-09'),
  (4, 4, 19, 72, '2026-10-09'),
  (5, 6, 19, 69, '2026-10-11'),
  (6, 7, 16, 55, '2026-10-11'),
  (7, 8, 14, 49, '2026-10-11'),
  (8, 9, 18, 73, '2026-10-11');

INSERT OR IGNORE INTO session_publications (session_id, published_at) VALUES
  (1, '2026-10-12 12:00:00'),
  (2, '2026-10-12 12:00:00');

-- The UI and SQL triggers enforce non-overlapping room/invigilator allocations,
-- room capacity, valid marks, program registration, and non-overlapping grades.

