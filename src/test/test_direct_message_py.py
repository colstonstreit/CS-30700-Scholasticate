import unittest

from scholasticate.database import Database

class Test_direct_message_py(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)
	
	def test_direct_messages(self):
		studenta = self.database.get_student(1)
		studentb = self.database.get_student(2)
		
		self.assertEqual(studenta.get_conversations(), [])
		self.assertEqual(studentb.get_conversations(), [])
		self.assertEqual(studenta.get_unread_conversations(), [])
		self.assertEqual(studentb.get_unread_conversations(), [])
		self.assertEqual(studenta.get_conversation(studentb), [])#if the converastion doesn't even exist, then the list of messages in the conversation should be empty
		self.assertEqual(studentb.get_conversation(studenta), [])
		
		messagea = self.database.create_direct_message(studenta, studentb, "Hello, studentb! I am studenta.", 1)
		self.assertEqual(self.database.get_direct_message(messagea.get_id()), messagea)
		self.assertEqual(messagea.get_sender(), studenta)
		self.assertEqual(messagea.get_recipient(), studentb)
		self.assertEqual(messagea.get_message(), "Hello, studentb! I am studenta.")
		self.assertEqual(messagea.get_time_sent(), 1)
		
		self.assertEqual(studenta.get_conversations(), [studentb])
		self.assertEqual(studentb.get_conversations(), [studenta])
		self.assertEqual(studenta.get_unread_conversations(), [])
		self.assertEqual(studentb.get_unread_conversations(), [studenta])
		self.assertEqual(studenta.get_conversation(studentb), [messagea])
		self.assertEqual(studentb.get_conversation(studenta), [messagea])
		
		studenta.read_conversation(studentb)
		self.assertEqual(studenta.get_unread_conversations(), [])
		self.assertEqual(studentb.get_unread_conversations(), [studenta])
		studentb.read_conversation(studenta)
		self.assertEqual(studenta.get_unread_conversations(), [])
		self.assertEqual(studentb.get_unread_conversations(), [])
		
		
		messageb = self.database.create_direct_message(studentb, studenta, "Nice to meet you.", 2)
		self.assertEqual(self.database.get_direct_message(messageb.get_id()), messageb)
		self.assertEqual(messageb.get_sender(), studentb)
		self.assertEqual(messageb.get_recipient(), studenta)
		self.assertEqual(messageb.get_message(), "Nice to meet you.")
		self.assertEqual(messageb.get_time_sent(), 2)
		
		self.assertEqual(studenta.get_conversations(), [studentb])
		self.assertEqual(studentb.get_conversations(), [studenta])
		self.assertEqual(studenta.get_unread_conversations(), [studentb])
		self.assertEqual(studentb.get_unread_conversations(), [])
		self.assertEqual(studenta.get_conversation(studentb), [messagea, messageb])
		self.assertEqual(studentb.get_conversation(studenta), [messagea, messageb])
		
		studenta.read_conversation(studentb)
		self.assertEqual(studenta.get_unread_conversations(), [])
		self.assertEqual(studentb.get_unread_conversations(), [])
		studentb.read_conversation(studenta)
		self.assertEqual(studenta.get_unread_conversations(), [])
		self.assertEqual(studentb.get_unread_conversations(), [])
		
	
