import unittest

from scholasticate.database import Database

class Test_group_message_py(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)
	
	def test_group_messages(self):
		studenta = self.database.get_student(1)
		studentb = self.database.get_student(2)
		group = self.database.get_study_group(1)
		
		self.assertEqual(group.get_conversation(), [])
		
		messagea = self.database.create_group_message(studenta, group, "Hello, studentb! I am studenta.", 1)
		self.assertEqual(self.database.get_group_message(messagea.get_id()), messagea)
		self.assertEqual(messagea.get_sender(), studenta)
		self.assertEqual(messagea.get_study_group(), group)
		self.assertEqual(messagea.get_message(), "Hello, studentb! I am studenta.")
		self.assertEqual(messagea.get_time_sent(), 1)
		
		self.assertEqual(group.get_conversation(), [messagea])
		
		messageb = self.database.create_group_message(studentb, group, "Nice to meet you.", 2)
		self.assertEqual(self.database.get_group_message(messageb.get_id()), messageb)
		self.assertEqual(messageb.get_sender(), studentb)
		self.assertEqual(messageb.get_study_group(), group)
		self.assertEqual(messageb.get_message(), "Nice to meet you.")
		self.assertEqual(messageb.get_time_sent(), 2)
		
		self.assertEqual(group.get_conversation(), [messagea, messageb])
		
	
