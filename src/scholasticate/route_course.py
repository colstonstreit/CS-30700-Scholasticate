import json
from flask import render_template, request, url_for, redirect, session, flash
from flask_login import logout_user
import scholasticate.database as db
from scholasticate.util import getUsefulUserInformation, render_template_wrapper
from scholasticate.course import Course

def route(app):

	@app.route('/course/<id>', methods=['GET'])
	def course(id):
		userID = session.get('userID')
		if userID is None:
			userID = "0"
		else:
			userID = userID

		database = db.Database()
		thisCourse = database.get_course(int(id))
		if thisCourse is None:
			flash("That course does not exist!")
			return redirect(url_for('index'))

		students = []
		for student in database.get_students_with_course(int(id)):
			students.append(json.loads(student.serialize()))

		groups = []
		pgroups_id = {}
		pgroups = []
		
		# Prioritize private groups the user is in (if logged in)
		thisStudent = database.get_student(int(userID))
		if thisStudent:
			for group in thisStudent.get_study_groups():
				if not group.is_public():
					pgroups.append(json.loads(group.serialize()))
					pgroups_id[group.get_id()] = True

		for group in database.get_public_study_groups():
			if group.get_id() not in pgroups_id:
				groups.append(json.loads(group.serialize()))

		return render_template_wrapper('course.html', courseInfo=thisCourse.serialize(), students=json.dumps(students), groups=json.dumps(groups), pgroups=json.dumps(pgroups))
	
	@app.route('/searchCourses/<search_term>', methods=['GET'])
	def searchCourses(search_term):
		database = db.Database()
		
		courseList = []
		for course in database.get_school(1).search_courses(search_term):
			courseList.append(json.loads(course.serialize()))
		
		return json.dumps(courseList)
	
