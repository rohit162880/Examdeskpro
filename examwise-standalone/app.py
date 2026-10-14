from __future__ import annotations

import html
import sqlite3
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

ROOT = Path(__file__).resolve().parent
DATABASE = ROOT / "examwise.sqlite3"
SCHEMA_FILE = ROOT / "schema.sql"
HOST = "127.0.0.1"
PORT = 8000

STYLE = """
:root{--navy:#13213a;--ink:#1d2b45;--muted:#7b879a;--blue:#4b68df;--line:#e8edf3;--bg:#f5f7fa;--green:#249a73;--red:#c95d5c;--orange:#bf7c35}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 "Segoe UI",Arial,sans-serif}
a{color:inherit;text-decoration:none}button,input,select,textarea{font:inherit}
.shell{min-height:100vh}.sidebar{position:fixed;inset:0 auto 0 0;width:238px;padding:24px 16px;background:var(--navy);color:#fff;display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:11px;margin:0 7px 36px;font-size:18px;font-weight:800;letter-spacing:-.5px}.brand-mark{display:grid;place-items:center;width:37px;height:37px;border-radius:11px;background:#526fe7;font-size:22px}.brand small{display:block;color:#8392ac;font-size:8px;letter-spacing:1.5px}
.nav-caption{padding:0 11px;margin-bottom:10px;color:#7788a3;font-size:9px;font-weight:700;letter-spacing:1.3px}.nav{display:grid;gap:5px}.nav a{display:flex;align-items:center;gap:11px;padding:10px 12px;border-radius:8px;color:#aeb9cc;font-size:12px}.nav a:hover,.nav a.active{background:#273956;color:#fff}.nav-icon{width:20px;text-align:center;color:#9db0ff;font-size:16px}
.side-note{margin-top:auto;padding:12px 11px;border:1px solid #ffffff1c;border-radius:9px;color:#b7c3d7;font-size:10px}.side-note b{display:block;color:#fff;font-size:11px;margin-bottom:3px}
.main{margin-left:238px;min-height:100vh}.topbar{height:65px;padding:0 38px;background:#fff;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;color:#8894a7;font-size:11px}.topbar strong{color:#33415a;font-weight:600}.top-right{color:#7b879a}
.content{max-width:1500px;margin:auto;padding:30px 38px 24px}.title-row{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}.eyebrow{color:#5975d8;font-size:9px;font-weight:800;letter-spacing:1.3px;margin-bottom:7px}h1{margin:0 0 4px;font-size:26px;line-height:1.2;letter-spacing:-.8px}h2{margin:0;color:#24324b;font-size:14px;line-height:1.3}h3{margin:0 0 6px;font-size:12px}p{margin:0;color:#8b96a8;font-size:11px}.muted{color:#8b96a8;font-size:10px}
.button{display:inline-flex;align-items:center;justify-content:center;gap:7px;border:1px solid transparent;border-radius:8px;padding:9px 14px;font-size:11px;font-weight:700;cursor:pointer}.primary{background:var(--blue);color:#fff;box-shadow:0 4px 10px #4b68df2e}.primary:hover{background:#3d59cf}.light{background:#fff;border-color:#e2e7ee;color:#56647a}.small-button{padding:6px 9px;font-size:9px}
.grid{display:grid;gap:14px}.metrics{grid-template-columns:repeat(4,minmax(0,1fr));margin-bottom:15px}.metric,.card{background:#fff;border:1px solid #edf0f4;border-radius:13px;box-shadow:0 3px 9px #28355005}.metric{padding:16px 18px;min-height:110px}.metric-label{display:flex;align-items:center;justify-content:space-between;color:#8290a4;font-size:10px}.metric-icon{width:27px;height:27px;display:grid;place-items:center;border-radius:8px;background:#edf1ff;color:#5571d8}.metric:nth-child(2) .metric-icon{background:#eaf8f2;color:#279b74}.metric:nth-child(3) .metric-icon{background:#fff3e8;color:#c9823f}.metric:nth-child(4) .metric-icon{background:#f2edff;color:#8261c5}.metric-value{margin-top:7px;font-size:25px;font-weight:800;letter-spacing:-.8px}.metric-foot{font-size:9px;color:#9aa4b2}
.dashboard-grid{grid-template-columns:minmax(0,1.25fr) minmax(280px,.85fr)}.card{padding:18px}.card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:13px}.card-head p{margin-top:4px}.text-link{font-size:10px;color:#5671d6;font-weight:700}
.upcoming{display:grid}.exam-row{display:grid;grid-template-columns:42px 1fr auto;align-items:center;gap:11px;padding:10px 0;border-top:1px solid #f0f2f6}.date-box{display:grid;place-content:center;text-align:center;width:39px;height:41px;background:#f1f4ff;color:#5571d8;border-radius:8px;line-height:1.1}.date-box b{font-size:15px}.date-box small{font-size:8px;text-transform:uppercase}.exam-main b{display:block;font-size:10px}.exam-main small{display:block;color:#929cad;font-size:9px;margin-top:3px}.room-name{font-size:9px;color:#77849a;white-space:nowrap}
.pass-value{display:flex;align-items:baseline;gap:8px;margin:19px 0 8px}.pass-value b{font-size:29px;letter-spacing:-1px}.pass-value span{font-size:10px;color:#8995a8}.bar{height:6px;background:#edf1f3;border-radius:10px;overflow:hidden}.bar span{display:block;height:100%;background:linear-gradient(90deg,#2eaa7e,#72d3a8);border-radius:10px}.grade-bars{height:62px;display:flex;align-items:flex-end;gap:8px;margin:17px 0 18px;border-bottom:1px solid var(--line)}.grade-bars div{flex:1;height:100%;display:flex;align-items:flex-end;justify-content:center;position:relative}.grade-bars i{width:14px;max-width:85%;min-height:4px;background:#9cb0f6;border-radius:4px 4px 0 0}.grade-bars div:nth-child(2n) i{background:#bdc9f4}.grade-bars small{position:absolute;bottom:-16px;color:#9ca5b2;font-size:8px}.legend{display:flex;gap:12px;color:#929cad;font-size:9px}.legend i{display:inline-block;width:6px;height:6px;border-radius:50%;background:#40b98e;margin-right:5px}.empty{padding:22px 10px;text-align:center;color:#97a1b1;font-size:11px}
.toolbar{display:flex;align-items:center;gap:10px;margin-bottom:14px}.search{display:flex;align-items:center;gap:8px;flex:1;max-width:420px;background:#fff;border:1px solid #e4e9ef;border-radius:8px;height:36px;padding:0 10px;color:#9ba5b3}.search input{border:0;outline:0;width:100%;font-size:10px}.toolbar .grow{flex:1}.select{background:#fff;border:1px solid #e4e9ef;border-radius:8px;height:36px;padding:0 10px;color:#68758a;font-size:10px}
.segment{display:flex;gap:3px;background:#fff;border:1px solid #e4e9ef;border-radius:8px;padding:3px}.segment a{padding:6px 9px;border-radius:6px;color:#8994a6;font-size:9px;font-weight:700}.segment a.sel{background:#edf1ff;color:#526dd7}
.table-card{padding:0;overflow:hidden}.table-head{padding:17px 18px 13px;display:flex;justify-content:space-between;align-items:center}.pill{display:inline-block;padding:4px 8px;border-radius:20px;background:#edf1ff;color:#5671d7;font-size:8px;font-weight:800;letter-spacing:.3px}.pill.green{background:#eaf8f2;color:#279b74}.pill.orange{background:#fff3e8;color:#bc7a38}.pill.red{background:#fff0ef;color:#c95d5c}.table-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;min-width:760px}th{text-align:left;padding:10px 13px;background:#fafbfd;border-top:1px solid #eef1f4;border-bottom:1px solid #edf0f4;color:#96a0af;font-size:8px;letter-spacing:.7px;white-space:nowrap}td{padding:11px 13px;border-bottom:1px solid #f0f2f5;color:#68758b;font-size:10px;vertical-align:middle}tr:last-child td{border-bottom:0}tbody tr:hover{background:#fbfcfe}.main-cell b{display:block;color:#34425a;font-size:10px}.main-cell small{display:block;color:#9aa3b1;font-size:8px;margin-top:3px}.course-badge,.person-badge{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:8px;margin-right:8px;background:#edf1ff;color:#5571d8;font-weight:700;font-size:9px}.person-badge{border-radius:50%;background:#f0eaff;color:#7856b8}.row-link{color:#5872d4;font-weight:700;font-size:9px}.right{text-align:right}
.form-card{max-width:760px;padding:20px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px}.field{display:grid;gap:5px}.field.full{grid-column:1/-1}.field label{font-size:9px;color:#58657b;font-weight:700}.field input,.field select,.field textarea{width:100%;height:37px;border:1px solid #dfe5ed;border-radius:7px;background:#fff;padding:0 10px;color:#34425a;font-size:10px;outline:0}.field textarea{height:80px;padding:9px;resize:vertical}.field input:focus,.field select:focus,.field textarea:focus{border-color:#8397e8;box-shadow:0 0 0 3px #5571d51a}.help{font-size:8px;color:#98a2b1}.form-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:17px;padding-top:14px;border-top:1px solid #eff1f4}.message{padding:10px 12px;border-radius:8px;background:#eaf8f2;color:#288d6d;font-size:10px;margin-bottom:15px}.error{background:#fff0ef;color:#b95350}
.stat-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin-bottom:14px}.mini{display:flex;justify-content:space-between;align-items:center;background:white;border:1px solid #edf0f4;border-radius:10px;padding:13px 15px}.mini span{color:#8490a3;font-size:9px}.mini b{font-size:19px}
.schema-grid{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:14px;align-items:start}.schema-content{display:grid;gap:14px}.schema-tabs{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:12px}.schema-tabs a{padding:6px 8px;border-radius:6px;background:#f4f6fa;color:#77849a;font-size:8px;font-weight:700}.schema-tabs a.sel{background:#edf1ff;color:#526dd7}.codebox{background:#14223a;border-radius:9px;overflow:hidden}.code-top{height:32px;padding:0 10px;display:flex;align-items:center;color:#9aabc1;border-bottom:1px solid #2a3a53;font-size:9px}.codebox pre{margin:0;padding:13px 15px;color:#c2d3e7;font:9px/1.65 Consolas,monospace;white-space:pre;overflow:auto;max-height:430px}.db-facts{display:grid;margin:12px 0}.fact{display:flex;justify-content:space-between;gap:10px;padding:8px 0;border-top:1px solid #eff1f4;color:#8792a4;font-size:9px}.fact b{color:#46536b;text-align:right}.sql-query{background:#172943;color:#b7cce6;padding:15px;border-radius:9px;font:8px/1.65 Consolas,monospace;white-space:pre-wrap;margin-top:10px}
.ticket{max-width:700px;border:1px dashed #b9c7e7;background:#fbfcff;padding:20px;border-radius:10px}.ticket h2{color:#526bd0;margin-bottom:12px}.ticket-row{display:flex;justify-content:space-between;gap:15px;padding:8px 0;border-top:1px solid #e9edf5;font-size:10px;color:#7b879a}.ticket-row b{color:#34425a;text-align:right}
.footer{display:flex;justify-content:space-between;gap:10px;padding:16px 2px 0;color:#9ba5b2;font-size:9px}
@media(max-width:1050px){.sidebar{width:205px}.main{margin-left:205px}.content{padding-left:24px;padding-right:24px}.topbar{padding:0 24px}.schema-grid{grid-template-columns:1fr 230px}}
@media(max-width:800px){.sidebar{width:64px;padding:18px 8px}.brand{margin:0 4px 30px}.brand-name,.nav-caption,.nav a:not(.active){font-size:0}.brand-mark{flex:none}.nav a{justify-content:center;padding:10px 0}.nav-icon{font-size:17px}.nav a.active{font-size:0}.side-note{display:none}.main{margin-left:64px}.dashboard-grid{grid-template-columns:1fr 1fr}.metrics{grid-template-columns:repeat(2,1fr)}.schema-grid{grid-template-columns:1fr}}
@media(max-width:580px){.sidebar{width:52px;padding:14px 6px}.brand{margin:0 3px 27px}.brand-mark{width:34px;height:34px}.main{margin-left:52px}.topbar{height:54px;padding:0 13px}.top-right{display:none}.content{padding:20px 12px}.title-row{align-items:flex-start;flex-direction:column;gap:13px}.title-row>.button{align-self:stretch}h1{font-size:22px}.dashboard-grid{grid-template-columns:1fr}.metrics{gap:8px}.metric{padding:12px;min-height:100px}.metric-value{font-size:22px}.stat-strip{gap:7px}.mini{padding:10px}.mini span{font-size:8px}.mini b{font-size:16px}.toolbar{flex-wrap:wrap}.search{min-width:100%;max-width:none}.segment{margin-right:auto}.form-grid{grid-template-columns:1fr}.field.full{grid-column:auto}.footer{flex-direction:column}.schema-grid{grid-template-columns:1fr}}
@media print{.sidebar,.topbar,.title-row,.footer,.button,.nav{display:none!important}.main{margin:0}.content{padding:0}.ticket{max-width:none;border:1px solid #999}}
"""

def db_connect():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    if DATABASE.exists():
        with sqlite3.connect(DATABASE) as existing:
            ready = existing.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='students'").fetchone()
        if ready:
            return
    with db_connect() as conn:
        conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))

def rows(query, params=()):
    with db_connect() as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]

def scalar(query, params=()):
    with db_connect() as conn:
        row = conn.execute(query, params).fetchone()
        return row[0] if row else 0

def e(value):
    return html.escape("" if value is None else str(value), quote=True)

def make_page(title, section, content, message=""):
    links = [
        ("/", "⌂", "Overview", "overview"),
        ("/schedule", "▦", "Exam schedule", "schedule"),
        ("/students", "♙", "Students", "students"),
        ("/results", "▤", "Results & marks", "results"),
        ("/database", "▥", "SQL database", "database"),
    ]
    nav = "".join(
        '<a class="' + ("active" if section == key else "") + '" href="' + href + '"><span class="nav-icon">' + icon + "</span>" + label + "</a>"
        for href, icon, label, key in links
    )
    notice = '<div class="message">' + e(message) + "</div>" if message else ""
    today = date.today().strftime("%a, %d %b %Y")
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Examwise · """ + e(title) + """</title><style>""" + STYLE + """</style></head>
<body><div class="shell"><aside class="sidebar">
<a class="brand" href="/"><span class="brand-mark">E.</span><span class="brand-name">examwise<small>ACADEMIC SYSTEMS</small></span></a>
<div class="nav-caption">WORKSPACE</div><nav class="nav">""" + nav + """</nav>
<div class="side-note"><b>Autumn semester · 2026</b>Examination office<br>Python + SQLite edition</div>
</aside><main class="main"><header class="topbar"><span>Academic operations &nbsp; / &nbsp; <strong>""" + e(title) + """</strong></span><span class="top-right">""" + e(today) + """ &nbsp; · &nbsp; Admin user</span></header>
<div class="content">""" + notice + content + """
<footer class="footer"><span>Examwise · Examination Management System</span><span>Python server · SQLite database</span></footer>
</div></main></div></body></html>"""

def title_block(kicker, title, subtitle, action=""):
    return '<div class="title-row"><div><div class="eyebrow">' + e(kicker) + '</div><h1>' + e(title) + "</h1><p>" + e(subtitle) + "</p></div>" + action + "</div>"

def metric(label, value, foot, icon):
    return '<article class="metric"><div class="metric-label">' + e(label) + '<span class="metric-icon">' + icon + '</span></div><div class="metric-value">' + e(value) + '</div><div class="metric-foot">' + e(foot) + "</div></article>"

def session_status(exam_date):
    return "upcoming" if exam_date >= date.today().isoformat() else "completed"

def overview_page(message=""):
    upcoming = rows("""SELECT x.session_id,x.exam_date,x.start_time,x.end_time,c.course_name,c.course_code,r.room_name,
      (SELECT COUNT(*) FROM registrations reg WHERE reg.session_id=x.session_id) AS candidates
      FROM exam_sessions x JOIN courses c ON c.course_id=x.course_id JOIN rooms r ON r.room_id=x.room_id
      WHERE x.exam_date>=? ORDER BY x.exam_date,x.start_time LIMIT 4""", (date.today().isoformat(),))
    student_count = scalar("SELECT COUNT(*) FROM students")
    exam_count = scalar("SELECT COUNT(*) FROM exam_sessions WHERE exam_date>=?", (date.today().isoformat(),))
    marks_count = scalar("SELECT COUNT(*) FROM marks")
    pass_count = scalar("SELECT COUNT(*) FROM results WHERE outcome='PASS'")
    result_count = scalar("SELECT COUNT(*) FROM results")
    pass_rate = round(100 * pass_count / result_count) if result_count else 0
    metrics = '<div class="grid metrics">' + metric("Upcoming exams", exam_count, "Scheduled sessions ahead", "▦") + metric("Registered students", student_count, "Across active programs", "♙") + metric("Marks recorded", marks_count, "Result records saved", "✎") + metric("Overall pass rate", str(pass_rate) + "%" if result_count else "—", str(result_count) + " assessed results", "↗") + "</div>"
    schedule_rows = []
    for item in upcoming:
        d = datetime.strptime(item["exam_date"], "%Y-%m-%d")
        schedule_rows.append(
            '<div class="exam-row"><span class="date-box"><b>' + d.strftime("%d") + '</b><small>' + d.strftime("%b") + '</small></span>'
            + '<span class="exam-main"><b>' + e(item["course_name"]) + '</b><small>' + e(item["course_code"]) + ' · ' + e(item["start_time"]) + '–' + e(item["end_time"]) + ' · ' + str(item["candidates"]) + ' candidates</small></span>'
            + '<span class="room-name">' + e(item["room_name"]) + '</span></div>'
        )
    if not schedule_rows:
        schedule_rows.append('<div class="empty">No upcoming examinations. Create a session to get started.</div>')
    grades = rows("SELECT grade,COUNT(*) AS n FROM results GROUP BY grade")
    grade_counts = {r["grade"]: r["n"] for r in grades}
    top = max([1] + list(grade_counts.values()))
    bar_items = []
    for grade in ("A+", "A", "B", "C", "D", "F"):
        height = max(5, int(grade_counts.get(grade, 0) * 100 / top))
        bar_items.append('<div><i style="height:' + str(height) + '%"></i><small>' + grade + "</small></div>")
    performance = '<article class="card"><div class="card-head"><div><h2>Result snapshot</h2><p>Published and recorded marks</p></div><span class="pill green">LIVE DATA</span></div><div class="pass-value"><b>' + (str(pass_rate) + "%" if result_count else "—") + '</b><span>overall pass rate</span></div><div class="bar"><span style="width:' + str(pass_rate) + '%"></span></div><div class="grade-bars">' + "".join(bar_items) + '</div><div class="legend"><span><i></i>Pass</span><span><i style="background:#f0a163"></i>Needs review</span></div></article>'
    actions = '<article class="card"><div class="card-head"><div><h2>Quick actions</h2><p>Continue your workflow</p></div></div><div class="upcoming"><div class="exam-row"><span class="course-badge">＋</span><span class="exam-main"><b>Add a student</b><small>Create a student profile</small></span><a class="row-link" href="/new-student">OPEN →</a></div><div class="exam-row"><span class="course-badge">✎</span><span class="exam-main"><b>Enter marks</b><small>Record exam performance</small></span><a class="row-link" href="/record-marks">OPEN →</a></div><div class="exam-row"><span class="course-badge">▥</span><span class="exam-main"><b>Explore database</b><small>Inspect tables and SQL</small></span><a class="row-link" href="/database">OPEN →</a></div></div></article>'
    schedule_card = '<article class="card"><div class="card-head"><div><h2>Upcoming examinations</h2><p>Your next scheduled sessions</p></div><a class="text-link" href="/schedule">View schedule ↗</a></div><div class="upcoming">' + "".join(schedule_rows) + "</div></article>"
    content = title_block("EXAMINATION OFFICE", "Good morning, Admin", "Here’s what’s happening across your examination desk.", '<a class="button primary" href="/new-exam">＋ Create exam</a>') + metrics + '<div class="grid dashboard-grid">' + schedule_card + performance + actions + "</div>"
    return make_page("Overview", "overview", content, message)

def option_list(items, value_key, label_fn, selected=None):
    out = []
    for item in items:
        value = str(item[value_key])
        mark = " selected" if str(selected) == value else ""
        out.append('<option value="' + e(value) + '"' + mark + ">" + e(label_fn(item)) + "</option>")
    return "".join(out)

def form_field(label, control, full=False, help_text=""):
    return '<div class="field' + (" full" if full else "") + '"><label>' + e(label) + "</label>" + control + ('<span class="help">' + e(help_text) + "</span>" if help_text else "") + "</div>"

def schedule_page(message="", q="", status="all"):
    sessions = rows("""SELECT x.*,c.course_code,c.course_name,c.credits,r.room_name,r.building,r.capacity,i.full_name AS invigilator_name,
      (SELECT COUNT(*) FROM registrations z WHERE z.session_id=x.session_id) AS candidates
      FROM exam_sessions x JOIN courses c ON c.course_id=x.course_id JOIN rooms r ON r.room_id=x.room_id
      JOIN invigilators i ON i.invigilator_id=x.invigilator_id ORDER BY x.exam_date,x.start_time""")
    shown = []
    needle = q.lower().strip()
    for s in sessions:
        actual = session_status(s["exam_date"])
        values = " ".join([s["course_name"],s["course_code"],s["room_name"],s["invigilator_name"]]).lower()
        if status not in ("all", actual) or (needle and needle not in values):
            continue
        shown.append(s)
    body = []
    for s in shown:
        label = '<span class="pill">' + ("UPCOMING" if session_status(s["exam_date"]) == "upcoming" else "COMPLETED") + "</span>"
        body.append(
            '<tr><td><span class="course-badge">' + e(s["course_code"][-2:]) + '</span><span class="main-cell"><b>' + e(s["course_name"]) + '</b><small>' + e(s["course_code"]) + ' · ' + str(s["credits"]) + ' credits</small></span></td>'
            + '<td><span class="main-cell"><b>' + e(datetime.strptime(s["exam_date"], "%Y-%m-%d").strftime("%d %b %Y")) + '</b><small>' + e(s["start_time"]) + ' – ' + e(s["end_time"]) + '</small></span></td>'
            + '<td><span class="main-cell"><b>' + e(s["room_name"]) + '</b><small>' + e(s["building"]) + ' · ' + str(s["capacity"]) + ' seats</small></span></td>'
            + '<td>' + e(s["invigilator_name"]) + '</td><td>' + str(s["candidates"]) + ' / ' + str(s["capacity"]) + '</td><td>' + label + '</td>'
            + '<td><a class="row-link" href="/hall-ticket?session_id=' + str(s["session_id"]) + '">Tickets</a></td></tr>'
        )
    if not body:
        body.append('<tr><td colspan="7"><div class="empty">No sessions match this schedule.</div></td></tr>')
    search = '<form class="toolbar" method="get" action="/schedule"><label class="search"><span>⌕</span><input name="q" value="' + e(q) + '" placeholder="Search course, room or invigilator"></label><div class="segment"><a class="' + ("sel" if status=="all" else "") + '" href="/schedule">All</a><a class="' + ("sel" if status=="upcoming" else "") + '" href="/schedule?status=upcoming">Upcoming</a><a class="' + ("sel" if status=="completed" else "") + '" href="/schedule?status=completed">Completed</a></div><button class="button light small-button">Search</button></form>'
    table = '<div class="card table-card"><div class="table-head"><div><h2>Examination sessions</h2><p>' + str(len(shown)) + ' scheduled sessions</p></div><span class="pill">' + str(len(shown)) + ' SESSIONS</span></div><div class="table-scroll"><table><thead><tr><th>COURSE / SESSION</th><th>DATE &amp; TIME</th><th>ROOM</th><th>INVIGILATOR</th><th>REGISTERED</th><th>STATUS</th><th></th></tr></thead><tbody>' + ''.join(body) + '</tbody></table></div></div>'
    content = title_block("ACADEMIC OPERATIONS", "Exam schedule", "Plan sessions, allocate rooms and prevent timetable conflicts.", '<a class="button primary" href="/new-exam">＋ Add examination</a>') + search + table
    return make_page("Exam schedule", "schedule", content, message)

def new_exam_page(error="", values=None):
    values = values or {}
    courses = rows("SELECT course_id,course_code,course_name FROM courses ORDER BY course_code")
    rooms = rows("SELECT room_id,room_name,capacity FROM rooms ORDER BY room_name")
    invigs = rows("SELECT invigilator_id,full_name,department FROM invigilators ORDER BY full_name")
    course_opts = option_list(courses,"course_id",lambda c:c["course_code"]+" · "+c["course_name"],values.get("course_id"))
    room_opts = option_list(rooms,"room_id",lambda r:r["room_name"]+" · "+str(r["capacity"])+" seats",values.get("room_id"))
    invig_opts = option_list(invigs,"invigilator_id",lambda i:i["full_name"]+" · "+i["department"],values.get("invigilator_id"))
    fields = form_field("Course *",'<select name="course_id" required>'+course_opts+'</select>',True)
    fields += form_field("Exam date *",'<input type="date" name="exam_date" min="'+date.today().isoformat()+'" value="'+e(values.get("exam_date",date.today().isoformat()))+'" required>')
    fields += form_field("Room *",'<select name="room_id" required>'+room_opts+'</select>')
    fields += form_field("Start time *",'<input type="time" name="start_time" value="'+e(values.get("start_time","09:30"))+'" required>')
    fields += form_field("End time *",'<input type="time" name="end_time" value="'+e(values.get("end_time","12:30"))+'" required>')
    fields += form_field("Invigilator *",'<select name="invigilator_id" required>'+invig_opts+'</select>')
    fields += form_field("Registration",'<input type="text" value="All eligible students are registered automatically" readonly>',True,"Room capacity and schedule conflicts are checked before saving.")
    content = title_block("ACADEMIC OPERATIONS", "Create examination", "Choose a course, time, room and invigilator.") + '<div class="card form-card">' + ('<div class="message error">'+e(error)+'</div>' if error else "") + '<form method="post" action="/create-exam"><div class="form-grid">'+fields+'</div><div class="form-actions"><a class="button light" href="/schedule">Cancel</a><button class="button primary">Save examination</button></div></form></div>'
    return make_page("Create examination", "schedule", content)

def create_exam(values):
    course_id=int(values.get("course_id","0")); room_id=int(values.get("room_id","0")); invigilator_id=int(values.get("invigilator_id","0"))
    exam_date=values.get("exam_date",""); start=values.get("start_time",""); end=values.get("end_time","")
    if exam_date < date.today().isoformat():
        return "Choose today or a future exam date."
    if not start or not end or start >= end:
        return "The end time must be later than the start time."
    course = rows("SELECT program_id FROM courses WHERE course_id=?", (course_id,))
    room = rows("SELECT capacity FROM rooms WHERE room_id=?", (room_id,))
    invig = rows("SELECT invigilator_id FROM invigilators WHERE invigilator_id=?", (invigilator_id,))
    if not course or not room or not invig:
        return "Choose a valid course, room and invigilator."
    candidates = rows("SELECT student_id FROM students WHERE program_id=?", (course[0]["program_id"],))
    if len(candidates) > room[0]["capacity"]:
        return "Room capacity is " + str(room[0]["capacity"]) + ", but " + str(len(candidates)) + " eligible students are registered."
    conflicts = rows("""SELECT session_id,room_id,invigilator_id,start_time,end_time FROM exam_sessions
        WHERE exam_date=? AND (room_id=? OR invigilator_id=?)
        AND start_time < ? AND end_time > ?""", (exam_date,room_id,invigilator_id,end,start))
    if conflicts:
        conflict=conflicts[0]
        resources=[]
        if int(conflict["room_id"])==room_id: resources.append("room")
        if int(conflict["invigilator_id"])==invigilator_id: resources.append("invigilator")
        return "Time conflict: the selected " + " and ".join(resources) + " is already allocated from " + conflict["start_time"] + " to " + conflict["end_time"] + "."
    try:
        with db_connect() as conn:
            with conn:
                cur=conn.execute("INSERT INTO exam_sessions(course_id,exam_date,start_time,end_time,room_id,invigilator_id) VALUES(?,?,?,?,?,?)",(course_id,exam_date,start,end,room_id,invigilator_id))
                session_id=cur.lastrowid
                conn.executemany("INSERT INTO registrations(student_id,session_id,registration_date,status) VALUES(?,?,?,'registered')",[(s["student_id"],session_id,date.today().isoformat()) for s in candidates])
    except sqlite3.IntegrityError as error:
        return str(error)
    return ""

def students_page(message="", search=""):
    all_students=rows("""SELECT s.student_id,s.roll_number,s.full_name AS name,s.email,s.program_id,s.semester,p.program_name,
        (SELECT COUNT(*) FROM registrations r WHERE r.student_id=s.student_id) AS exam_count,
        (SELECT COUNT(*) FROM registrations r JOIN marks m ON m.registration_id=r.registration_id WHERE r.student_id=s.student_id) AS graded_count
        FROM students s JOIN programs p ON p.program_id=s.program_id ORDER BY s.roll_number""")
    q=search.lower().strip()
    shown=[s for s in all_students if not q or q in " ".join(str(s[k]) for k in ("name","roll_number","email","program_name")).lower()]
    body=[]
    for s in shown:
        body.append('<tr><td><span class="person-badge">'+e("".join(x[0] for x in s["name"].split()[:2]).upper())+'</span><span class="main-cell"><b>'+e(s["name"])+'</b><small>'+e(s["email"])+'</small></span></td><td><b>'+e(s["roll_number"])+'</b></td><td>'+e(s["program_name"])+'</td><td>Semester '+str(s["semester"])+'</td><td>'+str(s["exam_count"])+' exams</td><td>'+str(s["graded_count"])+' / '+str(s["exam_count"])+' graded</td><td><a class="row-link" href="/hall-ticket?student_id='+str(s["student_id"])+'">Ticket ↗</a></td></tr>')
    if not body: body.append('<tr><td colspan="7"><div class="empty">No students match this search.</div></td></tr>')
    total_reg=scalar("SELECT COUNT(*) FROM registrations")
    avg=round(total_reg/len(all_students)) if all_students else 0
    stats='<div class="stat-strip"><div class="mini"><span>Total students</span><b>'+str(len(all_students))+'</b></div><div class="mini"><span>Exam registrations</span><b>'+str(total_reg)+'</b></div><div class="mini"><span>Average exams / student</span><b>'+str(avg)+'</b></div></div>'
    search_form='<form class="toolbar" method="get" action="/students"><label class="search"><span>⌕</span><input name="q" value="'+e(search)+'" placeholder="Search name, roll number or program"></label><button class="button light small-button">Search</button></form>'
    table='<div class="card table-card"><div class="table-scroll"><table><thead><tr><th>STUDENT</th><th>ROLL NUMBER</th><th>PROGRAM</th><th>SEMESTER</th><th>REGISTERED EXAMS</th><th>RESULTS</th><th></th></tr></thead><tbody>'+''.join(body)+'</tbody></table></div></div>'
    content=title_block("ACADEMIC RECORDS","Students","Manage student profiles and examination registrations.",'<a class="button primary" href="/new-student">＋ Add student</a>')+stats+search_form+table
    return make_page("Students","students",content,message)

def new_student_page(error="",values=None):
    values=values or {}
    programs=rows("SELECT program_id,program_name FROM programs ORDER BY program_name")
    opts=option_list(programs,"program_id",lambda p:p["program_name"],values.get("program_id"))
    semesters=''.join('<option value="'+str(i)+'"'+(' selected' if str(values.get("semester","5"))==str(i) else "")+'>'+str(i)+'</option>' for i in range(1,13))
    fields=form_field("Full name *",'<input name="name" value="'+e(values.get("name",""))+'" placeholder="e.g. Riya Sharma" maxlength="120" required>',True)
    fields+=form_field("Roll number *",'<input name="roll_number" value="'+e(values.get("roll_number",""))+'" placeholder="e.g. CS2026-006" maxlength="20" required>')
    fields+=form_field("Email address *",'<input type="email" name="email" value="'+e(values.get("email",""))+'" placeholder="student@campus.edu" maxlength="160" required>')
    fields+=form_field("Program *",'<select name="program_id" required>'+opts+'</select>')
    fields+=form_field("Semester *",'<select name="semester">'+semesters+'</select>')
    fields+=form_field("Exam registration",'<input type="text" value="Upcoming program exams are added automatically" readonly>',True)
    content=title_block("ACADEMIC RECORDS","Add student","Create a student profile and register for upcoming program exams.")+'<div class="card form-card">'+('<div class="message error">'+e(error)+'</div>' if error else "")+'<form method="post" action="/create-student"><div class="form-grid">'+fields+'</div><div class="form-actions"><a class="button light" href="/students">Cancel</a><button class="button primary">Add student</button></div></form></div>'
    return make_page("Add student","students",content)

def create_student(values):
    name=values.get("name","").strip(); roll=values.get("roll_number","").strip(); email=values.get("email","").strip().lower()
    if not name or not roll or not email: return "Name, roll number and email are required."
    try:
        with db_connect() as conn:
            with conn:
                cur=conn.execute("INSERT INTO students(roll_number,full_name,email,program_id,semester) VALUES(?,?,?,?,?)",(roll,name,email,int(values.get("program_id","0")),int(values.get("semester","5"))))
                student_id=cur.lastrowid
                upcoming=conn.execute("""SELECT x.session_id FROM exam_sessions x JOIN courses c ON c.course_id=x.course_id
                    WHERE x.exam_date>=? AND c.program_id=? ORDER BY x.exam_date""",(date.today().isoformat(),int(values.get("program_id","0")))).fetchall()
                conn.executemany("INSERT INTO registrations(student_id,session_id,registration_date,status) VALUES(?,?,?,'registered')",[(student_id,r["session_id"],date.today().isoformat()) for r in upcoming])
    except sqlite3.IntegrityError as error:
        text=str(error)
        if "roll_number" in text: return "That roll number is already in use."
        if "email" in text: return "A student with that email already exists."
        return text
    return ""

def result_page(message="",session_filter="all",search=""):
    all_sessions=rows("SELECT x.session_id,x.exam_date,c.course_code,c.course_name FROM exam_sessions x JOIN courses c ON c.course_id=x.course_id ORDER BY x.exam_date")
    result_rows=rows("""SELECT r.registration_id,r.roll_number,r.student_name,r.course_code,r.course_name,
       r.internal_marks,r.external_marks,r.total_marks,r.grade,r.outcome,
       CASE WHEN pub.session_id IS NULL THEN 0 ELSE 1 END AS published
       FROM results r JOIN registrations reg ON reg.registration_id=r.registration_id
       LEFT JOIN session_publications pub ON pub.session_id=reg.session_id
       ORDER BY r.course_code,r.roll_number""")
    query=search.lower().strip()
    shown=[r for r in result_rows if (session_filter=="all" or str(r["course_code"]+" · "+r["course_name"])==session_filter) and (not query or query in (r["student_name"]+" "+r["roll_number"]+" "+r["course_name"]+" "+r["course_code"]).lower())]
    passed=sum(1 for r in result_rows if r["outcome"]=="PASS")
    pass_rate=round(100*passed/len(result_rows)) if result_rows else 0
    average=round(sum(r["total_marks"] for r in result_rows)/len(result_rows)) if result_rows else 0
    missing=scalar("SELECT COUNT(*) FROM registrations r LEFT JOIN marks m ON m.registration_id=r.registration_id WHERE m.mark_id IS NULL")
    stats='<div class="stat-strip"><div class="mini"><span>Assessed results</span><b>'+str(len(result_rows))+'</b></div><div class="mini"><span>Pass percentage</span><b>'+(str(pass_rate)+"%" if result_rows else "—")+'</b></div><div class="mini"><span>Average score</span><b>'+(str(average)+"/100" if result_rows else "—")+'</b></div></div>'
    select='<option value="all">All examination sessions</option>'
    for s in all_sessions:
        label=s["course_code"]+" · "+s["course_name"]
        select+='<option value="'+e(label)+'"'+(" selected" if session_filter==label else "")+'>'+e(label+" · "+datetime.strptime(s["exam_date"],"%Y-%m-%d").strftime("%d %b"))+'</option>'
    filters='<form class="toolbar" method="get" action="/results"><label class="search"><span>⌕</span><input name="q" value="'+e(search)+'" placeholder="Search student or course"></label><select class="select" name="session">'+select+'</select><button class="button light small-button">Filter</button><span class="grow"></span><button class="button primary small-button" formaction="/publish-results" formmethod="post">Publish results</button></form>'
    body=[]
    for r in shown:
        status='<span class="pill green">PUBLISHED</span>' if r["published"] else '<span class="pill orange">DRAFT</span>'
        action=('<a class="row-link" href="/revaluation?registration_id='+str(r["registration_id"])+'">↻ Request</a>' if not scalar("SELECT COUNT(*) FROM revaluation_requests WHERE registration_id=?",(r["registration_id"],)) else '<span class="muted">Requested</span>')
        body.append('<tr><td><span class="person-badge">'+e("".join(x[0] for x in r["student_name"].split()[:2]).upper())+'</span><span class="main-cell"><b>'+e(r["student_name"])+'</b><small>'+e(r["roll_number"])+'</small></span></td><td><span class="main-cell"><b>'+e(r["course_code"])+'</b><small>'+e(r["course_name"])+'</small></span></td><td>'+e(r["internal_marks"])+' / 20</td><td>'+e(r["external_marks"])+' / 80</td><td><b>'+e(r["total_marks"])+'</b> / 100</td><td><span class="pill '+("green" if r["outcome"]=="PASS" else "red")+'">'+e(r["grade"])+'</span></td><td>'+status+'<br>'+action+'</td></tr>')
    if not body: body.append('<tr><td colspan="7"><div class="empty">No results match this selection. Record marks for a registered student.</div></td></tr>')
    table='<div class="card table-card"><div class="table-head"><div><h2>Student result ledger</h2><p>Grades are derived from the configured mark ranges</p></div><span class="pill">GRADE RULES ACTIVE</span></div><div class="table-scroll"><table><thead><tr><th>STUDENT</th><th>COURSE</th><th>INTERNAL</th><th>EXTERNAL</th><th>TOTAL</th><th>GRADE</th><th>RESULT</th></tr></thead><tbody>'+''.join(body)+'</tbody></table></div></div>'
    note='<div class="message" style="margin-top:13px">Grading policy: A+ ≥ 90 · A ≥ 80 · B ≥ 70 · C ≥ 60 · D ≥ 40 · F &lt; 40. A pass requires at least 40 marks out of 100. '+str(missing)+' registrations are awaiting marks.</div>'
    content=title_block("ASSESSMENT CENTRE","Results & marks","Record marks, review grades and publish student results.",'<a class="button primary" href="/record-marks">＋ Record marks</a>')+stats+filters+table+note
    return make_page("Results & marks","results",content,message)

def record_marks_page(error=""):
    registrations=rows("""SELECT r.registration_id,s.full_name,s.roll_number,c.course_code,c.course_name,x.exam_date
       FROM registrations r JOIN students s ON s.student_id=r.student_id
       JOIN exam_sessions x ON x.session_id=r.session_id JOIN courses c ON c.course_id=x.course_id
       LEFT JOIN marks m ON m.registration_id=r.registration_id WHERE m.mark_id IS NULL
       ORDER BY x.exam_date,s.roll_number""")
    options=option_list(registrations,"registration_id",lambda r:r["full_name"]+" · "+r["roll_number"]+" · "+r["course_code"]+" · "+datetime.strptime(r["exam_date"],"%Y-%m-%d").strftime("%d %b %Y"))
    fields=form_field("Registered student and exam *",'<select name="registration_id" required>'+options+'</select>',True,"Only registrations without a saved mark are listed.")
    fields+=form_field("Internal marks *",'<input name="internal_marks" type="number" min="0" max="20" step="0.5" value="16" required>')
    fields+=form_field("External marks *",'<input name="external_marks" type="number" min="0" max="80" step="0.5" value="60" required>')
    fields+=form_field("Assessment breakdown",'<input value="Internal: 20 marks · External: 80 marks" readonly>',True)
    error_text=('<div class="message error">'+e(error)+'</div>' if error else "")
    empty=('<div class="message">All registered students already have marks. You can publish results from the Results page.</div>' if not registrations else "")
    content=title_block("ASSESSMENT CENTRE","Record marks","Enter internal and external marks for a registered student.")+'<div class="card form-card">'+error_text+empty+'<form method="post" action="/save-marks"><div class="form-grid">'+fields+'</div><div class="form-actions"><a class="button light" href="/results">Cancel</a><button class="button primary"'+(" disabled" if not registrations else "")+'>Save marks</button></div></form></div>'
    return make_page("Record marks","results",content)

def save_marks(values):
    try:
        registration_id=int(values.get("registration_id","0"))
        internal=float(values.get("internal_marks","-1")); external=float(values.get("external_marks","-1"))
    except ValueError:
        return "Enter valid numeric marks."
    if not 0 <= internal <= 20: return "Internal marks must be between 0 and 20."
    if not 0 <= external <= 80: return "External marks must be between 0 and 80."
    try:
        with db_connect() as conn:
            with conn:
                conn.execute("INSERT INTO marks(registration_id,internal_marks,external_marks,entered_at) VALUES(?,?,?,?)",(registration_id,internal,external,datetime.now().isoformat(timespec="seconds")))
    except sqlite3.IntegrityError as error:
        return str(error)
    return ""

def revaluation_page(registration_id, error=""):
    record=rows("""SELECT r.registration_id,s.full_name,s.roll_number,c.course_code,c.course_name,m.internal_marks,m.external_marks,m.internal_marks+m.external_marks AS total
      FROM registrations r JOIN students s ON s.student_id=r.student_id JOIN exam_sessions x ON x.session_id=r.session_id
      JOIN courses c ON c.course_id=x.course_id JOIN marks m ON m.registration_id=r.registration_id WHERE r.registration_id=?""",(registration_id,))
    if not record:
        return make_page("Revaluation","results",title_block("ASSESSMENT CENTRE","Revaluation request","No result was found for this registration."))
    r=record[0]
    fields=form_field("Result",'<input value="'+e(r["full_name"]+" · "+r["roll_number"]+" · "+r["course_code"])+'" readonly>',True)
    fields+=form_field("Current marks",'<input value="'+e(r["total"])+' / 100" readonly>',True)
    fields+=form_field("Reason for revaluation *",'<textarea name="reason" maxlength="500" required placeholder="Describe which part of the result should be reviewed"></textarea>',True)
    content=title_block("ASSESSMENT CENTRE","Request revaluation","Submit a review request for this recorded result.")+'<div class="card form-card">'+('<div class="message error">'+e(error)+'</div>' if error else "")+'<form method="post" action="/create-revaluation"><input type="hidden" name="registration_id" value="'+str(registration_id)+'"><div class="form-grid">'+fields+'</div><div class="form-actions"><a class="button light" href="/results">Cancel</a><button class="button primary">Submit request</button></div></form></div>'
    return make_page("Revaluation request","results",content)

def hall_ticket_page(query):
    student_id=query.get("student_id",[""])[0]
    session_id=query.get("session_id",[""])[0]
    if student_id:
        records=rows("""SELECT s.student_id,s.full_name,s.roll_number,s.email,x.session_id,x.exam_date,x.start_time,x.end_time,
          c.course_code,c.course_name,room.room_name,room.building,i.full_name AS invigilator
          FROM registrations reg JOIN students s ON s.student_id=reg.student_id JOIN exam_sessions x ON x.session_id=reg.session_id
          JOIN courses c ON c.course_id=x.course_id JOIN rooms room ON room.room_id=x.room_id JOIN invigilators i ON i.invigilator_id=x.invigilator_id
          WHERE s.student_id=? AND x.exam_date>=? ORDER BY x.exam_date LIMIT 1""",(student_id,date.today().isoformat()))
    elif session_id:
        records=rows("""SELECT s.student_id,s.full_name,s.roll_number,s.email,x.session_id,x.exam_date,x.start_time,x.end_time,
          c.course_code,c.course_name,room.room_name,room.building,i.full_name AS invigilator
          FROM registrations reg JOIN students s ON s.student_id=reg.student_id JOIN exam_sessions x ON x.session_id=reg.session_id
          JOIN courses c ON c.course_id=x.course_id JOIN rooms room ON room.room_id=x.room_id JOIN invigilators i ON i.invigilator_id=x.invigilator_id
          WHERE x.session_id=? ORDER BY s.roll_number""",(session_id,))
    else:
        records=[]
    if not records:
        content=title_block("EXAMINATION OFFICE","Hall ticket","No upcoming registered exam was found for this selection.")+'<a class="button light" href="/schedule">Back to schedule</a>'
        return make_page("Hall ticket","schedule",content)
    r=records[0]
    details='<div class="ticket"><h2>EXAMINATION HALL TICKET</h2>'
    details+='<div class="ticket-row"><span>Student</span><b>'+e(r["full_name"])+' · '+e(r["roll_number"])+'</b></div>'
    details+='<div class="ticket-row"><span>Examination</span><b>'+e(r["course_name"])+' ('+e(r["course_code"])+')</b></div>'
    details+='<div class="ticket-row"><span>Date &amp; time</span><b>'+e(datetime.strptime(r["exam_date"],"%Y-%m-%d").strftime("%d %b %Y"))+' · '+e(r["start_time"])+'–'+e(r["end_time"])+'</b></div>'
    details+='<div class="ticket-row"><span>Venue</span><b>'+e(r["room_name"])+' · '+e(r["building"])+'</b></div>'
    details+='<div class="ticket-row"><span>Invigilator</span><b>'+e(r["invigilator"])+'</b></div></div>'
    if session_id:
        details+='<div class="card table-card" style="margin-top:15px"><div class="table-head"><h2>Registered candidates</h2><span class="pill">'+str(len(records))+' CANDIDATES</span></div><div class="table-scroll"><table><thead><tr><th>ROLL NUMBER</th><th>STUDENT</th><th>EMAIL</th></tr></thead><tbody>'+''.join('<tr><td>'+e(x["roll_number"])+'</td><td>'+e(x["full_name"])+'</td><td>'+e(x["email"])+'</td></tr>' for x in records)+'</tbody></table></div></div>'
    content=title_block("EXAMINATION OFFICE","Hall ticket","Candidate and session details for the selected exam. Use Ctrl+P to print.")+details
    return make_page("Hall ticket","schedule",content)

TABLES = {
    "programs": ("programs","program_id"),
    "courses": ("courses","course_id"),
    "students": ("students","student_id"),
    "rooms": ("rooms","room_id"),
    "invigilators": ("invigilators","invigilator_id"),
    "exam_sessions": ("exam_sessions","session_id"),
    "registrations": ("registrations","registration_id"),
    "session_publications": ("session_publications","session_id"),
    "marks": ("marks","mark_id"),
    "grade_rules": ("grade_rules","grade_rule_id"),
    "revaluation_requests": ("revaluation_requests","request_id"),
    "results": ("results","registration_id"),
}

def database_page(selected="students",message=""):
    if selected not in TABLES: selected="students"
    tabs=''.join('<a class="'+("sel" if selected==name else "")+'" href="/database?table='+name+'">'+name+'</a>' for name in TABLES)
    table,sortkey=TABLES[selected]
    with db_connect() as conn:
        columns=[r["name"] for r in conn.execute("PRAGMA table_info("+table+")").fetchall()]
        data=[dict(r) for r in conn.execute("SELECT * FROM "+table+" LIMIT 50").fetchall()]
    if not columns and data: columns=list(data[0])
    header='<tr>'+''.join('<th>'+e(c.replace("_"," ").upper())+'</th>' for c in columns)+'</tr>'
    body=''.join('<tr>'+''.join('<td>'+e(row.get(c,""))+'</td>' for c in columns)+'</tr>' for row in data)
    if not body: body='<tr><td colspan="'+str(max(1,len(columns)))+'"><div class="empty">This table is empty.</div></td></tr>'
    data_card='<div class="card table-card"><div class="table-head"><div><h2>Live table data · '+e(selected)+'</h2><p>'+str(len(data))+' rows currently stored</p></div><span class="pill green">SQLITE</span></div><div class="table-scroll"><table><thead>'+header+'</thead><tbody>'+body+'</tbody></table></div></div>'
    schema=e(SCHEMA_FILE.read_text(encoding="utf-8"))
    sql_card='<div class="card"><div class="card-head"><div><h2>SQL schema and sample data</h2><p>DDL, integrity triggers and starter records from schema.sql</p></div><a class="text-link" href="/schema.sql">Open SQL file ↗</a></div><div class="codebox"><div class="code-top">schema.sql · SQLite</div><pre>'+schema+'</pre></div></div>'
    query_card="""<div class="card"><div class="eyebrow">SAMPLE QUERY</div><h2>Pass percentage by course</h2><pre class="sql-query">SELECT course_code,
       ROUND(100.0 * SUM(CASE WHEN outcome = &#39;PASS&#39; THEN 1 ELSE 0 END) / COUNT(*), 1) AS pass_pct
FROM results
GROUP BY course_code;</pre><p>The results view joins marks to registered students, sessions and courses.</p></div>"""
    content=title_block("DATA MANAGEMENT","SQL database","Inspect the actual SQLite rows and relational design.")+'<div class="schema-grid"><div class="schema-content"><div class="card"><div class="card-head"><div><h2>Live database tables</h2><p>Select a table to inspect its stored rows</p></div></div><div class="schema-tabs">'+tabs+'</div>'+data_card+'</div>'+sql_card+'</div><aside class="schema-content"><div class="card"><div class="eyebrow">DATABASE OVERVIEW</div><h2>Relational model</h2><div class="db-facts"><div class="fact"><span>Tables + view</span><b>11 + 1</b></div><div class="fact"><span>SQLite rows</span><b>'+str(sum(scalar("SELECT COUNT(*) FROM "+item[0]) for item in TABLES.values() if item[0]!="results")+scalar("SELECT COUNT(*) FROM results"))+'</b></div><div class="fact"><span>Integrity</span><b>PK · FK · CHECK · UNIQUE</b></div><div class="fact"><span>Result grade</span><b>Calculated from ranges</b></div></div><a class="button light" href="/schema.sql" download>Download SQL schema</a></div>'+query_card+'</aside></div>'
    return make_page("SQL database","database",content,message)

def publish_results():
    with db_connect() as conn:
        with conn:
            conn.execute("""INSERT OR IGNORE INTO session_publications(session_id)
                SELECT DISTINCT r.session_id FROM registrations r JOIN marks m ON m.registration_id=r.registration_id""")
    return ""

def create_revaluation(values):
    try:
        with db_connect() as conn:
            with conn:
                conn.execute("INSERT INTO revaluation_requests(registration_id,request_date,reason,status) VALUES(?,?,?,'pending')",(int(values.get("registration_id","0")),date.today().isoformat(),values.get("reason","").strip()))
    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed" in str(error): return "A revaluation request already exists for this result."
        return str(error)
    return ""

def query_values(body):
    parsed=parse_qs(body.decode("utf-8"),keep_blank_values=True)
    return {key:value[0] for key,value in parsed.items()}

class ExamwiseHandler(BaseHTTPRequestHandler):
    def send_html(self, document, status=200):
        body=document.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(body)

    def redirect(self,path):
        self.send_response(303)
        self.send_header("Location",path)
        self.send_header("Content-Length","0")
        self.end_headers()

    def do_GET(self):
        parsed=urlparse(self.path)
        query=parse_qs(parsed.query)
        msg=query.get("message",[""])[0]
        route=parsed.path
        if route=="/":
            self.send_html(overview_page(msg))
        elif route=="/schedule":
            self.send_html(schedule_page(msg,query.get("q",[""])[0],query.get("status",["all"])[0]))
        elif route=="/new-exam":
            self.send_html(new_exam_page())
        elif route=="/students":
            self.send_html(students_page(msg,query.get("q",[""])[0]))
        elif route=="/new-student":
            self.send_html(new_student_page())
        elif route=="/results":
            self.send_html(result_page(msg,query.get("session",["all"])[0],query.get("q",[""])[0]))
        elif route=="/record-marks":
            self.send_html(record_marks_page())
        elif route=="/hall-ticket":
            self.send_html(hall_ticket_page(query))
        elif route=="/revaluation":
            try: reg_id=int(query.get("registration_id",["0"])[0])
            except ValueError: reg_id=0
            self.send_html(revaluation_page(reg_id))
        elif route=="/database":
            self.send_html(database_page(query.get("table",["students"])[0],msg))
        elif route=="/schema.sql":
            try:
                content=SCHEMA_FILE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type","application/sql; charset=utf-8")
                self.send_header("Content-Disposition",'attachment; filename="examwise-schema.sql"')
                self.send_header("Content-Length",str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except OSError:
                self.send_error(404)
        else:
            self.send_html(make_page("Not found","",title_block("EXAMWISE","Page not found","That page does not exist.")+'<a class="button light" href="/">Return to overview</a>'),404)

    def do_POST(self):
        length=int(self.headers.get("Content-Length","0"))
        if length>1_000_000:
            self.send_error(413)
            return
        values=query_values(self.rfile.read(length))
        route=urlparse(self.path).path
        if route=="/create-exam":
            error=create_exam(values)
            if error:
                self.send_html(new_exam_page(error,values),400)
            else:
                self.redirect("/schedule?"+urlencode({"message":"Examination saved and eligible students registered."}))
        elif route=="/create-student":
            error=create_student(values)
            if error:
                self.send_html(new_student_page(error,values),400)
            else:
                self.redirect("/students?"+urlencode({"message":"Student added and upcoming program exams registered."}))
        elif route=="/save-marks":
            error=save_marks(values)
            if error:
                self.send_html(record_marks_page(error),400)
            else:
                self.redirect("/results?"+urlencode({"message":"Marks saved. The grade and pass status were calculated."}))
        elif route=="/publish-results":
            publish_results()
            self.redirect("/results?"+urlencode({"message":"Recorded results have been published."}))
        elif route=="/create-revaluation":
            error=create_revaluation(values)
            if error:
                try: reg_id=int(values.get("registration_id","0"))
                except ValueError: reg_id=0
                self.send_html(revaluation_page(reg_id,error),400)
            else:
                self.redirect("/results?"+urlencode({"message":"Revaluation request saved."}))
        else:
            self.send_error(404)

    def log_message(self, format_string, *args):
        print("%s - %s" % (self.address_string(), format_string % args))

def main():
    initialize_database()
    server=ThreadingHTTPServer((HOST,PORT),ExamwiseHandler)
    print("Examwise Python website running at http://"+HOST+":"+str(PORT))
    print("SQLite database: "+str(DATABASE))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nExamwise server stopped.")
    finally:
        server.server_close()

if __name__=="__main__":
    main()

