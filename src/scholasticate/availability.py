import json

class Availability:
	def __init__(self, database, time_id):
		self.database = database
		self.time_id = time_id

	def __eq__(self, other):
		return self.time_id == other.time_id
    
	def serialize(self):
		result = self.database.conn.execute('SELECT * FROM time_availability WHERE time_id = ?', (self.time_id,)).fetchone()
		if result is None:
			return "[]"
		return json.dumps(dict(result))
    
	def get_id(self):
		return self.time_id
    
	def get_weekday(self):
		result = self.database.conn.execute('SELECT weekday FROM time_availability WHERE time_id = ?', (self.time_id,)).fetchone()
		return result['weekday']
    
	def get_start_time(self):
		result = self.database.conn.execute('SELECT start_time FROM time_availability WHERE time_id = ?', (self.time_id,)).fetchone()
		return result['start_time']
    
	def get_end_time(self):
		result = self.database.conn.execute('SELECT end_time FROM time_availability WHERE time_id = ?', (self.time_id,)).fetchone()
		return result['end_time']
