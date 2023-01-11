import json

class Study_group_invitation:
	def __init__(self, database, study_group_invitation_id):
		self.database = database
		self.study_group_invitation_id = study_group_invitation_id

	def __eq__(self, other):
		return self.study_group_invitation_id == other.study_group_invitation_id

	def serialize(self):
		result = self.database.conn.execute('SELECT * FROM study_group_invitations WHERE study_group_invitation_id = ?', (self.get_id(),)).fetchone()
		if result is None:
			return "[]"
		return json.dumps(dict(result))

	def get_id(self):
		return self.study_group_invitation_id

	def get_study_group(self):
		result = self.database.conn.execute('SELECT study_group_id FROM study_group_invitations WHERE study_group_invitation_id = ?', (self.get_id(),)).fetchone()
		return self.database.get_study_group(result['study_group_id'])
	
	def get_sender(self):
		result = self.database.conn.execute('SELECT sender_student_id FROM study_group_invitations WHERE study_group_invitation_id = ?', (self.get_id(),)).fetchone()
		return self.database.get_student(result['sender_student_id'])
		
	def get_recipient(self):
		result = self.database.conn.execute('SELECT recipient_student_id FROM study_group_invitations WHERE study_group_invitation_id = ?', (self.get_id(),)).fetchone()
		return self.database.get_student(result['recipient_student_id'])
	
	def delete(self):
		self.database.conn.execute('DELETE FROM study_group_invitations WHERE study_group_invitation_id = ?', (self.get_id(), ))
		self.database.conn.commit()