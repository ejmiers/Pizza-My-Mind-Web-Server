from pmm_server import db
from pmm_server.date_models import Date
from pmm_server.db_models import Student, Administrator, Event, Attendance, SemesterMetaData
import csv
import os.path

class EventSpreadsheet():

    def __init__(self, eventID):
        self.event = Event.query.filter_by(id=eventID).first()
        self.attendance = Attendance.query.filter_by(eventID=eventID).all()
        self.filename = str(self.event.eventName.replace(' ', '_')) + '__' + str(self.event.eventDate) + '.csv'
        self.filepath = os.getcwd() + '/pmm_server/spreadsheets/events/'
        self.generateSpreadsheet()

    def generateSpreadsheet(self):
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)

        fullPath = os.path.join(self.filepath, self.filename)
        with open(fullPath, mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'FIRST', 'LAST', 'EMAIL', 'YEAR', 'IS_NEW'])

            for entry in self.attendance:
                student = Student.query.filter_by(id=entry.studentID).first()
                row = [student.id, student.firstName, student.lastName,
                       student.email, student.classDescription, entry.isNew]
                writer.writerow(row)

class MasterSpreadsheet():

    def __init__(self):
        date = Date()
        self.attendance = Attendance.query.filter_by(semester=date.season, year=date.year)
        self.events = Event.query.filter_by(semester=date.season, year=date.year)
        self.students = Student.query.all()
        self.filename = str(date.season) + str(date.year) + '__Master_Spreadsheet.csv'
        self.filepath = os.getcwd() + '/pmm_server/spreadsheets/master/'
        self.generateSpreadsheet()

    def generateSpreadsheet(self):
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
        # else:
        #     if os.path.exists(os.path.join(self.filepath, self.filename)):
        #         os.remove(os.path.join(self.filepath, self.filename))

        fullPath = os.path.join(self.filepath, self.filename)
        with open(fullPath, mode='w') as f:
            writer = csv.writer(f)

            header = ['First','Last', 'Major', 'Email', 'Class']
            for event in self.events:
                header.append(event.eventName)

            eventTotals  = ['','','','','']
            for event in self.events:
                eventTotals.append(event.attendanceTotal)

            print(eventTotals)
            writer.writerow(header)

            for student in self.students:
                row = [student.firstName, student.lastName, student.major,
                       student.email, student.classDescription]

                for event in self.events:
                    if Attendance.query.filter_by(eventID=event.id).filter_by(studentID=student.id).first() != None:
                        row.append('1')
                    else:
                        row.append('')

                writer.writerow(row)

            writer.writerow(eventTotals)
