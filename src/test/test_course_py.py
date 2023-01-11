import unittest

from scholasticate.database import Database

class Test_course_py(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)
		self.course1 = self.database.get_course(1)
		self.course2 = self.database.get_course(2)

	def test_get_name(self):
		self.assertEqual(self.course1.get_name(), "CS 307")
		self.assertEqual(self.course2.get_name(), "CS 352")
	
	def test_get_title(self):
		self.assertEqual(self.course1.get_title(), "Software Engineering I")
		self.assertEqual(self.course2.get_title(), "Compilers: Principles and Practice")
	
	def test_get_professor_name(self):
		self.assertEqual(self.course1.get_professor_name(), "Xiangyu Zhang")
		self.assertEqual(self.course2.get_professor_name(), "Zhiyuan Li")
	
	def test_get_school(self):
		self.assertEqual(self.course1.get_school(), self.database.get_school(1))
		self.assertEqual(self.course2.get_school(), self.database.get_school(1))
		
