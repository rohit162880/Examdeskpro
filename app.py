from flask import Flask, request, redirect, url_for, flash, render_template_string
import sqlite3
from pathlib import Path
from datetime import date

ROOT=Path(__file__).resolve().parent
DB=ROOT/"examdesk.db"
app=Flask(__name__)
app.secret_key="examdesk-local-demo"

def connect():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY, roll TEXT UNIQUE NOT NULL, name TEXT NOT NULL, dept TEXT NOT NULL, semester INTEGER NOT NULL, email TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, dept TEXT NOT NULL, semester INTEGER NOT NULL, credits INTEGER NOT NULL DEFAULT 3);
        CREATE TABLE IF NOT EXISTS rooms(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, capacity INTEGER NOT NULL, location TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS exams(id INTEGER PRIMARY KEY, course_id INTEGER NOT NULL REFERENCES courses(id), exam_date TEXT NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL, room_id INTEGER NOT NULL REFERENCES rooms(id), notes TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS registrations(id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id), exam_id INTEGER NOT NULL REFERENCES exams(id), UNIQUE(student_id,exam_id));
        CREATE TABLE IF NOT EXISTS results(id INTEGER PRIMARY KEY, registration_id INTEGER UNIQUE NOT NULL REFERENCES registrations(id), marks REAL NOT NULL, maximum REAL NOT NULL, remarks TEXT DEFAULT '');
        """)
        if c.execute("SELECT COUNT(*) FROM students").fetchone()[0]==0:
            c.executemany("INSERT INTO students(roll,name,dept,semester,email) VALUES(?,?,?,?,?)",[
             ("CS2401","Aarav Sharma","Computer Science",4,"aarav@example.com"),("CS2402","Ananya Rao","Computer Science",4,"ananya@example.com"),("IT2401","Vihaan Patel","Information Technology",4,"vihaan@example.com")])
        if c.execute("SELECT COUNT(*) FROM courses").fetchone()[0]==0:
            c.executemany("INSERT INTO courses(code,name,dept,semester,credits) VALUES(?,?,?,?,?)",[
             ("DBMS204","Database Management Systems","Computer Science",4,4),("PY202","Python Programming","Computer Science",4,3),("NET206","Computer Networks","Information Technology",4,3)])
        if c.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]==0:
            c.executemany("INSERT INTO rooms(name,capacity,location) VALUES(?,?,?)",[("Exam Hall A",60,"Block A"),("Lab 2",35,"IT Block"),("Seminar Hall",100,"Main Block")])
        if c.execute("SELECT COUNT(*) FROM exams").fetchone()[0]==0:
            co=c.execute("SELECT id FROM courses WHERE code='DBMS204'").fetchone()
            ro=c.execute("SELECT id FROM rooms WHERE name='Exam Hall A'").fetchone()
            c.execute("INSERT INTO exams(course_id,exam_date,start_time,end_time,room_id,notes) VALUES(?,?,?,?,?,?)",(co["id"],date.today().isoformat(),"10:00","13:00",ro["id"],"Sample schedule"))
        if c.execute("SELECT COUNT(*) FROM registrations").fetchone()[0]==0:
            e=c.execute("SELECT id FROM exams LIMIT 1").fetchone()
            for s in c.execute("SELECT id FROM students LIMIT 2").fetchall(): c.execute("INSERT OR IGNORE INTO registrations(student_id,exam_id) VALUES(?,?)",(s["id"],e["id"]))

STYLE="""<style>
:root{--navy:#172554;--blue:#4358db;--bg:#f4f6fb;--ink:#202b43;--muted:#6d7890;--line:#e3e8f2}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 'Segoe UI',Arial,sans-serif}
header{background:linear-gradient(110deg,#172554,#3449a5);color:#fff;padding:20px 30px;display:flex;justify-content:space-between;align-items:center;gap:10px}.logo{font-size:22px;font-weight:800}.logo span{color:#a8baff}.small{font-size:12px;color:#d8defa}
.shell{display:grid;grid-template-columns:210px 1fr;min-height:calc(100vh - 70px)}aside{background:#fff;border-right:1px solid var(--line);padding:20px 12px}nav a{display:block;padding:11px 13px;margin:4px 0;border-radius:9px;text-decoration:none;color:#5c6780;font-weight:650}nav a:hover,nav a.on{background:#edf0ff;color:var(--blue)}main{padding:28px;max-width:1500px;width:100%;margin:auto}.head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap;margin-bottom:22px}h1{margin:0;font-size:28px;letter-spacing:-.5px}.muted{color:var(--muted)}.btn{display:inline-block;background:var(--blue);color:white;border:0;border-radius:9px;padding:10px 14px;text-decoration:none;font-weight:700;cursor:pointer}.btn.alt{background:white;color:var(--blue);border:1px solid #dbe1f4}.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px;margin-bottom:20px}.card,.panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:19px;box-shadow:0 3px 14px #17255408}.label{font-size:13px;color:var(--muted);font-weight:700}.num{font-size:30px;font-weight:800;margin-top:6px}.cols{display:grid;grid-template-columns:1.25fr 1fr;gap:17px}.panel h2{font-size:17px;margin:0 0 14px}.tablewrap{overflow:auto}table{width:100%;border-collapse:collapse;white-space:nowrap}th,td{text-align:left;padding:11px 9px;border-bottom:1px solid var(--line)}th{font-size:12px;color:var(--muted);text-transform:uppercase;background:#fafbfe}tr:last-child td{border:0}.flash{padding:12px 15px;background:#e6f7ef;color:#11694f;border-radius:9px;margin-bottom:14px}.flash.error{background:#fff0ee;color:#a72a20}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.field label{display:block;font-weight:700;font-size:13px;margin-bottom:5px}.field input,.field select,.field textarea{width:100%;padding:11px;border:1px solid #d7deeb;border-radius:8px;font:inherit;background:#fff}.full{grid-column:1/-1}.toolbar{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:12px}.search{padding:10px;border:1px solid #d7deeb;border-radius:8px;font:inherit}.empty{text-align:center;padding:24px;color:var(--muted)}.pill{background:#e6f7ef;color:#126b51;padding:3px 8px;border-radius:20px;font-size:12px;font-weight:700}.foot{font-size:12px;color:var(--muted);padding:22px 0}
@media(max-width:850px){.shell{grid-template-columns:1fr}aside{padding:7px;border-bottom:1px solid var(--line)}nav{display:flex;overflow:auto}nav a{white-space:nowrap}main{padding:16px}.cards{grid-template-columns:repeat(2,1fr)}.cols{grid-template-columns:1fr}}@media(max-width:520px){header{padding:15px}.cards{gap:8px}.card{padding:13px}.grid{grid-template-columns:1fr}.full{grid-column:auto}h1{font-size:24px}}
</style>"""

def page(title, content, active="/"):
    nav=[("Dashboard","/"),("Students","/students"),("Courses","/courses"),("Rooms","/rooms"),("Exam Schedule","/exams"),("Registrations","/registrations"),("Results","/results")]
    return render_template_string("""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{title}} · ExamDesk Pro</title>"""+STYLE+"""</head><body><header><div><div class="logo">◈ ExamDesk <span>Pro</span></div><div class="small">Examination Scheduling & Result Processing</div></div><div class="small">Academic administration</div></header><div class="shell"><aside><nav>{% for n,u in nav %}<a class="{% if active==u %}on{% endif %}" href="{{u}}">{{n}}</a>{% endfor %}</nav></aside><main>{% with msgs=get_flashed_messages(with_categories=true) %}{% for cat,msg in msgs %}<div class="flash {% if cat=='error' %}error{% endif %}">{{msg}}</div>{% endfor %}{% endwith %}{{content|safe}}<div class="foot">ExamDesk Pro · Local project demo · Data stored in examdesk.db</div></main></div><script>document.querySelectorAll('[data-search]').forEach(i=>i.addEventListener('input',()=>{let q=i.value.toLowerCase();document.querySelectorAll(i.dataset.search+' tbody tr').forEach(r=>r.style.display=r.innerText.toLowerCase().includes(q)?'':'none')}));document.querySelectorAll('[data-confirm]').forEach(a=>a.onclick=e=>{if(!confirm(a.dataset.confirm))e.preventDefault()});</script></body></html>""",title=title,content=content,nav=nav,active=active)

def allrows(sql,args=()):
    with connect() as c:return c.execute(sql,args).fetchall()
def count(sql):
    with connect() as c:return c.execute(sql).fetchone()[0]
def n(v,d=1):
    try:return int(v)
    except:return d

@app.route("/")
def dashboard():
    stats=[("Students",count("SELECT COUNT(*) FROM students")),("Courses",count("SELECT COUNT(*) FROM courses")),("Scheduled exams",count("SELECT COUNT(*) FROM exams")),("Results entered",count("SELECT COUNT(*) FROM results"))]
    exams=allrows("""SELECT e.*,c.code,c.name course,r.name room,(SELECT COUNT(*) FROM registrations x WHERE x.exam_id=e.id) enrolled FROM exams e JOIN courses c ON c.id=e.course_id JOIN rooms r ON r.id=e.room_id ORDER BY e.exam_date,e.start_time LIMIT 6""")
    recent=allrows("""SELECT s.name,s.roll,c.code,z.marks,z.maximum FROM results z JOIN registrations g ON g.id=z.registration_id JOIN students s ON s.id=g.student_id JOIN exams e ON e.id=g.exam_id JOIN courses c ON c.id=e.course_id ORDER BY z.id DESC LIMIT 5""")
    content=render_template_string("""<div class="head"><div><h1>Dashboard</h1><div class="muted">Your examination operations at a glance.</div></div><div><a class="btn" href="/exams/new">＋ Schedule exam</a> <a class="btn alt" href="/results">Enter results</a></div></div><div class="cards">{% for label,val in stats %}<div class="card"><div class="label">{{label}}</div><div class="num">{{val}}</div><div class="muted">Current records</div></div>{% endfor %}</div><div class="cols"><section class="panel"><h2>Exam schedule</h2><div class="tablewrap"><table><thead><tr><th>Date</th><th>Course</th><th>Time</th><th>Room</th><th>Enrolled</th></tr></thead><tbody>{% for e in exams %}<tr><td>{{e.exam_date}}</td><td><b>{{e.code}}</b><br><span class="muted">{{e.course}}</span></td><td>{{e.start_time}}–{{e.end_time}}</td><td>{{e.room}}</td><td><span class="pill">{{e.enrolled}}</span></td></tr>{% else %}<tr><td colspan="5" class="empty">No exams scheduled yet.</td></tr>{% endfor %}</tbody></table></div></section><section class="panel"><h2>Recent results</h2><div class="tablewrap"><table><thead><tr><th>Student</th><th>Course</th><th>Marks</th></tr></thead><tbody>{% for r in recent %}<tr><td>{{r.name}}<br><span class="muted">{{r.roll}}</span></td><td>{{r.code}}</td><td>{{"%.1f"|format(r.marks)}}/{{"%.1f"|format(r.maximum)}}</td></tr>{% else %}<tr><td colspan="3" class="empty">No results entered yet.</td></tr>{% endfor %}</tbody></table></div></section></div>""",stats=stats,exams=exams,recent=recent)
    return page("Dashboard",content)

@app.route("/students",methods=["GET","POST"])
def students():
    if request.method=="POST":
        vals=[request.form.get(k,"").strip() for k in ("roll","name","dept","email")]; sem=n(request.form.get("semester"),1)
        if not all(vals[:3]):flash("Roll number, name, and department are required.","error")
        else:
            try:
                with connect() as c:c.execute("INSERT INTO students(roll,name,dept,semester,email) VALUES(?,?,?,?,?)",(vals[0],vals[1],vals[2],sem,vals[3]))
                flash("Student added.")
            except sqlite3.IntegrityError:flash("Roll number already exists.","error")
        return redirect(url_for("students"))
    data=allrows("SELECT * FROM students ORDER BY name")
    content=render_template_string("""<div class="head"><div><h1>Students</h1><div class="muted">Student records and academic details.</div></div></div><div class="cols"><section class="panel"><h2>Student list</h2><div class="toolbar"><b>{{data|length}} records</b><input class="search" placeholder="Search..." data-search="#tbl"></div><div class="tablewrap"><table id="tbl"><thead><tr><th>Roll</th><th>Name</th><th>Department</th><th>Sem</th><th>Email</th></tr></thead><tbody>{% for s in data %}<tr><td>{{s.roll}}</td><td>{{s.name}}</td><td>{{s.dept}}</td><td>{{s.semester}}</td><td>{{s.email}}</td></tr>{% else %}<tr><td colspan="5" class="empty">No students yet.</td></tr>{% endfor %}</tbody></table></div></section><section class="panel"><h2>Add student</h2><form method="post" class="grid"><div class="field"><label>Roll number *</label><input name="roll" required></div><div class="field"><label>Full name *</label><input name="name" required></div><div class="field full"><label>Department *</label><input name="dept" required></div><div class="field"><label>Semester</label><select name="semester">{% for i in range(1,9) %}<option>{{i}}</option>{% endfor %}</select></div><div class="field"><label>Email</label><input type="email" name="email"></div><div class="field full"><button class="btn">Save student</button></div></form></section></div>""",data=data)
    return page("Students",content,"/students")

@app.route("/courses",methods=["GET","POST"])
def courses():
    if request.method=="POST":
        code=request.form.get("code","").strip().upper();name=request.form.get("name","").strip();dept=request.form.get("dept","").strip();sem=n(request.form.get("semester"));credits=n(request.form.get("credits"),3)
        try:
            with connect() as c:c.execute("INSERT INTO courses(code,name,dept,semester,credits) VALUES(?,?,?,?,?)",(code,name,dept,sem,credits))
            flash("Course added.")
        except sqlite3.IntegrityError:flash("Course code must be unique; check required fields.","error")
        return redirect(url_for("courses"))
    data=allrows("SELECT * FROM courses ORDER BY code")
    content=render_template_string("""<div class="head"><div><h1>Courses</h1><div class="muted">Manage the course catalogue.</div></div></div><div class="cols"><section class="panel"><h2>Course catalogue</h2><div class="tablewrap"><table><thead><tr><th>Code</th><th>Course</th><th>Department</th><th>Sem</th><th>Credits</th></tr></thead><tbody>{% for c in data %}<tr><td>{{c.code}}</td><td>{{c.name}}</td><td>{{c.dept}}</td><td>{{c.semester}}</td><td>{{c.credits}}</td></tr>{% else %}<tr><td colspan="5" class="empty">No courses.</td></tr>{% endfor %}</tbody></table></div></section><section class="panel"><h2>Add course</h2><form method="post" class="grid"><div class="field"><label>Code *</label><input name="code" required></div><div class="field"><label>Course name *</label><input name="name" required></div><div class="field full"><label>Department *</label><input name="dept" required></div><div class="field"><label>Semester</label><input type="number" min="1" max="8" name="semester" value="1"></div><div class="field"><label>Credits</label><input type="number" min="1" max="10" name="credits" value="3"></div><div class="field full"><button class="btn">Save course</button></div></form></section></div>""",data=data)
    return page("Courses",content,"/courses")

@app.route("/rooms",methods=["GET","POST"])
def rooms():
    if request.method=="POST":
        name=request.form.get("name","").strip();cap=n(request.form.get("capacity"),30);loc=request.form.get("location","").strip()
        try:
            if not name or cap<1:raise ValueError
            with connect() as c:c.execute("INSERT INTO rooms(name,capacity,location) VALUES(?,?,?)",(name,cap,loc))
            flash("Room added.")
        except (ValueError,sqlite3.IntegrityError):flash("Provide a unique room name and positive capacity.","error")
        return redirect(url_for("rooms"))
    data=allrows("SELECT * FROM rooms ORDER BY name")
    content=render_template_string("""<div class="head"><div><h1>Rooms & resources</h1><div class="muted">Manage halls, labs, and seating capacity.</div></div></div><div class="cols"><section class="panel"><h2>Rooms</h2><table><thead><tr><th>Room</th><th>Location</th><th>Capacity</th></tr></thead><tbody>{% for r in data %}<tr><td>{{r.name}}</td><td>{{r.location}}</td><td>{{r.capacity}}</td></tr>{% else %}<tr><td colspan="3" class="empty">No rooms yet.</td></tr>{% endfor %}</tbody></table></section><section class="panel"><h2>Add room</h2><form method="post" class="grid"><div class="field full"><label>Room name *</label><input name="name" required></div><div class="field"><label>Capacity *</label><input type="number" name="capacity" min="1" value="30" required></div><div class="field"><label>Location</label><input name="location"></div><div class="field full"><button class="btn">Save room</button></div></form></section></div>""",data=data)
    return page("Rooms",content,"/rooms")

@app.route("/exams",methods=["GET","POST"])
def exams():
    if request.method=="POST":
        cid=n(request.form.get("course_id"),0);rid=n(request.form.get("room_id"),0);d=request.form.get("exam_date","");st=request.form.get("start_time","");en=request.form.get("end_time","")
        if not all([cid,rid,d,st,en]) or st>=en:flash("Choose a course, room, date, and valid time range.","error")
        else:
            try:
                with connect() as c:
                    clash=c.execute("SELECT COUNT(*) FROM exams WHERE room_id=? AND exam_date=? AND start_time < ? AND end_time > ?",(rid,d,en,st)).fetchone()[0]
                    if clash:flash("That room is already booked during this time.","error")
                    else:c.execute("INSERT INTO exams(course_id,exam_date,start_time,end_time,room_id) VALUES(?,?,?,?,?)",(cid,d,st,en,rid));flash("Exam scheduled.")
            except sqlite3.Error:flash("Could not save the exam; check course and room selections.","error")
        return redirect(url_for("exams"))
    data=allrows("""SELECT e.*,c.code,c.name course,r.name room,r.capacity,(SELECT COUNT(*) FROM registrations g WHERE g.exam_id=e.id) enrolled FROM exams e JOIN courses c ON c.id=e.course_id JOIN rooms r ON r.id=e.room_id ORDER BY e.exam_date,e.start_time""")
    cs=allrows("SELECT * FROM courses ORDER BY code");rs=allrows("SELECT * FROM rooms ORDER BY name")
    content=render_template_string("""<div class="head"><div><h1>Exam schedule</h1><div class="muted">Plan dates, time slots, and room allocation.</div></div></div><div class="cols"><section class="panel"><h2>Scheduled exams</h2><div class="tablewrap"><table><thead><tr><th>Date</th><th>Course</th><th>Time</th><th>Room</th><th>Enrolled</th></tr></thead><tbody>{% for e in data %}<tr><td>{{e.exam_date}}</td><td><b>{{e.code}}</b><br><span class="muted">{{e.course}}</span></td><td>{{e.start_time}}–{{e.end_time}}</td><td>{{e.room}} ({{e.capacity}})</td><td>{{e.enrolled}}</td></tr>{% else %}<tr><td colspan="5" class="empty">No exams scheduled.</td></tr>{% endfor %}</tbody></table></div></section><section class="panel"><h2>Schedule an exam</h2><form method="post" class="grid"><div class="field full"><label>Course *</label><select name="course_id" required>{% for c in cs %}<option value="{{c.id}}">{{c.code}} — {{c.name}}</option>{% endfor %}</select></div><div class="field"><label>Date *</label><input type="date" name="exam_date" value="{{today}}" required></div><div class="field"><label>Room *</label><select name="room_id" required>{% for r in rs %}<option value="{{r.id}}">{{r.name}} ({{r.capacity}})</option>{% endfor %}</select></div><div class="field"><label>Start *</label><input type="time" name="start_time" value="10:00" required></div><div class="field"><label>End *</label><input type="time" name="end_time" value="13:00" required></div><div class="field full"><button class="btn" {% if not cs or not rs %}disabled{% endif %}>Save schedule</button></div></form></section></div>""",data=data,cs=cs,rs=rs,today=date.today().isoformat())
    return page("Exam schedule",content,"/exams")

@app.route("/registrations",methods=["GET","POST"])
def registrations():
    if request.method=="POST":
        sid=n(request.form.get("student_id"),0);eid=n(request.form.get("exam_id"),0)
        try:
            with connect() as c:
                info=c.execute("SELECT r.capacity,(SELECT COUNT(*) FROM registrations g WHERE g.exam_id=e.id) cnt FROM exams e JOIN rooms r ON r.id=e.room_id WHERE e.id=?",(eid,)).fetchone()
                if not info:flash("Select a valid exam.","error")
                elif info["cnt"]>=info["capacity"]:flash("Room capacity has been reached.","error")
                else:c.execute("INSERT INTO registrations(student_id,exam_id) VALUES(?,?)",(sid,eid));flash("Student registered.")
        except sqlite3.IntegrityError:flash("Student already registered or invalid selection.","error")
        return redirect(url_for("registrations"))
    data=allrows("SELECT s.roll,s.name,c.code,e.exam_date,e.start_time FROM registrations g JOIN students s ON s.id=g.student_id JOIN exams e ON e.id=g.exam_id JOIN courses c ON c.id=e.course_id ORDER BY e.exam_date,s.name")
    ss=allrows("SELECT * FROM students ORDER BY name");ee=allrows("SELECT e.id,e.exam_date,e.start_time,c.code FROM exams e JOIN courses c ON c.id=e.course_id ORDER BY e.exam_date")
    content=render_template_string("""<div class="head"><div><h1>Registrations</h1><div class="muted">Register students for scheduled examinations.</div></div></div><div class="cols"><section class="panel"><h2>Registration list</h2><table><thead><tr><th>Student</th><th>Exam</th><th>Date/time</th></tr></thead><tbody>{% for x in data %}<tr><td>{{x.name}}<br><span class="muted">{{x.roll}}</span></td><td>{{x.code}}</td><td>{{x.exam_date}} {{x.start_time}}</td></tr>{% else %}<tr><td colspan="3" class="empty">No registrations.</td></tr>{% endfor %}</tbody></table></section><section class="panel"><h2>Register student</h2><form method="post" class="grid"><div class="field full"><label>Student *</label><select name="student_id" required>{% for s in ss %}<option value="{{s.id}}">{{s.roll}} — {{s.name}}</option>{% endfor %}</select></div><div class="field full"><label>Exam *</label><select name="exam_id" required>{% for e in ee %}<option value="{{e.id}}">{{e.exam_date}} · {{e.code}} · {{e.start_time}}</option>{% endfor %}</select></div><div class="field full"><button class="btn" {% if not ss or not ee %}disabled{% endif %}>Register</button></div></form></section></div>""",data=data,ss=ss,ee=ee)
    return page("Registrations",content,"/registrations")

@app.route("/results",methods=["GET","POST"])
def results():
    if request.method=="POST":
        rid=n(request.form.get("registration_id"),0)
        try:
            marks=float(request.form.get("marks","0"));maximum=float(request.form.get("maximum","100"))
            if maximum<=0 or marks<0 or marks>maximum:raise ValueError
            with connect() as c:c.execute("INSERT INTO results(registration_id,marks,maximum,remarks) VALUES(?,?,?,?) ON CONFLICT(registration_id) DO UPDATE SET marks=excluded.marks,maximum=excluded.maximum,remarks=excluded.remarks",(rid,marks,maximum,request.form.get("remarks","").strip()))
            flash("Result saved.")
        except (ValueError,sqlite3.IntegrityError):flash("Enter valid marks and select a registered student.","error")
        return redirect(url_for("results"))
    data=allrows("""SELECT g.id reg_id,s.roll,s.name,c.code,e.exam_date,z.marks,z.maximum,z.remarks FROM registrations g JOIN students s ON s.id=g.student_id JOIN exams e ON e.id=g.exam_id JOIN courses c ON c.id=e.course_id LEFT JOIN results z ON z.registration_id=g.id ORDER BY e.exam_date,s.name""")
    content=render_template_string("""<div class="head"><div><h1>Results processing</h1><div class="muted">Enter or update marks for registered students.</div></div></div><div class="cols"><section class="panel"><h2>Results register</h2><table><thead><tr><th>Student</th><th>Course</th><th>Marks</th><th>Status</th></tr></thead><tbody>{% for r in data %}<tr><td>{{r.name}}<br><span class="muted">{{r.roll}}</span></td><td>{{r.code}}<br><span class="muted">{{r.exam_date}}</span></td><td>{% if r.marks is not none %}{{"%.1f"|format(r.marks)}}/{{"%.1f"|format(r.maximum)}}{% else %}—{% endif %}</td><td>{% if r.marks is not none %}<span class="pill">Entered</span>{% else %}Pending{% endif %}</td></tr>{% else %}<tr><td colspan="4" class="empty">Register a student for an exam first.</td></tr>{% endfor %}</tbody></table></section><section class="panel"><h2>Enter / update marks</h2><form method="post" class="grid"><div class="field full"><label>Student / exam *</label><select name="registration_id" required>{% for r in data %}<option value="{{r.reg_id}}">{{r.roll}} — {{r.name}} · {{r.code}}</option>{% endfor %}</select></div><div class="field"><label>Marks *</label><input type="number" step="0.5" min="0" name="marks" value="0" required></div><div class="field"><label>Maximum *</label><input type="number" step="0.5" min="1" name="maximum" value="100" required></div><div class="field full"><label>Remarks</label><input name="remarks"></div><div class="field full"><button class="btn" {% if not data %}disabled{% endif %}>Save result</button></div></form></section></div>""",data=data)
    return page("Results",content,"/results")

@app.route("/health")
def health():
    with connect() as c:c.execute("SELECT 1").fetchone()
    return {"status":"ok","database":"connected"}

@app.errorhandler(500)
def server_error(err):
    app.logger.exception("Unhandled ExamDesk request error")
    return page("Error",'<div class="panel"><h1>Something went wrong</h1><p>The technical error was logged in the VS Code terminal.</p><a class="btn" href="/">Return to dashboard</a></div>'),500

@app.errorhandler(404)
def missing(err):
    return page("Not found",'<div class="panel"><h1>Page not found</h1><a class="btn" href="/">Return to dashboard</a></div>'),404

if __name__=="__main__":
    init_db()
    print(f"ExamDesk Pro running at http://127.0.0.1:5000\\nDatabase: {DB}")
    app.run(host="127.0.0.1",port=5000,debug=False)
