from pmm_server import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from pmm_server.date_models import Date

@login_manager.user_loader
def load_user(user_id):
    return Administrator.query.get(user_id)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column('student_id', db.String(10), primary_key=True, nullable=False)
    firstName = db.Column('first_name', db.String(20), default='new_student')
    lastName = db.Column('last_name', db.String(20), default='new_student')
    email = db.Column('email', db.String(50), default='new_student')
    major = db.Column('major', db.String(30), default='new_student')
    classDescription = db.Column('class_description', db.String(20), default='new_student')
    dateAdded = db.Column('date_added', db.String(10), default=datetime.now().strftime("%m_%d_%Y"))

    def __init__(self, id, firstName='new_student', lastName='new_student', email='new_student', major='new_student', classDescription='new_student'):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.major = major
        self.classDescription = classDescription

    def __repr__(self):
        return f"Student('{self.id}', '{self.firstName}', '{self.lastName}',"\
                        f"'{self.email}', '{self.major}', '{self.classDescription}', '{self.dateAdded}')"


class Administrator(db.Model, UserMixin):
    __tablename__ = 'admins'
    id = db.Column('admin_id', db.Integer, primary_key=True, nullable=False)
    firstName = db.Column('first_name', db.String(20), nullable=False)
    lastName = db.Column('last_name', db.String(20), nullable=False)
    email = db.Column('email', db.String(50), nullable=False)
    passKey = db.Column('pass_hash', db.String(60), nullable=False)

    def __init__(self, firstName, lastName, email, passKey):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.passKey = passKey

    def __repr__(self):
        return f"Administrator('{self.id}', '{self.firstName}', '{self.lastName}',"\
                             f"'{self.email}')"

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column('event_id', db.Integer, primary_key=True, nullable=False)

    date = Date()
    eventDate = db.Column('event_date', db.String(10), default=date.stringDate)
    eventName = db.Column('event_name', db.String(50), nullable=False)
    attendanceTotal = db.Column('attendance_total', db.Integer, nullable=False, default=0)
    newStudentTotal = db.Column('new_student_total', db.Integer, nullable=False, default=0)
    semester = db.Column('semester', db.String(6), nullable=False, default=date.season)
    year = db.Column('year', db.String(4), nullable=False, default=date.year)

    def __init__(self, eventName, attendanceTotal, newStudentTotal, semester, year):
        self.eventName = eventName
        self.attendanceTotal = attendanceTotal
        self.newStudentTotal = newStudentTotal
        self.semester = semester
        self.year = year

    def __repr__(self):
        return f"Event('{self.id}', '{self.eventDate}', '{self.eventName}',"\
                        f"'{self.attendanceTotal}','{self.semester}', '{self.year}')"

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column('attendance_id', db.Integer, primary_key=True, nullable=False)
    date = Date()
    eventID = db.Column('event_id', db.Integer, nullable=False)
    studentID = db.Column('student_id', db.String(10), db.ForeignKey('students.student_id'),
                            nullable=False)
    isNew = db.Column('is_new', db.Integer, nullable=False, default=0)
    semester = db.Column('semester', db.String(6), nullable=False, default=date.season)
    year = db.Column('year', db.String(4), nullable=False, default=date.year)
    date = db.Column('date_added', db.String(10), default=date.stringDate)

    def __init__(self, eventID, studentID, isNew, semester, year):
        self.eventID = eventID
        self.studentID = studentID
        self.isNew = isNew
        self.semester = semester
        self.year = year

    def __repr__(self):
        return f"Attendance('{self.id}', '{self.eventID}', '{self.studentID}',"\
                        f"'{self.isNew}', '{self.semester}', '{self.year}', '{self.date}')"

class SemesterMetaData(db.Model):
    __tablename__ = 'semester_metadata'
    id = db.Column('semester_id', db.Integer, primary_key=True, nullable=False)
    date = Date()
    semester = db.Column('semester', db.String(6), nullable=False, default=date.season)
    year = db.Column('year', db.String(4), nullable=False, default=date.year)
    numEventsOnePoint = db.Column('num_events_one_point', db.Integer, nullable=False, default=10)
    numEventsTwoPoints = db.Column('num_events_two_points', db.Integer, nullable=False, default=12)
    dateSurveyExpire = db.Column('survey_expiration_date', db.String(10), default='null')
    timeSurveyExpire = db.Column('survey_expiration_time', db.String(10), default='null')

    def __init__(self, semester, year):
        self.semester = semester
        self.year = year

    def __repr__(self):
        return f"Semester('{self.id}', '{self.semester}', '{self.year}',"\
                        f"'{self.numEventsOnePoint}', '{self.numEventsTwoPoints}',"\
                        f"'{self.dateSurveyExpire}', '{self.timeSurveyExpire}')"

class CourseData(db.Model):
    __tablename__ = 'course_data'
    date = Date()
    id = db.Column('course_id', db.Integer, primary_key=True, nullable=False)
    semester = db.Column('semester', db.String(6), nullable=False, default=date.season)
    year = db.Column('year', db.String(4), nullable=False, default=date.year)
    crn = db.Column('crn', db.Integer, nullable=False)
    course = db.Column('course', db.String(10), nullable=False)
    section = db.Column('section', db.String(5), nullable=False)
    title = db.Column('title', db.String(100), nullable=False)
    hours = db.Column('hours', db.String(3), nullable=False)
    llc = db.Column('area_of_llc', db.String(10))
    type = db.Column('type', db.String(3), nullable=False)
    days = db.Column('days', db.String(3))
    time = db.Column('time', db.String(9))
    location = db.Column('location', db.String(15), nullable=False)
    instructor = db.Column('instructor', db.String(50), nullable=False)
    seats = db.Column('seats_still_available', db.Integer, nullable=False)
    status = db.Column('status', db.String(6), nullable=False)

    def __init__(self, crn, course, section, title, hours, llc, type, days, time,
                 location, instructor, seats, status):
        self.crn = crn
        self.course = course
        self.section = section
        self.title = title
        self.hours = hours
        self.llc = llc
        self.type = type
        self.days = days
        self.time = time
        self.location = location
        self.instructor = instructor
        self.seats = seats
        self.status = status

    def __repr__(self):
        return f"Course('{self.id}', '{self.semester}', '{self.year}', '{self.crn}',"\
                      f"'{self.course}', '{self.title}', '{self.hours}', '{self.llc}',"\
                      f"'{self.type}', '{self.days}', '{self.time}', '{self.location}',"\
                      f"'{self.instructor}', '{self.seats}', '{self.status}')"
