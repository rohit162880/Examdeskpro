-- =============================================================================
-- Examination Scheduling and Result Processing System
-- Sample Seed Data Script
-- Database: exam_scheduling_db
-- =============================================================================

USE exam_scheduling_db;

-- -----------------------------------------------------------------------------
-- 1. Programmes (4 academic programmes)
-- -----------------------------------------------------------------------------
INSERT INTO programmes (programme_id, name, duration_years, degree_type) VALUES
(1, 'B.Tech Computer Science and Engineering', 4, 'B.Tech'),
(2, 'B.Tech Electronics and Communication Engineering', 4, 'B.Tech'),
(3, 'B.Tech Mechanical Engineering', 4, 'B.Tech'),
(4, 'B.Tech Civil Engineering', 4, 'B.Tech');

-- -----------------------------------------------------------------------------
-- 2. Courses (12 courses, 3 per programme)
-- -----------------------------------------------------------------------------
INSERT INTO courses (course_id, course_code, name, credits, programme_id, semester) VALUES
-- Computer Science & Engineering (Programme 1)
(1, 'CS301', 'Database Management Systems', 4, 1, 5),
(2, 'CS302', 'Operating Systems', 4, 1, 5),
(3, 'CS303', 'Computer Networks', 3, 1, 5),
-- Electronics & Communication Engineering (Programme 2)
(4, 'EC201', 'Digital Electronics', 4, 2, 3),
(5, 'EC202', 'Signals and Systems', 4, 2, 3),
(6, 'EC301', 'VLSI Design', 3, 2, 5),
-- Mechanical Engineering (Programme 3)
(7, 'ME201', 'Thermodynamics', 4, 3, 3),
(8, 'ME202', 'Fluid Mechanics', 4, 3, 3),
(9, 'ME301', 'Design of Machine Elements', 4, 3, 5),
-- Civil Engineering (Programme 4)
(10, 'CE201', 'Structural Analysis', 4, 4, 3),
(11, 'CE202', 'Surveying and Geomatics', 3, 4, 3),
(12, 'CE301', 'Environmental Engineering', 3, 4, 5);

-- -----------------------------------------------------------------------------
-- 3. Students (15 students with realistic Indian names)
-- -----------------------------------------------------------------------------
INSERT INTO students (student_id, roll_number, name, email, phone, programme_id, admission_year) VALUES
(1, '2022CSE001', 'Aarav Sharma', 'aarav.sharma@example.edu.in', '9876543210', 1, 2022),
(2, '2022CSE002', 'Ananya Iyer', 'ananya.iyer@example.edu.in', '9876543211', 1, 2022),
(3, '2022CSE003', 'Rohan Verma', 'rohan.verma@example.edu.in', '9876543212', 1, 2022),
(4, '2022CSE004', 'Diya Patel', 'diya.patel@example.edu.in', '9876543213', 1, 2022),
(5, '2023ECE001', 'Aditya Nair', 'aditya.nair@example.edu.in', '9876543214', 2, 2023),
(6, '2023ECE002', 'Sneha Kulkarni', 'sneha.kulkarni@example.edu.in', '9876543215', 2, 2023),
(7, '2023ECE003', 'Vikram Rao', 'vikram.rao@example.edu.in', '9876543216', 2, 2023),
(8, '2023ECE004', 'Pooja Hegde', 'pooja.hegde@example.edu.in', '9876543217', 2, 2023),
(9, '2023MEC001', 'Arjun Reddy', 'arjun.reddy@example.edu.in', '9876543218', 3, 2023),
(10, '2023MEC002', 'Kavita Joshi', 'kavita.joshi@example.edu.in', '9876543219', 3, 2023),
(11, '2023MEC003', 'Manish Kumar', 'manish.kumar@example.edu.in', '9876543220', 3, 2023),
(12, '2023CIV001', 'Rithvik Menon', 'rithvik.menon@example.edu.in', '9876543221', 4, 2023),
(13, '2023CIV002', 'Tanvi Deshmukh', 'tanvi.deshmukh@example.edu.in', '9876543222', 4, 2023),
(14, '2022CSE005', 'Siddharth Gupta', 'siddharth.gupta@example.edu.in', '9876543223', 1, 2022),
(15, '2023CIV003', 'Meera Nambiar', 'meera.nambiar@example.edu.in', '9876543224', 4, 2023);

-- -----------------------------------------------------------------------------
-- 4. Rooms (6 examination halls across Main & Science blocks)
-- -----------------------------------------------------------------------------
INSERT INTO rooms (room_id, room_number, building, capacity, has_projector) VALUES
(1, 'LH-101', 'Main Block', 120, TRUE),
(2, 'LH-102', 'Main Block', 100, TRUE),
(3, 'LH-103', 'Main Block', 80, FALSE),
(4, 'LH-104', 'Science Block', 150, TRUE),
(5, 'LH-105', 'Science Block', 200, TRUE),
(6, 'LH-106', 'Science Block', 60, FALSE);

-- -----------------------------------------------------------------------------
-- 5. Invigilators (6 faculty members)
-- -----------------------------------------------------------------------------
INSERT INTO invigilators (invigilator_id, name, department, email, phone) VALUES
(1, 'Dr. Rajesh Ramanathan', 'Computer Science and Engineering', 'rajesh.ramanathan@example.edu.in', '9123456701'),
(2, 'Dr. Meenakshi Sundaram', 'Computer Science and Engineering', 'meenakshi.s@example.edu.in', '9123456702'),
(3, 'Prof. Suresh Venkatesh', 'Electronics and Communication Engineering', 'suresh.v@example.edu.in', '9123456703'),
(4, 'Dr. Priya Swaminathan', 'Electronics and Communication Engineering', 'priya.s@example.edu.in', '9123456704'),
(5, 'Dr. Harish Chandra', 'Mechanical Engineering', 'harish.c@example.edu.in', '9123456705'),
(6, 'Prof. Sunita Agarwal', 'Civil Engineering', 'sunita.a@example.edu.in', '9123456706');

-- -----------------------------------------------------------------------------
-- 6. Exam Sessions (2 cycles: End Sem and Mid Sem)
-- -----------------------------------------------------------------------------
INSERT INTO exam_sessions (session_id, name, session_type, start_date, end_date, is_active) VALUES
(1, 'November 2024 End Semester', 'END_SEM', '2024-11-15', '2024-11-30', TRUE),
(2, 'March 2025 Mid Semester', 'MID_SEM', '2025-03-10', '2025-03-25', TRUE);

-- -----------------------------------------------------------------------------
-- 7. Grade Rules (Standard grading scale for Session 1 and Session 2)
-- -----------------------------------------------------------------------------
INSERT INTO grade_rules (session_id, min_marks, max_marks, grade, grade_point) VALUES
(1, 90.00, 100.00, 'O',  10.0),
(1, 80.00,  89.99, 'A+',  9.0),
(1, 70.00,  79.99, 'A',   8.0),
(1, 60.00,  69.99, 'B+',  7.0),
(1, 50.00,  59.99, 'B',   6.0),
(1, 40.00,  49.99, 'C',   5.0),
(1,  0.00,  39.99, 'F',   0.0),
-- Session 2 Rules
(2, 90.00, 100.00, 'O',  10.0),
(2, 80.00,  89.99, 'A+',  9.0),
(2, 70.00,  79.99, 'A',   8.0),
(2, 60.00,  69.99, 'B+',  7.0),
(2, 50.00,  59.99, 'B',   6.0),
(2, 40.00,  49.99, 'C',   5.0),
(2,  0.00,  39.99, 'F',   0.0);

-- -----------------------------------------------------------------------------
-- 8. Schedules (10 conflict-free exam slots)
-- -----------------------------------------------------------------------------
INSERT INTO schedules (schedule_id, session_id, course_id, room_id, exam_date, start_time, end_time) VALUES
(1,  1, 1,  1, '2024-11-18', '09:30:00', '12:30:00'),
(2,  1, 2,  2, '2024-11-20', '09:30:00', '12:30:00'),
(3,  1, 3,  1, '2024-11-22', '09:30:00', '12:30:00'),
(4,  1, 4,  3, '2024-11-18', '09:30:00', '12:30:00'),
(5,  1, 5,  4, '2024-11-20', '14:00:00', '17:00:00'),
(6,  1, 7,  5, '2024-11-19', '09:30:00', '12:30:00'),
(7,  1, 8,  2, '2024-11-21', '14:00:00', '17:00:00'),
(8,  1, 10, 6, '2024-11-19', '14:00:00', '17:00:00'),
(9,  2, 1,  1, '2025-03-11', '10:00:00', '12:00:00'),
(10, 2, 4,  2, '2025-03-12', '10:00:00', '12:00:00');

-- -----------------------------------------------------------------------------
-- 9. Schedule Invigilators (Faculty duties assigned to schedules)
-- -----------------------------------------------------------------------------
INSERT INTO schedule_invigilators (id, schedule_id, invigilator_id) VALUES
(1,  1,  1),
(2,  2,  2),
(3,  3,  1),
(4,  4,  3),
(5,  5,  4),
(6,  6,  5),
(7,  7,  5),
(8,  8,  6),
(9,  9,  2),
(10, 10, 3);

-- -----------------------------------------------------------------------------
-- 10. Registrations (20 registrations linking students to courses & sessions)
-- -----------------------------------------------------------------------------
INSERT INTO registrations (registration_id, student_id, course_id, session_id, registered_date) VALUES
(1,  1,  1,  1, '2024-10-20'),
(2,  1,  2,  1, '2024-10-20'),
(3,  1,  3,  1, '2024-10-20'),
(4,  2,  1,  1, '2024-10-21'),
(5,  2,  2,  1, '2024-10-21'),
(6,  2,  3,  1, '2024-10-21'),
(7,  3,  1,  1, '2024-10-21'),
(8,  3,  2,  1, '2024-10-21'),
(9,  4,  1,  1, '2024-10-22'),
(10, 4,  2,  1, '2024-10-22'),
(11, 5,  4,  1, '2024-10-22'),
(12, 5,  5,  1, '2024-10-22'),
(13, 6,  4,  1, '2024-10-23'),
(14, 6,  5,  1, '2024-10-23'),
(15, 7,  4,  1, '2024-10-23'),
(16, 9,  7,  1, '2024-10-24'),
(17, 9,  8,  1, '2024-10-24'),
(18, 10, 7,  1, '2024-10-24'),
(19, 12, 10, 1, '2024-10-25'),
(20, 13, 10, 1, '2024-10-25');

-- -----------------------------------------------------------------------------
-- 11. Marks (15 entries across registered courses)
-- -----------------------------------------------------------------------------
INSERT INTO marks (mark_id, registration_id, marks_obtained, max_marks) VALUES
(1,  1,  92.50, 100),
(2,  2,  84.00, 100),
(3,  3,  78.50, 100),
(4,  4,  95.00, 100),
(5,  5,  88.50, 100),
(6,  6,  72.00, 100),
(7,  7,  65.50, 100),
(8,  8,  54.00, 100),
(9,  9,  81.00, 100),
(10, 10, 45.00, 100),
(11, 11, 76.50, 100),
(12, 12, 32.00, 100),
(13, 13, 89.00, 100),
(14, 14, 68.00, 100),
(15, 15, 58.50, 100);

-- -----------------------------------------------------------------------------
-- 12. Results (10 computed outcomes based on marks & grading rules)
-- -----------------------------------------------------------------------------
INSERT INTO results (result_id, registration_id, grade, grade_point, is_published) VALUES
(1,  1,  'O',  10.0, TRUE),
(2,  2,  'A+',  9.0, TRUE),
(3,  3,  'A',   8.0, TRUE),
(4,  4,  'O',  10.0, TRUE),
(5,  5,  'A+',  9.0, TRUE),
(6,  6,  'A',   8.0, TRUE),
(7,  7,  'B+',  7.0, TRUE),
(8,  8,  'B',   6.0, TRUE),
(9,  9,  'A+',  9.0, TRUE),
(10, 12, 'F',   0.0, TRUE);

-- -----------------------------------------------------------------------------
-- 13. Revaluation Requests (2 requests: 1 PENDING, 1 APPROVED)
-- -----------------------------------------------------------------------------
INSERT INTO revaluation_requests (request_id, registration_id, reason, status, requested_date, resolved_date, new_marks) VALUES
(1, 10, 'Discrepancy observed in Section B evaluation, requested recount of question 4 marks.', 'PENDING', '2024-12-05', NULL, NULL),
(2, 12, 'Omission of answered sub-questions on page 14 verified upon examination script inspection.', 'APPROVED', '2024-12-02', '2024-12-08', 42.00);
