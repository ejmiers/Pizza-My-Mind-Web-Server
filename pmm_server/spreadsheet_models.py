from pmm_server import db
from pmm_server.date_models import Date
from pmm_server.db_models import Student, Administrator, Event, Attendance, SemesterMetaData
import csv
import os.path

class EventSpreadsheet():

    def __init__(self, eventID):
        self.event = Event.query.filter_by(id=eventID).first()
        print(self.event)
        self.filename = str(self.event.eventName.replace(' ', '_')) + '__' + str(self.event.eventDate) + '.csv'
        self.attendance = Attendance.query.filter_by(eventID=eventID).all()
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
