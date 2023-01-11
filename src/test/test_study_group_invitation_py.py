import unittest
import sqlite3

from scholasticate.database import Database

class Test_study_group_invitation_py(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)
	
	def test_create_study_group_invitation(self):
		group = self.database.get_study_group(1)
		sender = self.database.get_student(1)
		recipient = self.database.get_student(2)

		new_invite = self.database.create_study_group_invitation(group, sender, recipient)

		self.assertEqual(self.database.get_study_group_invitation(new_invite.get_id()), new_invite)
		self.assertEqual(new_invite.get_study_group(), group)
		self.assertEqual(new_invite.get_sender(), sender)
		self.assertEqual(new_invite.get_recipient(), recipient)

	def test_study_group_invitation_unique(self):
		group = self.database.get_study_group(1)
		sender = self.database.get_student(1)
		recipient = self.database.get_student(2)

		invite1 = self.database.create_study_group_invitation(group, sender, recipient)

		# This should fail the UNIQUE constraint
		with self.assertRaises(sqlite3.IntegrityError):
			invite2 = self.database.create_study_group_invitation(group, sender, recipient)
		
		# This should NOT fail the constraint
		invite3 = self.database.create_study_group_invitation(group, recipient, sender)