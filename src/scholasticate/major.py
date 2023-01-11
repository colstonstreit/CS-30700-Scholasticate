import json

class Major:
	def __init__(self, database, major_id):
		self.database = database
		self.major_id = major_id
	
	def __eq__(self, other):
		return self.major_id == other.major_id

	def serialize(self):
		result = self.database.conn.execute('SELECT * FROM majors WHERE major_id = ?', (self.major_id,)).fetchone()
		if result is None:
			return "[]"
		return json.dumps(dict(result))

	def get_id(self):
		return self.major_id
	
	def get_name(self):
		result = self.database.conn.execute('SELECT name FROM majors WHERE major_id = ?', (self.major_id,)).fetchone()
		return result['name']
	
	def get_school(self):
		result = self.database.conn.execute('SELECT school_id FROM majors WHERE major_id = ?', (self.major_id,)).fetchone()
		return self.database.get_school(result['school_id'])

