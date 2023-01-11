import unittest

from scholasticate.database import Database
from scholasticate.location import Location
from scholasticate.course import Course

class Test_student_py(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)
		self.student = self.database.get_student(1)
	
	def test_create_student(self):
		new_student = self.database.create_student("email@email.com", "password1", "John Smith", self.database.get_school(1))
		self.assertEqual(new_student.get_email(), "email@email.com")
		self.assertEqual(new_student.get_hashpw(), "password1")
		self.assertEqual(new_student.get_name(), "John Smith")
		self.assertEqual(new_student.get_school(), self.database.get_school(1))
	
	def test_get_email(self):
		self.assertEqual(self.student.get_email(), "jpurdue@purdue.edu")
	
	def test_getset_hashpw(self):
		self.assertEqual(self.student.get_hashpw(), "XXXX")
		self.student.set_hashpw("YYYY")
		self.assertEqual(self.student.get_hashpw(), "YYYY")
	
	def test_getset_name(self):
		self.assertEqual(self.student.get_name(), "John Purdue")
		self.student.set_name("Not John")
		self.assertEqual(self.student.get_name(), "Not John")
	
	def test_get_school(self):
		self.assertEqual(self.student.get_school(), self.database.get_school(1))
	
	def test_getset_bio(self):
		self.assertEqual(self.student.get_bio(), "This is my school! he/him/his")
		self.student.set_bio("Off my lawn!")
		self.assertEqual(self.student.get_bio(), "Off my lawn!")
	
	def test_getset_location(self):
		self.assertEqual(self.student.get_location(), None)
		self.student.set_location(Location(1, 2))
		self.assertEqual(self.student.get_location(), Location(1, 2))
	
	def test_getset_location_last_updated(self):
		self.assertEqual(self.student.get_location_last_updated(), None)
		self.student.set_location_last_updated(101239)
		self.assertEqual(self.student.get_location_last_updated(), 101239)
	
	def test_getset_current_courses(self):
		self.assertEqual(self.student.get_current_courses(), [self.database.get_course(1)])
		self.student.add_current_course(self.database.get_course(2))
		self.student.add_current_course(self.database.get_course(2))#second one shouldn't do anything
		self.assertEqual(self.student.get_current_courses(), [self.database.get_course(1), self.database.get_course(2)])
		self.student.remove_current_course(self.database.get_course(2))
		self.assertEqual(self.student.get_current_courses(), [self.database.get_course(1)])
		
	def test_getset_past_courses(self):
		self.assertEqual(self.student.get_past_courses(), [])
		self.student.add_past_course(self.database.get_course(2))
		self.student.add_past_course(self.database.get_course(2))#second one shouldn't do anything
		self.assertEqual(self.student.get_past_courses(), [self.database.get_course(2)])
		self.student.remove_past_course(self.database.get_course(2))
		self.assertEqual(self.student.get_past_courses(), [])
	
	def test_getset_friends(self):
		self.assertEqual(self.student.get_friends(), [self.database.get_student(2)])
		self.student.remove_friend(self.database.get_student(2))
		self.assertEqual(self.student.get_friends(), [])
		self.student.add_friend(self.database.get_student(2))
		self.student.add_friend(self.database.get_student(2)) #second one shouldn't do anything
		self.assertEqual(self.student.get_friends(), [self.database.get_student(2)])
	
	def test_getset_blocked(self):
		self.assertEqual(self.student.get_blockeds(), [])
		self.student.add_blocked(self.database.get_student(2))
		self.assertEqual(self.student.get_blockeds(), [self.database.get_student(2)])
		self.student.remove_blocked(self.database.get_student(2))
		self.assertEqual(self.student.get_blockeds(), [])

	def test_getset_accepted_users(self):
		self.assertEqual(self.student.get_accepted_users(), [])
		self.student.add_accepted(self.database.get_student(2))
		self.assertEqual(self.student.get_accepted_users(), [self.database.get_student(2)])
		self.student.remove_accepted(self.database.get_student(2))
		self.assertEqual(self.student.get_accepted_users(), [])
	
	def test_getset_clothing(self):
		self.assertEqual(self.student.get_clothing(), [self.database.get_clothing(1)])
		clothing = self.student.add_clothing("pants", "PINK", (120, 140, 50))
		self.assertEqual(self.student.get_clothing(), [self.database.get_clothing(1), clothing])
		clothing.delete()
		self.assertEqual(self.student.get_clothing(), [self.database.get_clothing(1)])
	
	def test_get_study_groups(self):
		self.assertEqual(self.student.get_study_groups(), [self.database.get_study_group(1)])
	
	def test_deactivate(self):
		self.student.deactivate()

		self.assertEqual(self.student.is_deactivated(), True)
		self.assertEqual(self.student.get_name(), "")
		self.assertEqual(self.student.get_email(), str(self.student.get_id()))

	def test_get_students_with_course(self):
		# student2 has course 1 as a past course
		student2 = self.database.get_student(2)

		# student2 should not show up
		self.assertEqual(self.database.get_students_with_course(1, True), [self.student])

		# student2 *should* show up
		self.assertEqual(self.database.get_students_with_course(1, False), [self.student, student2])
		
