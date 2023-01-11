import json
from scholasticate.location import Location

class Study_group:
	def __init__(self, database, study_group_id):
		self.database = database
		self.study_group_id = study_group_id

	def __eq__(self, other):
		return self.study_group_id == other.study_group_id

	def serialize(self):
		result = self.database.conn.execute('SELECT * FROM study_groups WHERE study_group_id = ?', (self.study_group_id,)).fetchone()
		if result is None:
			return "[]"
		result = dict(result)
		course = self.database.get_course(result['course_id'])
		if course is not None:
			result['course'] = json.loads(course.serialize())
		return json.dumps(result)

	def get_id(self):
		return self.study_group_id

	def get_public(self):
		result = self.database.conn.execute('SELECT public FROM study_groups WHERE study_group_id = ?', (self.study_group_id,)).fetchone()
		return result['public']

	def is_public(self):
		return self.get_public()

	def set_public(self, public):
		self.database.conn.execute('UPDATE study_groups SET public = ? WHERE study_group_id = ?', (public, self.get_id()))
		self.database.conn.commit()

	def get_name(self):
		result = self.database.conn.execute('SELECT name FROM study_groups WHERE study_group_id = ?', (self.study_group_id,)).fetchone()
		return result['name']

	def set_name(self, name):
		self.database.conn.execute('UPDATE study_groups SET name = ? WHERE study_group_id = ?', (name, self.get_id()))
		self.database.conn.commit()

	def get_description(self):
		result = self.database.conn.execute('SELECT description FROM study_groups WHERE study_group_id = ?', (self.study_group_id,)).fetchone()
		return result['description']

	def set_description(self, description):
		self.database.conn.execute('UPDATE study_groups SET description = ? WHERE study_group_id = ?', (description, self.get_id()))
		self.database.conn.commit()

	def get_course(self):
		result = self.database.conn.execute('SELECT course_id FROM study_groups WHERE study_group_id = ?', (self.study_group_id,)).fetchone()
		return self.database.get_course(result['course_id'])

	def set_course(self, course):
		self.database.conn.execute('UPDATE study_groups SET course_id = ? WHERE study_group_id = ?', (course.get_id(), self.get_id()))
		self.database.conn.commit()

	def get_schedule(self):
		result = self.database.conn.execute('SELECT schedule FROM study_groups WHERE study_group_id = ?', (self.study_group_id,)).fetchone()
		return result['schedule']

	def set_schedule(self, schedule):
		self.database.conn.execute('UPDATE study_groups SET schedule = ? WHERE study_group_id = ?', (schedule, self.get_id()))
		self.database.conn.commit()

	def get_location(self):
		result = self.database.conn.execute('SELECT latitude, longitude FROM study_groups WHERE study_group_id = ?', (self.study_group_id,)).fetchone()
		return Location(result['latitude'], result['longitude'])

	def set_location(self, location):
		self.database.conn.execute('UPDATE study_groups SET latitude = ?, longitude = ? WHERE study_group_id = ?', (location.latitude, location.longitude, self.get_id()))
		self.database.conn.commit()

	def get_owner(self):
		result = self.database.conn.execute('SELECT student_id FROM study_group_members WHERE study_group_id = ? AND owner = TRUE', (self.study_group_id,)).fetchone()
		return self.database.get_student(result['student_id'])

	def is_owner(self, student):
		result = self.database.conn.execute('SELECT COUNT(*) FROM study_group_members WHERE study_group_id = ? AND owner = TRUE AND student_id = ?', (self.study_group_id, student.get_id())).fetchone()
		return result[0] == 1

	def set_owner(self, student):
		self.database.conn.execute('UPDATE study_group_members SET owner = ? WHERE study_group_id = ? AND student_id = ?', (True, self.get_id(), student.get_id()))
		self.database.conn.execute('UPDATE study_group_members SET owner = ? WHERE study_group_id = ? AND student_id <> ?', (False, self.study_group_id, student.get_id()))
		self.database.conn.commit()

	def is_member(self, student):
		result = self.database.conn.execute('SELECT COUNT(*) FROM study_group_members WHERE study_group_id = ? AND student_id = ?', (self.study_group_id, student.get_id())).fetchone()
		return result[0] == 1

	def add_member(self, student):
		self.database.conn.execute('INSERT INTO study_group_members(study_group_id, student_id, owner) VALUES(?, ?, FALSE) ON CONFLICT DO NOTHING', (self.get_id(), student.get_id()))
		self.database.conn.commit()

	def remove_member(self, student):
		self.database.conn.execute('DELETE FROM study_group_members WHERE study_group_id = ? AND student_id = ?', (self.get_id(), student.get_id()))
		self.database.conn.commit()

	def get_members(self):
		students = self.database.conn.execute('SELECT student_id FROM study_group_members WHERE study_group_id = ?', (self.study_group_id, )).fetchall()

		output = []
		for i in students:
			s = self.database.get_student(i['student_id'])
			if s is not None:
				output.append(s)

		return output

	def get_max_members(self):
		result = self.database.conn.execute('SELECT max_members FROM study_groups WHERE study_group_id = ?', (self.study_group_id, )).fetchone()
		return result['max_members']

	def set_max_members(self, max_members):
		self.database.conn.execute('UPDATE study_groups SET max_members = ? WHERE study_group_id = ?', (max_members, self.get_id()))
		self.database.conn.commit()

	def get_conversation(self):
		messages = self.database.conn.execute('SELECT group_message_id FROM group_messages WHERE (study_group_id = ?) ORDER BY time_sent', (self.get_id(), ))

		output = []
		for i in messages:
			output.append(self.database.get_group_message(i['group_message_id']))

		return output

	def delete(self):
		self.database.conn.execute('DELETE FROM study_groups WHERE study_group_id = ?', (self.get_id(), ))
		self.database.conn.execute('DELETE FROM study_group_invitations WHERE study_group_id = ?', (self.get_id(), ))
		self.database.conn.execute('DELETE FROM study_group_members WHERE study_group_id = ?', (self.get_id(), ))
		self.database.conn.commit()
