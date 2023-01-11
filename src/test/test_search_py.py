import unittest

from scholasticate.database import Database

class Test_search_py(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)
		self.studenta = self.database.get_student(1)
		self.studentb = self.database.get_student(2)
		self.course1 = self.database.get_course(1)
		self.course2 = self.database.get_course(2)
		self.course3 = self.database.get_course(3)
		self.course4 = self.database.get_course(4)

	def test_search_student(self):
		self.assertEqual(self.database.search_student("not-a-student"), [])

		# username
		self.assertEqual(self.database.search_student("John Purdue"), [self.studenta])
		self.assertEqual(self.database.search_student("mitch dan"), [self.studentb])
		self.assertEqual(self.database.search_student("DANIELS"), [self.studentb])

		# email
		self.assertEqual(self.database.search_student("mdaniel"), [self.studentb])
		self.assertEqual(self.database.search_student("@purdue.edu"), [self.studenta, self.studentb])

	def test_search_student_email(self):
		self.assertEqual(self.database.search_student_email("not-a-email"), [])

		# exact
		self.assertEqual(self.database.search_student_email("jpurdue@purdue.edu", True), [self.studenta])
		self.assertEqual(self.database.search_student_email("jpurdue", True), [])

		# partial
		self.assertEqual(self.database.search_student_email("mdaniels@purdue.edu", False), [self.studentb])
		self.assertEqual(self.database.search_student_email("daniels", False), [self.studentb])
		self.assertEqual(self.database.search_student_email("purdue.edu", False), [self.studenta, self.studentb])

	def test_search_course(self):
		self.assertEqual(self.database.search_course("PHYS"), [])
		self.assertEqual(self.database.search_course("CS 307"), [self.course1])
		self.assertEqual(self.database.search_course("compiler"), [self.course2])
		self.assertEqual(self.database.search_course("CS"), [self.course1, self.course2, self.course3, self.course4])
		self.assertEqual(self.database.search_course("Software Engineering"), [self.course1, self.course4])

	def test_search_group(self):
		group = self.database.get_study_group(1)
		self.assertEqual(self.database.search_group("CS 307 Group"), [group])
		self.assertEqual(self.database.search_group("GroupThatDoesnotexist"), [])