import json

class Course:
	def __init__(self, database, course_id):
		self.database = database
		self.course_id = course_id

	def __eq__(self, other):
		return self.course_id == other.course_id

	def serialize(self):
		result = self.database.conn.execute('SELECT * FROM courses WHERE course_id = ?', (self.course_id,)).fetchone()
		if result is None:
			return "[]"
		return json.dumps(dict(result))

	def get_id(self):
		return self.course_id

	def get_name(self):
		result = self.database.conn.execute('SELECT course_name FROM courses WHERE course_id = ?', (self.course_id,)).fetchone()
		return result['course_name']
	
	def get_title(self):
		result = self.database.conn.execute('SELECT course_title FROM courses WHERE course_id = ?', (self.course_id,)).fetchone()
		return result['course_title']

	def get_professor_name(self):
		result = self.database.conn.execute('SELECT professor_name FROM courses WHERE course_id = ?', (self.course_id,)).fetchone()
		return result['professor_name']

	def get_school(self):
		result = self.database.conn.execute('SELECT school_id FROM courses WHERE course_id = ?', (self.course_id,)).fetchone()
		return self.database.get_school(result['school_id'])