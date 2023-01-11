import json
from flask import render_template, request, url_for, redirect, session, flash
from flask_login import logout_user
import scholasticate.database as db
from scholasticate.util import getUsefulUserInformation, render_template_wrapper
from scholasticate.course import Course
from scholasticate.util import name_validity_check

def route(app):

	@app.route('/search', methods=['GET'])
	def search():

		query = request.args.get("query").strip()

		if not query:
			return render_template_wrapper("search.html")

		database = db.Database()
		if (query == "*"):
			query = ""

		ret_students = []
		ret_courses = []
		ret_groups = []

		students = database.search_student(query)
		if students is not None:
			for i in students:
				ret_students.append(json.loads(i.serialize()))

		courses = database.search_course(query)
		if courses is not None:
			for i in courses:
				ret_courses.append(json.loads(i.serialize()))

		groups = database.search_group(query)
		if groups is not None:
			for i in groups:
				ret_groups.append(json.loads(i.serialize()))

		return render_template_wrapper("search.html", query=query, students=json.dumps(ret_students), courses=json.dumps(ret_courses), groups=json.dumps(ret_groups))