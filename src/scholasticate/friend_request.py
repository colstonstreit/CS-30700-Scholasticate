import json

class Friend_Request:
	def __init__(self, database, friend_request_id):
		self.database = database
		self.friend_request_id = friend_request_id

	def __eq__(self, other):
		return self.friend_request_id == other.friend_request_id

	def serialize(self):
		result = self.database.conn.execute('SELECT * FROM friend_requests WHERE friend_request_id = ?', (self.get_id(),)).fetchone()
		if result is None:
			return "[]"
		return json.dumps(dict(result))

	def get_id(self):
		return self.friend_request_id

	def get_sender(self):
		result = self.database.conn.execute('SELECT sender_student_id FROM friend_requests WHERE friend_request_id = ?', (self.get_id(),)).fetchone()
		return self.database.get_student(result['sender_student_id'])

	def get_recipient(self):
		result = self.database.conn.execute('SELECT recipient_student_id FROM friend_requests WHERE friend_request_id = ?', (self.get_id(),)).fetchone()
		return self.database.get_student(result['recipient_student_id'])

	def delete(self):
		self.database.conn.execute('DELETE FROM friend_requests WHERE friend_request_id = ?', (self.get_id(), ))
		self.database.conn.commit()