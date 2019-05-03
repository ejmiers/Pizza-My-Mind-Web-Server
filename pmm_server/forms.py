from flask_wtf import FlaskForm
from pmm_server.date_models import Date
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField  
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Email, Optional

class StudentSignInForm(FlaskForm):
    studentID = StringField('Student ID', validators=[DataRequired()])
    login = SubmitField('Check Attendance')

class AdminSignInForm(FlaskForm):
    adminEmail = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Login')

class NewEventForm(FlaskForm):
    date = Date()
    eventName = StringField('Event Name', validators=[DataRequired()])
    attendance = SelectField('Use Attendance From', validators=[DataRequired()])
    startNew = SubmitField('Start Event')

class IDReaderForm(FlaskForm):
    id = StringField('Student ID', validators=[DataRequired()])

class SemesterMetaDataForm(FlaskForm):
    date = Date()
    onePoint = IntegerField('Number of events for one point', validators=[Optional()])
    twoPoints = IntegerField('Number of events for two points', validators=[Optional()])
    expirationDate = DateField('Survey expiration date', default=date.currentDay, validators=[Optional()])
    expirationTime = TimeField('Survey expiration time', default=date.currentTime, validators=[Optional()])
    updateSemester = SubmitField('Update Semester')
