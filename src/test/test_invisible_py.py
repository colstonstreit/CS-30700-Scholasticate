import unittest
import sqlite3

from scholasticate.database import Database
from scholasticate.location import Location
from scholasticate.student import Student

class Test_invisible(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)

	def test_get_online_students(self):
		student1 = self.database.get_student(1)
		student2 = self.database.get_student(2)

		# Neither student has a valid location
		self.assertEqual(self.database.get_online_students(), [])

		# student1 should be considered online now
		student1.set_location(Location(1, 1))
		self.assertEqual(self.database.get_online_students(), [student1])

		# student1 should not show up when they set themselves to be invisible
		student1.set_invisible(True)
		self.assertEqual(self.database.get_online_students(), [])

		# By including ourselves in get_online_students, it will always include our position if it exists
		self.assertEqual(self.database.get_online_students(student1), [student1])

		student2.set_location(Location(1, 2))
		student1.set_invisible(False)
		self.assertEqual(self.database.get_online_students(), [student1, student2])