import unittest

from scholasticate.database import Database
from scholasticate.school import School
from scholasticate.location import Location

def to_names(in_array):
	out_array = []
	for i in in_array:
		out_array.append(i.get_name())
	return out_array

class Test_school_py(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)
	
	def test_get_id(self):
		self.assertEqual(self.database.get_school(1).get_id(), 1)
	
	def test_get_name(self):
		self.assertEqual(self.database.get_school(1).get_name(), 'Purdue University')
	
	def test_get_location(self):
		self.assertEqual(self.database.get_school(1).get_location(), Location(40.42397490770524, -86.92118923770037))
	
	def test_get_all_schools(self):
		self.assertEqual(to_names(self.database.get_all_schools()), ['Purdue University'])
	


