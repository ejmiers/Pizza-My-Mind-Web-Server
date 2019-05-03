from flask import render_template, url_for, flash, redirect
from pmm_server import app, db, bcrypt
from pmm_server.db_models import Student, Administrator, Event, Attendance, SemesterMetaData
from pmm_server.forms import StudentSignInForm, AdminSignInForm, NewEventForm, IDReaderForm, SemesterMetaDataForm
from pmm_server.date_models import Date
from flask_login import login_user, current_user, logout_user
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You must be logged in as an administrator to view this page.', 'danger')
            return redirect(url_for('adminLogin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

# Handles requests to check student event attendance
# Returns student-console page on successful validation of Student ID
@app.route("/attendance", methods=['GET', 'POST'])
def attendance():
    form = StudentSignInForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(id=form.studentID.data).first()
        if student:
            date = Date()
            attendance = Attendance.query.filter_by(studentID=form.studentID.data).\
                                          filter_by(semester=date.season).\
                                          filter_by(year=date.year).all()
            events = Event.query.filter_by(semester=date.season).\
                                 filter_by(year=date.year).all()

            return render_template('student-console.html', title='Student Attendance', date=date, student=student, attendance=attendance, events=events)
        else:
            flash(f'The user \'{form.studentID.data}\' does not exist.\
                    Please contact your department administrator.', 'danger')
    return render_template('student-signin.html', title='Login', form=form)

# Handles requests to login to admin console
# Returns student-console page on successful validation of Student ID
@app.route("/admin", methods=['GET', 'POST'])
def adminLogin():
    form = AdminSignInForm()
    if form.validate_on_submit():
        admin = Administrator.query.filter_by(email=form.adminEmail.data).first()
        if admin and bcrypt.check_password_hash(admin.passKey, form.password.data):
            login_user(admin)
            return redirect(url_for('adminConsole'))
        elif admin and not bcrypt.check_password_hash(admin.passKey, form.password.data):
            flash(f'The password entered is invalid.\
                    Please contact your department administrator.', 'danger')
        else:
            flash(f'The admin account \'{form.adminEmail.data}\' does not exist.\
                    Please contact your department administrator.', 'danger')
    return render_template('admin-signin.html', title='Admin Console Login', form=form)

@app.route("/admin-console", methods=['GET', 'POST'])
@login_required
def adminConsole():
    date = Date()
    events = Event.query.filter_by(semester=date.season).filter_by(year=date.year).all()

    allSemesterAttendance = 0
    for event in events:
        allSemesterAttendance += int(event.attendanceTotal)

    return render_template('admin.html', title='Admin Console', events=events, date=date, attendTotal=allSemesterAttendance)

@app.route("/admin-console/start-event", methods=['GET', 'POST'])
@login_required
def adminConsole_startEvent():
    date = Date()
    eventChoices = [(str(g.id), g.eventName) for g in Event.query.filter_by(semester=date.season).filter_by(year=date.year).all()]
    eventChoices.insert(0,('none', 'none (new event session)'))

    form = NewEventForm()
    form.attendance.choices = eventChoices

    if form.validate_on_submit():
        if form.attendance.data != 'none':
            eventAttendance = Event.query.filter_by(id=form.attendance.data)\
                                         .filter_by(semester=date.season)\
                                         .filter_by(year=date.year).first()
            attendanceEntries = Attendance.query.filter_by(eventID=eventAttendance.id).all()
            event = Event(eventName=form.eventName.data, attendanceTotal=eventAttendance.attendanceTotal,
                          newStudentTotal=0, semester=date.season, year=date.year)
            db.session.add(event)
            db.session.commit()

            for entry in attendanceEntries:
                newEntry = Attendance(event.id, entry.studentID, 0, entry.semester, entry.year)
                db.session.add(newEntry)

            db.session.commit()
        else:
            event = Event(eventName=form.eventName.data, attendanceTotal=0,
                          newStudentTotal=0, semester=date.season, year=date.year)
            db.session.add(event)
            db.session.commit()

        pageTitle = "event: " + str(event.eventName)
        return redirect(url_for('adminConsole_eventSession', event_url=event.id))

    return render_template('create_event.html', title='start new event', admin=current_user, form=form)

@app.route("/admin-console/event/eventID='<event_url>'", methods=['GET', 'POST'])
@login_required
def adminConsole_eventSession(event_url):
    date = Date()
    event = Event.query.filter_by(id=event_url).first()

    if not event:
        flash(f'Cannot open event session for event id: {event_url}', 'danger')
        return redirect(url_for('adminConsole_startEvent'))

    form = IDReaderForm()
    if form.validate_on_submit():
        id = form.id.data
        if id.startswith('2000'):
            id = id[2:]
        elif id.startswith('200'):
            id = id[1:]

        student = Student.query.filter_by(id=id).first()

        if (not Attendance.query.filter_by(eventID=event.id).filter_by(studentID=id).first()):
            event.attendanceTotal += 1

            if student == None:
                isNew = True
            else:
                isNew = False

            if isNew:
                newStudent = Student(id=id)
                attendanceEntry = Attendance(eventID=event.id, studentID=id, isNew=1, semester=date.season, year=date.year)
                db.session.add(newStudent)
            else:
                attendanceEntry = Attendance(eventID=event.id, studentID=id, isNew=0, semester=date.season, year=date.year)

            db.session.add(attendanceEntry)
            db.session.commit()

            if isNew:
                flash(f'Welcome New Student!', 'success')
            else:
                flash(f'Welcome {student.firstName} {student.lastName}!', 'success')

            return redirect(url_for('adminConsole_eventSession', event_url=event.id))
        else:
            if student.firstName == 'new_student':
                flash(f'New Student ({student.id}) has already checked in!', 'danger')
            else:
                flash(f'{student.firstName} {student.lastName} has already checked in!', 'danger')
            return redirect(url_for('adminConsole_eventSession', event_url=event.id))

    return render_template('event_session.html', title='event-session', form=form, event=event)

@app.route("/admin-console/semester-details", methods=['GET', 'POST'])
@login_required
def adminConsole_semesterDetails():
    date = Date()
    form = SemesterMetaDataForm()

    if form.validate_on_submit():
        semester = SemesterMetaData.query.filter_by(semester=date.season).filter_by(year=date.year).first()
        print(semester)

        if not semester:
            semester = SemesterMetaData(semester=date.season, year=date.year)
            db.session.add(semester)
            db.session.commit()

        if form.onePoint.data:
            semester.numEventsOnePoint = form.onePoint.data
        if form.twoPoints.data:
            semester.numEventsTwoPoints = form.twoPoints.data
        if form.expirationDate.data:
            semester.dateSurveyExpire = form.expirationDate.data.strftime("%m_%d_%Y")
        if form.expirationTime.data:
            semester.timeSurveyExpire = form.expirationTime.data.strftime("%H_%M_%S")


        if form.onePoint.data or form.twoPoints.data or form.expirationDate.data or form.expirationTime.data:
            db.session.commit()
            flash(f'{date.season}, {date.year} semester details have been updated!', 'success')

    return render_template('semester_metadata.html', title='edit-semester-details', form=form, date=date)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
