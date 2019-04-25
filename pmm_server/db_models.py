from pmm_server import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from pmm_server.date_models import Date

@login_manager.user_loader
def load_user(user_id):
    return Administrator.query.get(user_id)

class Student(db.Model, UserMixin):
    __tablename__ = 'students'
    id = db.Column('student_id', db.String(10), primary_key=True, nullable=False)
    firstName = db.Column('first_name', db.String(20), default='new_student')
    lastName = db.Column('last_name', db.String(20), default='new_student')
    email = db.Column('email', db.String(50), unique=True, default='new_student')
    major = db.Column('major', db.String(30), default='new_student')
    classDescription = db.Column('class_description', db.String(20), default='new_student')
    dateAdded = db.Column('date_added', db.String(10), default=datetime.now().strftime("%m_%d_%Y"))
    urole = db.Column(db.Integer, default=0)

    #attendanceRecords = db.relationship('attendance', backref='user',lazy=True)

    def __init__(self, id, firstName, lastName, email, major, classDescription):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.major = major
        self.classDescription = classDescription

    def get_id(self):
        return self.id

    def get_firstName(self):
        return self.firstName

    def get_lastName(self):
        return self.lastName

    def get_email(self):
        return self.email

    def get_major(self):
        return self.major

    def get_classDescription(self):
        return self.classDescription

    def get_dateAdded(self):
        return self.dateAdded

    def get_role(self):
            return self.urole

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
    urole = db.Column(db.Integer, default=1)

    def __init__(self, firstName, lastName, email, passKey):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.passKey = passKey

    def get_id(self):
        return self.id

    def get_firstName(self):
        return self.firstName

    def get_lastName(self):
        return self.lastName

    def get_email(self):
        return self.email

    def get_role(self):
        return self.urole

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

    def get_eventDate(self):
        return self.eventDate

    def get_eventName(self):
        return self.eventName

    def get_attendanceTotal(self):
        return self.attendanceTotal

    def get_newStudentTotal(self):
        return self.newStudentTotal

    def get_semester(self):
        return self.semester

    def get_year(self):
        return self.year

    def __repr__(self):
        return f"Event('{self.id}', '{self.eventDate}', '{self.eventName}',"\
                        f"'{self.semester}', '{self.year}')"

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

    def get_eventID(self):
        return self.eventID

    def get_studentID(self):
        return self.studentID

    def get_isNew(self):
        return self.isNew

    def get_semester(self):
        return self.semester

    def get_year(self):
        return self.year

    def __repr__(self):
        return f"Attendance('{self.id}', '{self.eventID}', '{self.studentID}',"\
                        f"'{self.isNew}', '{self.semester}', '{self.year}', '{self.date}')"
