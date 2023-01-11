import json
import io
import base64
from flask import app, render_template, request, url_for, redirect, session, flash, abort
from flask_login import logout_user
import scholasticate.database as db
from scholasticate.util import getUsefulUserInformation, render_template_wrapper
from scholasticate.course import Course
from scholasticate.profile_picture import Profile_Picture
from scholasticate.util import name_validity_check, get_session_student

def route(app):

	@app.route('/profile/<id>', methods=['GET'])
	def profile(id):
		userID = session.get('userID')
		if userID is None:
			userID = "0"

		database = db.Database()
		thisStudent = database.get_student(int(id))
		if thisStudent is None:
			abort(404)

		studentInfo = getUsefulUserInformation(userID=int(id), profilePicture=True, school=True, currentCourses=True,
		pastCourses=True, friends=True, studyGroups=True, clothing=True, online_status=True, full_status=(thisStudent==database.get_student(int(userID))))
		# userInfo = getUsefulUserInformation(all=True)
		return render_template_wrapper('profile.html', studentInfo=studentInfo, profileID=userID)

	@app.route('/profile/<id>/edit', methods=['GET'])
	def editProfile(id):
		database = db.Database()

		student, studentID = get_session_student(database, session, id, True)
		if type(student) == int:
			abort(student)

		studentInfo = getUsefulUserInformation(school=True, currentCourses=True)

		clothingInfo = student.get_clothing()
		allClothingSerialized = []
		for item in clothingInfo:
			allClothingSerialized.append(json.loads(item.serialize()))

		availabilityInfo = student.get_schedule()
		allTimesSerialized = []
		for time in availabilityInfo:
			allTimesSerialized.append(json.loads(time.serialize()))

		studentInfo = getUsefulUserInformation(userID=studentID, profilePicture=True)

		return render_template_wrapper('editProfile.html', allClothingItems=json.dumps(allClothingSerialized),
		 availabilityList=json.dumps(allTimesSerialized), studentInfo=studentInfo, profileID=id)

	@app.route('/profile/<id>/edit', methods=['POST'])
	def editProfile_Post(id):
		database = db.Database()

		student, studentID = get_session_student(database, session, id, True)
		if type(student) == int:
			abort(student)

		name = request.form.get("name").strip()
		namecheck = name_validity_check(name)
		if namecheck != True:
			flash(namecheck)
			return redirect(url_for('profile', id=id))

		bio = request.form.get("bio")
		invisible = request.form.get("invisible")
		courseIDs = json.loads(request.form.get("courseIds"))
		studentCourses = student.get_current_courses()
		for course in studentCourses:
			student.remove_current_course(course)
		for courseID in courseIDs:
			student.add_current_course(Course(database, int(courseID)))

		studentPastCourses = student.get_past_courses()
		courseHistoryIDs = json.loads(request.form.get("courseHistoryIds"))
		for course in studentPastCourses:
			student.remove_past_course(course)
		for pastCourseID in courseHistoryIDs:
			student.add_past_course(Course(database, int(pastCourseID)))

		studentPastWardrobe = student.get_clothing()
		if (request.form.get("newClothingItems")):
			newClothingItems = json.loads(request.form.get("newClothingItems"))
			for pastItem in studentPastWardrobe:
				student.remove_clothing(pastItem.get_article(), pastItem.get_brand(), pastItem.get_color())
			for item in newClothingItems:
				student.add_clothing(item["article"], item["brand"], [item["color_red"], item["color_green"], item["color_blue"]])
		else:
			for pastItem in studentPastWardrobe:
				student.remove_clothing(pastItem.get_article(), pastItem.get_brand(), pastItem.get_color())

		studentPastSchedule = student.get_schedule()
		if (request.form.get("newAvailabilities")):
			newSchedule = json.loads(request.form.get("newAvailabilities"))
			for pastTimeItem in studentPastSchedule:
				student.delete_time(pastTimeItem.get_weekday(), pastTimeItem.get_start_time(), pastTimeItem.get_end_time())
			for newTimeItem in newSchedule:
				student.add_time(newTimeItem["weekday"], newTimeItem["start_time"], newTimeItem["end_time"])
		else:
			for pastTimeItem in studentPastSchedule:
				student.delete_time(pastTimeItem.get_weekday(), pastTimeItem.get_start_time(), pastTimeItem.get_end_time())

		profilePictureString = request.form.get("basePhotoString")
		base64_length = len(profilePictureString)
		size_of_image = (base64_length * (3/4)) - profilePictureString.count("=")
		print(size_of_image)
		if profilePictureString != "" and size_of_image > 20000 and size_of_image < 1000000:
			profilePhoto = student.get_profile_picture()
			if profilePhoto is None:
				database.create_profile_picture(student, profilePictureString)
			else:
				profilePhoto.set_string(profilePictureString)

		student.set_name(name)
		student.set_bio(bio)
		student.set_invisible(bool(invisible))
		return redirect(url_for('profile', id=id))

	@app.route('/setQuestionnaire/<id>')
	def setQuestionnaire(id):
		database = db.Database()
		student, studentID = get_session_student(database, session, id, True)
		if type(student) == int:
			abort(student)

		return render_template('setSecurityQuestion.html', profileID=id)

	@app.route('/setQuestionnaire/<id>', methods=['POST'])
	def setQuestionnairePost(id):
		database = db.Database()
		student, studentID = get_session_student(database, session, id, True)
		if type(student) == int:
			abort(student)

		question = request.form.get("question")
		answer = request.form.get("answer")
		student.set_security_question(question)
		student.set_security_answer(answer)

		return redirect(url_for('profile', id=id))

	@app.route('/profile/<id>/deactivate', methods=['POST'])
	def deactivateAccount(id):
		database = db.Database()

		student, studentID = get_session_student(database, session, id, True)
		if type(student) == int:
			abort(student)

		# Ensure the student does not own any study groups
		groups = student.get_study_groups()
		for g in groups:
			if g.is_owner(student):
				flash("You cannot deactivate your account if you own a group!")
				return redirect(url_for('profile', id=id))

		student.deactivate()
		logout_user()
		session.pop('userID')
		return redirect(url_for('index'))

	@app.route('/sharing', methods=['POST'])
	def toggleSharing():
		database = db.Database()

		student, studentID = get_session_student(database, session)
		if type(student) == int:
			abort(student)

		cur_sharing = student.is_sharing()
		student.set_sharing(not cur_sharing)
		if cur_sharing:
			flash('You are no longer sharing your position.')
		else:
			flash('Your location will now be shared.')
		return redirect(request.referrer)

	@app.route('/invisible', methods=['POST'])
	def toggleInvisible():
		userID = session.get('userID')
		if (userID is None):
			return redirect(url_for('auth.login'))
		database = db.Database()
		student = database.get_student(int(userID))
		if student is None:
			return redirect(url_for('auth.login'))

		curr = student.is_invisible()
		student.set_invisible(not curr)

		# When a user disables invisible, do not let them immediately share their location
		if curr:
			student.set_sharing(False)

		if curr:
			flash('You are no longer invisible.')
		else:
			flash('You have set yourself invisible. Other users will see you as offline.')
		return redirect(request.referrer)

	@app.route('/settings', methods=['GET'])
	def settings():
		database = db.Database()
		student, studentID = get_session_student(database, session)
		if type(student) == int:
			abort(student)
		return render_template_wrapper('settings.html', id=studentID)

	@app.route('/submitSettings', methods=['POST'])
	def submitSettings():
		database = db.Database()
		student, studentID = get_session_student(database, session)
		if type(student) == int:
			abort(student)

		settings = request.json
		student.set_settings_json(json.dumps(settings))
		return "200", 200