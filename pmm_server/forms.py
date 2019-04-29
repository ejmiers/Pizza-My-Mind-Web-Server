from flask_wtf import FlaskForm
from pmm_server.date_models import Date
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email

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
