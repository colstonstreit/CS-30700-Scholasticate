import unittest

from scholasticate.location import Location
from scholasticate.database import Database
import random

class Test_Distance_Sorting(unittest.TestCase):

	def setUp(self):
		self.database = Database(in_memory=True)
		self.student = self.database.create_student(str(100), "", "", self.database.get_school(1))
		self.student.set_location(Location(0, 0))
		self.studentList = []
		for i in range(50):
			s = self.database.create_student(str(i),"","", self.database.get_school(1))
			s.set_location(Location(random.random() * 160 - 80, random.random() * 360 - 180))
			self.studentList.append(s)

			group = self.database.create_study_group(self.database.get_course(1), Location(random.random() * 160 - 80, random.random() * 360 - 180), str(i), 5)
			self.studentList.append(group)


	def test_ascending(self):
		distances = self.student.calculateRelativeDistances(self.studentList)
		for i in range(len(self.studentList) - 1):
			# distances[i][0] is the student JSON, and distances[i][1] is the distance
			self.assertTrue(distances[i]["distance"] <= distances[i + 1]["distance"])

