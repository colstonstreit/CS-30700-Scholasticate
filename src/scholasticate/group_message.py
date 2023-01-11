import json
from scholasticate.location import Location

class Group_message:
	def __init__(self, database, group_message_id):
		self.database = database
		self.group_message_id = group_message_id

	def __eq__(self, other):
		return self.group_message_id == other.group_message_id

	def serialize(self):
		result = self.database.conn.execute('SELECT * FROM group_messages WHERE group_message_id = ?', (self.get_id(),)).fetchone()
		if result is None:
			return "[]"
		return json.dumps(dict(result))

	def get_id(self):
		return self.group_message_id

	def get_sender(self):
		result = self.database.conn.execute('SELECT sender_student_id FROM group_messages WHERE group_message_id = ?', (self.get_id(),)).fetchone()
		return self.database.get_student(result['sender_student_id'])

	def get_study_group(self):
		result = self.database.conn.execute('SELECT study_group_id FROM group_messages WHERE group_message_id = ?', (self.get_id(),)).fetchone()
		return self.database.get_study_group(result['study_group_id'])

	def get_message(self):
		result = self.database.conn.execute('SELECT message FROM group_messages WHERE group_message_id = ?', (self.get_id(),)).fetchone()
		return result['message']

	def get_time_sent(self):
		result = self.database.conn.execute('SELECT time_sent FROM group_messages WHERE group_message_id = ?', (self.get_id(),)).fetchone()
		return result['time_sent']

	def get_read_student_ids(self):
		result = self.database.conn.execute('SELECT users_read_json FROM group_messages WHERE group_message_id = ?', (self.get_id(),)).fetchone()
		studentIds = json.loads(result['users_read_json'])
		return studentIds

	def delete(self): # Sets text to [deleted]
		self.database.conn.execute('UPDATE group_messages SET message = "" WHERE group_message_id = ?', (self.get_id(),))
		self.database.conn.commit()

