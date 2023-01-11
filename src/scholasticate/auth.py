from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .student import Student
from .database import Database
import time
from scholasticate.util import name_validity_check

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
	return render_template('login.html', status="")

@auth.route('/login', methods=["POST"])
def login_post():
	database = Database()
	studentEmail = request.form.get("email")
	enteredPassword = request.form.get("password")
	studentToLogin = database.search_student_email(studentEmail)

	if not studentToLogin:
		# There is no account associated with the provided email address.
		return render_template('login.html', status="There is no account with this email address.")
	elif not check_password_hash(studentToLogin[0].get_hashpw(), enteredPassword):
		# The entered password is incorrect.
		return render_template('login.html', status="The password is incorrect.")

	# If the log-in is successful, go to the user profile:
	login_user(studentToLogin[0])
	flash('Logged in successfully.')
	loggedInID = studentToLogin[0].get_id()
	
	# Since location_last_updated determines online status, this is necessary to
	# make the user not show up as "Offline" when they log in. That would be weird!
	studentToLogin[0].set_location_last_updated(int(time.time()))

	session['userID'] = loggedInID
	return redirect(url_for('profile', id=str(loggedInID)))

@auth.route('/register')
def register():
	database = Database()
	return render_template('signup.html', schools = database.get_all_schools())

@auth.route('/register', methods=['POST'])
def register_post():
	database = Database()
	studentEmail = request.form.get("email")
	studentPassword = request.form.get("password")
	studentName = request.form.get("name")
	studentSchool = request.form.get("school")

	# Remove whitespace
	studentName = studentName.strip()

	namecheck = name_validity_check(studentName)
	if namecheck != True:
		return render_template('login.html', status=namecheck)

	# Searching if a student already exists with the desired email.
	initialSearchStudent = database.search_student_email(studentEmail, True)
	if initialSearchStudent:
		return render_template('login.html', status="An account already exists under this email.")
	
	schoolObject = database.get_school(studentSchool)
	if schoolObject is None:
		return render_template('login.html', status="Invalid School.")
	
	# If no student exists, hash the password and create a new user.
	hashedPassword = generate_password_hash(studentPassword, method='sha256')
	database.create_student(studentEmail, hashedPassword, studentName, schoolObject)

	# After the user is created, reprompt the user to login.
	return redirect(url_for('auth.login'))

@auth.route('/questionnaire/<id>')
def questionnaire(id):
	database = Database()
	student = database.get_student(int(id))
	user_question = student.get_security_question()
	if (user_question != None):
		return render_template('securityQuestion.html', user_question=user_question, profileID=id)
	return render_template('login.html', status="Sorry, the password reset feature has not been configured for the desired account.")

@auth.route('/questionnaire/<id>', methods=['POST'])
def questionnairePost(id):
	database = Database()
	student = database.get_student(int(id))
	answer = request.form.get("answer")
	if answer == student.get_security_answer():
		return redirect(url_for('auth.changePassword'))
	else:
		return render_template('login.html', status="Incorrect security question answer")

@auth.route('/forgotPassword')
def forgotPassword():
	return render_template('forgotPassword.html')

@auth.route('/forgotPassword', methods=['POST'])
def forgotPassword_post():
	database = Database()
	studentEmail = request.form.get("email")
	foundStudent = database.search_student_email(studentEmail)
	if not foundStudent:
		# There is no account associated with the provided email address.
		return render_template('login.html', status="There is no account with thie provided email address. Please try logging in to another account.")
	return redirect(url_for('auth.questionnaire', id=foundStudent[0].get_id()))

@auth.route('/forgotUsername')
def forgotUsername():
	return render_template('forgotUsername.html')

@auth.route('/changePassword')
def changePassword():
	return render_template('changePassword.html')

@auth.route('/changePassword', methods=['POST'])
def changePassword_post():
	database = Database()
	studentEmail = request.form.get("email")
	studentNewPassword = request.form.get("password")
	foundStudent = database.search_student(studentEmail)

	if not foundStudent:
		# There is no account associated with the provided email address.
		return render_template('login.html', status="There is no account with thie provided email address. Please try logging in to another account.")

	hashedNewPassword = generate_password_hash(studentNewPassword, method='sha256')
	foundStudent[0].set_hashpw(hashedNewPassword)
	return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
	logout_user()
	session.pop('userID')
	return redirect(url_for('index'))