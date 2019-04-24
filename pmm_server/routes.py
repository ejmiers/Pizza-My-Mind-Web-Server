from flask import render_template, url_for, flash, redirect
from pmm_server import app, db, bcrypt
from pmm_server.db_models import Student, Administrator, Event, Attendance
from pmm_server.forms import StudentSignInForm, AdminSignInForm
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
            return render_template('student-console.html', title='Student Attendance', student=student)
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
    # if Student.query.filter_by(id=current_user.get_id).first():
    #     flash('You do not have permission to access this page.', 'danger')
    #     return redirect(url_for('home'))
    return "<p1>Pardon our dust! Console under construction.</p1>"

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/test")
def test():
    flash(f'{current_user}  class: {type(current_user)}')
    return redirect(url_for('home'))
