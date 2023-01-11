import os
import json, time, random
from flask import Flask, render_template, request, url_for, flash, redirect, session, send_from_directory
from flask_login import LoginManager, login_required
from scholasticate.student import Student
from scholasticate.location import Location
from scholasticate.course import Course
from scholasticate.school import School
from scholasticate.util import getUsefulUserInformation, render_template_wrapper

import scholasticate.route_study_group, scholasticate.route_study_group_invitation, scholasticate.route_message, scholasticate.route_friend_request, scholasticate.route_profile, scholasticate.route_course, scholasticate.route_search, scholasticate.route_accepted_user
import scholasticate.database as db

def run_website(config = None, run = True):

	template_folder = os.path.join(os.path.dirname(__file__), 'templates')
	static_folder = os.path.join(os.path.dirname(__file__), 'static')
	print("using template folder %s" % template_folder)
	print("using static folder %s" % static_folder)

	app = Flask(__name__,
		template_folder=template_folder,
		static_url_path='/static',
		static_folder=static_folder)

	if config is not None:
		app.config.from_mapping(config)
	else:
		app.config.from_pyfile('_config.py')

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	def get_name_from_student_id(student_id):
		student = db.Database().get_student(student_id)
		if student is None:
			return "Invalid Student"
		return student.get_name()

	app.jinja_env.globals.update(get_name_from_student_id=get_name_from_student_id)

	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(student_id):
		database = db.Database()
		return database.get_student(student_id)

	@app.route('/')
	def index():
		userID = session.get('userID')

		thisStudent = db.Database().get_student(int(userID or "-1"))
		friendsSerialized = []
		friendRequestsSerialized = []
		studentInfo = None
		if (thisStudent is not None):
			studentInfo = getUsefulUserInformation(userID=int(userID), full_status=True)
			friends = thisStudent.get_friends()
			for friend in friends:
				friendsSerialized.append(friend.serialize())

			receivedFriendRequests = thisStudent.get_received_friend_requests()
			sentFriendRequests = thisStudent.get_sent_friend_requests()
			for request in receivedFriendRequests:
				friendRequestsSerialized.append(request.serialize())
			for request in sentFriendRequests:
				friendRequestsSerialized.append(request.serialize())

		return render_template_wrapper('index.html', friends=json.dumps(friendsSerialized), friendRequests=json.dumps(friendRequestsSerialized), studentInfo=studentInfo)

	@app.route('/setLocation/<id>', methods=['POST'])
	def setLocation(id):
		userID = session.get('userID')
		if (userID is None or int(session.get('userID')) != int(id)):
			return redirect(url_for('auth.login'))
		student = db.Database().get_student(int(id))
		#student.set_location(Location(random.random() * 160 - 80, random.random() * 360 - 180))
		student.set_location(Location(request.json.get("latitude"), request.json.get("longitude")))
		return "200"

	@app.route('/getUsersAndGroups/<id>', methods=["GET"])
	def getUsersAndGroups(id):
		userID = session.get('userID')
		if (userID is None or int(session.get('userID')) != int(id)):
			return redirect(url_for('auth.login'))
		database = db.Database()
		thisStudent = database.get_student(int(id))
		require_sharing = (request.args.get('require_sharing') == "true" and True) or False
		students = database.get_online_students(self_student=thisStudent, require_sharing=require_sharing)
		groups = thisStudent.get_study_groups()
		if groups is not None:
			students.extend(groups)
		distances = thisStudent.calculateRelativeDistances(students)
		ret = []
		for distance in distances:
			ret.append(distance)
		return json.dumps(ret)

	@app.route('/list', methods=["GET"])
	def listEntities():
		database = db.Database()
		students = database.get_online_students()
		serializedStudents = []
		for student in students:
			serializedStudents.append(student.serialize())
		groups = database.get_public_study_groups()
		serializedGroups = []
		for group in groups:
			serializedGroups.append(group.serialize())
		return render_template_wrapper('list.html', onlineStudents=json.dumps(serializedStudents), publicStudyGroups=json.dumps(serializedGroups))

	@app.route('/notifications', methods=['GET'])
	def notifications():
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		return render_template_wrapper("notifications.html")

	@app.route('/getNotifications', methods=['GET'])
	def getNotifications():
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		### Check for study group sessions that are about to start and sends notifications for them
		student = db.Database().get_student(int(userID))
		if student is not None:
			student.check_for_upcoming_study_sessions()

		data = getUsefulUserInformation(getStudent=False, notifications=True)
		return data

	@app.route('/deleteNotification/<notification_id>', methods=['POST'])
	def deleteNotification(notification_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		notification = db.Database().get_notification(int(notification_id))
		print(notification.serialize())
		if notification is None or notification.get_student() != db.Database().get_student(userID):
			return "Invalid notification!"

		notification.delete()
		return "200"

	scholasticate.route_profile.route(app)

	scholasticate.route_study_group.route(app)

	scholasticate.route_study_group_invitation.route(app)

	scholasticate.route_message.route(app)

	scholasticate.route_friend_request.route(app)

	scholasticate.route_course.route(app)
	
	scholasticate.route_search.route(app)

	scholasticate.route_accepted_user.route(app)

	@app.errorhandler(404)
	def page_not_found(e):
		return render_template('404.html'), 404

	@app.errorhandler(403)
	def page_forbidden(e):
		return render_template('403.html'), 403

	if run:
		app.run(host='0.0.0.0', port='8080', debug=True)

	return app
