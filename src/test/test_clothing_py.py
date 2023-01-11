import unittest

from scholasticate.database import Database

class Test_clothing_py(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)
		self.studenta = self.database.get_student(1)
		self.studentb = self.database.get_student(2)
		self.clothinga = self.studenta.get_clothing()[0]
		self.clothingb = self.studentb.get_clothing()[0]
	
	def test_get_id(self):
		self.assertEqual(self.database.get_school(1).get_id(), 1)
	
	def test_get_article(self):
		self.assertEqual(self.clothinga.get_article(), 'shirt')
		self.assertEqual(self.clothingb.get_article(), 'hat')
			
	def test_get_brand(self):
		self.assertTrue(self.clothinga.get_brand() is None)
		self.assertEqual(self.clothingb.get_brand(), 'Nike')
	
	def test_get_color(self):
		self.assertEqual(self.clothinga.get_color(), (120, 20, 0))
		self.assertEqual(self.clothingb.get_color(), (255, 255, 0))
