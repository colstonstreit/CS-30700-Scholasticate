import json
from scholasticate.location import Location
from scholasticate.student import Account_Status

class School:
	def __init__(self, database, school_id):
		self.database = database
		self.school_id = school_id

	def __eq__(self, other):
		return self.school_id == other.school_id

	def serialize(self):
		result = self.database.conn.execute('SELECT * FROM schools WHERE school_id = ?', (self.school_id,)).fetchone()
		if result is None:
			return "[]"
		return json.dumps(dict(result))

	def get_id(self):
		return self.school_id

	def get_name(self):
		result = self.database.conn.execute('SELECT name FROM schools WHERE school_id = ?', (self.school_id,)).fetchone()
		return result['name']

	def get_location(self):
		result = self.database.conn.execute('SELECT latitude, longitude FROM schools WHERE school_id = ?', (self.school_id,)).fetchone()
		return Location(result['latitude'], result['longitude'])

	def get_courses(self):
		courses = self.database.conn.execute('SELECT course_id FROM courses WHERE school_id = ?', (self.school_id,)).fetchall()

		output = []
		for i in courses:
			output.append(self.database.get_course(i['course_id']))

		return output

	def search_courses(self, search_term):
		courses = self.database.conn.execute("SELECT * FROM courses WHERE school_id = ? AND (LOWER(course_name) LIKE ? OR LOWER(course_title) LIKE ?) LIMIT 25", (self.school_id, '%' + search_term.lower() + '%', '%' + search_term.lower() + '%')).fetchall()

		output = []
		for i in courses:
			output.append(self.database.get_course(i['course_id']))

		return output

	def get_majors(self):
		majors = self.database.conn.execute('SELECT major_id FROM majors WHERE school_id = ?', (self.school_id,)).fetchall()

		output = []
		for i in majors:
			output.append(self.database.get_major(i['major_id']))

		return output

	def get_students(self):
		students = self.database.conn.execute('SELECT student_id FROM students WHERE school_id = ? AND account_status = ?', (self.school_id, Account_Status.NORMAL)).fetchall()

		output = []
		for i in students:
			s = self.database.get_student(i['student_id'])
			if s is not None:
				output.append(s)

		return output

