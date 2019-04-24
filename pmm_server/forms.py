from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class StudentSignInForm(FlaskForm):
    studentID = StringField('Student ID', validators=[DataRequired()])
    login = SubmitField('Login')

class AdminSignInForm(FlaskForm):
    adminEmail = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Login')
