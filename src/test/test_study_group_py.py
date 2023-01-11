import unittest

from scholasticate.database import Database
from scholasticate.location import Location

def to_ids(in_array):
	out_array = []
	for i in in_array:
		out_array.append(i.get_id())
	return out_array

class Test_study_group_py(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)
		self.studenta = self.database.get_student(1)
		self.studentb = self.database.get_student(2)
		self.study_group = self.studenta.get_study_groups()[0]

	def test_create_study_group(self):
		new_study_group = self.database.create_study_group(self.database.get_course(1), Location(10, 20), "New study Group", 5)
		self.assertEqual(self.database.get_study_group(new_study_group.get_id()), new_study_group)
		self.assertEqual(new_study_group.get_course(), self.database.get_course(1))
		self.assertEqual(new_study_group.get_location(), Location(10, 20))
		self.assertEqual(new_study_group.get_name(), "New study Group")
		self.assertEqual(new_study_group.get_description(), "")#default is empty string
		self.assertEqual(new_study_group.get_schedule(), "")#default is empty string

	def test_get_id(self):
		self.assertEqual(self.study_group.get_id(), 1)

	def test_getset_public(self):
		self.assertEqual(self.study_group.get_public(), True)
		self.study_group.set_public(False)
		self.assertEqual(self.study_group.get_public(), False)

	def test_getset_name(self):
		self.assertEqual(self.study_group.get_name(), 'CS 307 Group')
		self.study_group.set_name('Party Group!!!')
		self.assertEqual(self.study_group.get_name(), 'Party Group!!!')

	def test_getset_description(self):
		self.assertEqual(self.study_group.get_description(), 'Group for studying for Software Engineering')
		self.study_group.set_description('Group for partying!!')
		self.assertEqual(self.study_group.get_description(), 'Group for partying!!')

	def test_getset_course(self):
		self.assertEqual(self.study_group.get_course(), self.database.get_course(1))
		self.study_group.set_course(self.database.get_course(2))
		self.assertEqual(self.study_group.get_course(), self.database.get_course(2))

	def test_getset_schedule(self):
		self.assertEqual(self.study_group.get_schedule(), 'Every tuesday')
		self.study_group.set_schedule('Everyday, bro!')
		self.assertEqual(self.study_group.get_schedule(), 'Everyday, bro!')

	def test_getset_location(self):
		self.assertEqual(self.study_group.get_location(), Location(40.427528179812505, -86.91317399046419))
		self.study_group.set_location(Location(123, 456))
		self.assertEqual(self.study_group.get_location(), Location(123, 456))

	def test_isset_member(self):
		self.assertTrue(self.study_group.is_member(self.studenta))
		self.assertTrue(self.study_group.is_member(self.studentb))
		self.study_group.remove_member(self.studentb)
		self.assertFalse(self.study_group.is_member(self.studentb))
		self.study_group.add_member(self.studentb)
		self.study_group.add_member(self.studentb)#second time shouldn't do anything
		self.assertTrue(self.study_group.is_member(self.studentb))

	def test_is_owner(self):
		self.assertTrue(self.study_group.is_owner(self.studenta))
		self.assertFalse(self.study_group.is_owner(self.studentb))
		self.study_group.set_owner(self.studentb)
		self.assertTrue(self.study_group.is_owner(self.studentb))
		self.study_group.set_owner(self.studenta)
		self.assertFalse(self.study_group.is_owner(self.studentb))

	def test_get_members(self):
		self.assertEqual(to_ids(self.study_group.get_members()), [1, 2])

	def test_delete(self):
		self.assertEqual(self.studenta.get_study_groups(), [self.study_group])
		self.assertTrue(self.studenta.is_in_study_group(self.study_group))
		self.study_group.delete()
		self.assertEqual(self.studenta.get_study_groups(), [])
		self.assertFalse(self.studenta.is_in_study_group(self.study_group))

