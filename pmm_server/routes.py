from flask import render_template, url_for, flash, redirect, send_file
from pmm_server import app, db, bcrypt
from pmm_server.db_models import Student, Administrator, Event, Attendance, SemesterMetaData
from pmm_server.forms import (StudentSignInForm, AdminSignInForm,
                              NewEventForm, IDReaderForm, SemesterMetaDataForm,
                              LoadEventForm)
from pmm_server.date_models import Date
from pmm_server.spreadsheet_models import EventSpreadsheet, MasterSpreadsheet
from flask_login import login_user, current_user, logout_user
from functools import wraps
import os

# Custom decorator that checks to see if a user has been authenticated as an admin
# Redirects to admin login page
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

            semester = SemesterMetaData.query.filter_by(semester=date.season).\
                                              filter_by(year=date.year).first()

            # Check to see if student qualifies for any points
            if (semester == None):
                pointsQualified = (None, None)
            elif (len(attendance) >= semester.numEventsTwoPoints):
                pointsQualified = (0,2)
            elif (len(attendance) >= semester.numEventsOnePoint):
                pointsQualified = (0,1)
            else:
                pointsQualified = (semester.numEventsOnePoint - len(attendance), 0)


            return render_template('student-console.html', title='Student Attendance', date=date, student=student,
                                    pointsQualified=pointsQualified, attendance=attendance, events=events)
        else:
            flash(f'The user \'{form.studentID.data}\' does not exist.\
                    Please contact your department administrator.', 'danger')
    return render_template('student-signin.html', title='Login', form=form)

# Handles requests to login to admin console
# Returns admin-console page on successful login authentication
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

# Main route for the admin console
# User must be logged in to view this page
@app.route("/admin-console", methods=['GET', 'POST'])
@login_required
def adminConsole():
    date = Date()
    events = Event.query.filter_by(semester=date.season).filter_by(year=date.year).all()

    generateMasterSpreadsheet = MasterSpreadsheet()
    masterSpreadsheet = ('master', generateMasterSpreadsheet.filename)

    # Attendance Total is used to generate percentage style chart on admin-console page
    allSemesterAttendance = 0
    eventsWithFilePath = []
    for event in events:
        allSemesterAttendance += int(event.attendanceTotal)
        spreadsheet = EventSpreadsheet(event.id)

        eventWithFilePath = (event, ('event',spreadsheet.filename))
        eventsWithFilePath.append(eventWithFilePath)



    return render_template('admin.html', title='Admin Console', events=eventsWithFilePath, date=date,
                            attendTotal=allSemesterAttendance, masterSpreadsheet=masterSpreadsheet)

# Routes to event setup choice page
# Will redirect to new event setup page or re-open event page depending on link chosen
@app.route("/admin-console/create-or-repoen-event")
@login_required
def adminConsole_createOrReopenEvent():
    return render_template('event-choice.html', title='event setup choice')

# Route within the admin console used to start PMM events
# Redirects to a new event session upon validation of NewEventForm
# User must be logged in to view this page
@app.route("/admin-console/start-event", methods=['GET', 'POST'])
@login_required
def adminConsole_startEvent():
    date = Date()
    eventChoices = [(str(g.id), g.eventName) for g in Event.query.filter_by(semester=date.season).filter_by(year=date.year).all()]
    eventChoices.insert(0,('none', 'none (new event session)'))

    form = NewEventForm()
    form.attendance.choices = eventChoices

    if form.validate_on_submit():
        # Check to see if user chose to create a new pmm event with preexisting attendance data
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

        # Create new pmm event with blank attendance record
        else:
            event = Event(eventName=form.eventName.data, attendanceTotal=0,
                          newStudentTotal=0, semester=date.season, year=date.year)
            db.session.add(event)
            db.session.commit()

        pageTitle = "event: " + str(event.eventName)
        return redirect(url_for('adminConsole_eventSession', event_url=event.id))

    return render_template('create_event.html', title='start new event', form=form)

# Route within the admin console used to start PMM events
# Redirects to a new event session upon validation of NewEventForm
# User must be logged in to view this page
@app.route("/admin-console/reopen-event", methods=['GET', 'POST'])
@login_required
def adminConsole_openExistingEvent():
    date = Date()
    eventChoices = [(str(g.id), g.eventName) for g in Event.query.filter_by(semester=date.season).filter_by(year=date.year).all()]

    form = LoadEventForm()
    form.chooseEvent.choices = eventChoices

    if form.validate_on_submit():
        eventChosen = Event.query.filter_by(id=form.chooseEvent.data)\
                                 .filter_by(semester=date.season)\
                                 .filter_by(year=date.year).first()

        pageTitle = "event: " + str(eventChosen.eventName)
        return redirect(url_for('adminConsole_eventSession', event_url=eventChosen.id))

    return render_template('reload_event.html', title='Re-open existing event', form=form)

# Route for a new event session
# Redirects back to itself upon scanning a student ID
# User must be logged in to view this page
@app.route("/admin-console/event/eventID='<event_url>'", methods=['GET', 'POST'])
@login_required
def adminConsole_eventSession(event_url):
    date = Date()
    event = Event.query.filter_by(id=event_url).first()
    attendance = Attendance.query.filter_by(eventID=event.id).all()

    if not event:
        flash(f'Cannot open event session for event id: {event_url}', 'danger')
        return redirect(url_for('adminConsole_startEvent'))

    form = IDReaderForm()
    if form.validate_on_submit():
        id = form.id.data

        # Trim scanned barcode ID to 00xxxxxx ID format
        if id.startswith('2000'):
            id = id[2:]
        elif id.startswith('200'):
            id = id[1:]

        student = Student.query.filter_by(id=id).first()

        # Check that the student hasn't already been registered for the event
        if (not Attendance.query.filter_by(eventID=event.id).filter_by(studentID=id).first()):
            event.attendanceTotal += 1

            # If a student is new, create an entry in the database and generate an attendance record
            # Otherwise just generate the attendance record
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

    return render_template('event_session.html', title='event-session', form=form, event=event, attendance=attendance)

# Route that allows an admin to update semester parameters
# User must be logged in to view this page
@app.route("/admin-console/semester-details", methods=['GET', 'POST'])
@login_required
def adminConsole_semesterDetails():
    date = Date()
    form = SemesterMetaDataForm()

    if form.validate_on_submit():
        semester = SemesterMetaData.query.filter_by(semester=date.season).filter_by(year=date.year).first()

        # Current Semester not an entry in the database, create a new semester entry
        if not semester:
            semester = SemesterMetaData(semester=date.season, year=date.year)
            db.session.add(semester)
            db.session.commit()

        # Update semester fields for number of points and time/date survey expiration
        if form.onePoint.data:
            semester.numEventsOnePoint = form.onePoint.data
        if form.twoPoints.data:
            semester.numEventsTwoPoints = form.twoPoints.data
        if form.expirationDate.data:
            semester.dateSurveyExpire = form.expirationDate.data.strftime("%m_%d_%Y")
        if form.expirationTime.data:
            semester.timeSurveyExpire = form.expirationTime.data.strftime("%H_%M_%S")

        # if a change has been made, commit the data
        if form.onePoint.data or form.twoPoints.data or form.expirationDate.data or form.expirationTime.data:
            db.session.commit()
            flash(f'{date.season}, {date.year} semester details have been updated!', 'success')

    return render_template('semester_metadata.html', title='edit-semester-details', form=form, date=date)

# @app.route("/admin-console/edit-admin", methods=['GET', 'POST'])
# @login_required
# def adminConsole_editAdmin():

@app.route("/admin-console/download/file='<file>'", methods=['GET', 'POST'])
@login_required
def downloadFile(file):

    if file[2:7] == 'event':
        path = os.getcwd() + '/pmm_server/spreadsheets/events/' + file[11:len(file)-2]
        return send_file(path, as_attachment=True, cache_timeout=0)

    elif file[2:8] == 'master':
        path = os.getcwd() + '/pmm_server/spreadsheets/master/' + file[12:len(file)-2]
        return send_file(path, as_attachment=True, cache_timeout=0)

    flash(f'ERROR: Cannot download file', 'danger')

    return redirect(url_for('adminConsole'))


@app.route("/admin-console/event/eventID='<event_url>/deleteID=<student_id>'", methods=['GET', 'POST'])
@login_required
def eventCheckout(event_url, student_id):

    event = Event.query.filter_by(id=event_url).first()
    attendanceRecord = Attendance.query.filter_by(eventID=event_url).filter_by(studentID=student_id).first()

    event.attendanceTotal -= 1
    db.session.delete(attendanceRecord)
    db.session.commit()

    flash(f'{student_id} has been checked out of this event', 'warning')

    return redirect(url_for('adminConsole_eventSession', event_url=event_url))

# logout signed-in admins
# Redirect back to the home page
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
