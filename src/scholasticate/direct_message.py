import json
from scholasticate.location import Location

class Direct_message:
	def __init__(self, database, direct_message_id):
		self.database = database
		self.direct_message_id = direct_message_id

	def __eq__(self, other):
		return self.direct_message_id == other.direct_message_id

	def serialize(self):
		result = self.database.conn.execute('SELECT * FROM direct_messages WHERE direct_message_id = ?', (self.get_id(),)).fetchone()
		if result is None:
			return "[]"
		return json.dumps(dict(result))

	def get_id(self):
		return self.direct_message_id

	def get_sender(self):
		result = self.database.conn.execute('SELECT sender_student_id FROM direct_messages WHERE direct_message_id = ?', (self.get_id(),)).fetchone()
		return self.database.get_student(result['sender_student_id'])

	def get_recipient(self):
		result = self.database.conn.execute('SELECT recipient_student_id FROM direct_messages WHERE direct_message_id = ?', (self.get_id(),)).fetchone()
		return self.database.get_student(result['recipient_student_id'])

	def get_message(self):
		result = self.database.conn.execute('SELECT message FROM direct_messages WHERE direct_message_id = ?', (self.get_id(),)).fetchone()
		return result['message']

	def get_time_sent(self):
		result = self.database.conn.execute('SELECT time_sent FROM direct_messages WHERE direct_message_id = ?', (self.get_id(),)).fetchone()
		return result['time_sent']

	def is_unread(self):
		result = self.database.conn.execute('SELECT unread FROM direct_messages WHERE direct_message_id = ?', (self.get_id(),)).fetchone()
		return result['unread'] == 1

	def delete(self): # Sets text to empty which will be detected in JS and shown as [deleted]
		self.database.conn.execute('UPDATE direct_messages SET message = "" WHERE direct_message_id = ?', (self.get_id(),))
		self.database.conn.commit()
