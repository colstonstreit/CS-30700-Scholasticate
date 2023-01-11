import unittest
import sqlite3

from scholasticate.database import Database

class Test_friend_request(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)

	def test_create_friend_request(self):
		sender = self.database.get_student(1)
		recipient = self.database.get_student(2)

		new_request = self.database.create_friend_request(sender, recipient)

		self.assertEqual(self.database.get_friend_request(new_request.get_id()), new_request)
		self.assertEqual(new_request.get_sender(), sender)
		self.assertEqual(new_request.get_recipient(), recipient)

	def test_friend_request_unique(self):
		sender = self.database.get_student(1)
		recipient = self.database.get_student(2)

		request1 = self.database.create_friend_request(sender, recipient)

		# This should fail the UNIQUE constraint
		with self.assertRaises(sqlite3.IntegrityError):
			request2 = self.database.create_friend_request(sender, recipient)

		# This should NOT fail the constraint
		request3 = self.database.create_friend_request(recipient, sender)