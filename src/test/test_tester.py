import unittest

class Test_tester(unittest.TestCase):
	def test_assert(self):
		self.assertTrue(1 == 1)
		self.assertFalse(1 == 0)
	
