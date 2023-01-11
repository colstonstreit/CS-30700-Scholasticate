import unittest
import sqlite3

from scholasticate.database import Database
from scholasticate.location import Location
from scholasticate.util import name_validity_check

class Test_name(unittest.TestCase):
	def setUp(self):
		self.database = Database(in_memory = True)
		self.cases = [
			
			# length
			("", "Name must be at least 2 characters long!"),
			("?", "Name must be at least 2 characters long!"),
			("hi every1 im new!!!!!!! holds up spork my name is katy but u can call me t3h PeNgU1N oF d00m!!!!!!!!", "Name must be no more than 64 characters long!"),
			
			# invisible unicode
			# you can't see them but trust me they're there
			# nasty little buggers
			("­­­­", "Name shouldn't contain invalid characters!"),
			("឴᠎‌‌​‍", "Name shouldn't contain invalid characters!"),
			("l‎m‏a‏o", "Name shouldn't contain invalid characters!"),

			# zalgotext
			# aka 2007-era copypasta
			("t̴́3҉h P͘eN͢gU͘͝1̸Ń̡̕ ͏͠o҉̕F̵̸ ̴͝d͟00̢͜m", "Name shouldn't contain invalid characters!"),
			("b̶̡͚̠̟̘̹̟͍̺̗̺̰͚̰̐̓̾̀̀̎̀̓̄̉́̎́͆̕ͅ", "Name shouldn't contain invalid characters!"),
		]

		self.validnames = ["Bobby", "Tim, the Enchanter", "朋友是一个坚韧不拔的纪录片", "?!?!?!?!?!", "Что бы Россия была Великая и Мощная!", "he", "love u❤️", "🍆💦🍑", "❤□△○"]

	def test_name_length(self):

		for case in self.cases:
			self.assertEqual(name_validity_check(case[0]), case[1])

		for case in self.validnames:
			self.assertEqual(name_validity_check(case), True)
	
	# Technically testing a python feature but ehhhh
	def test_whitespace_stripping(self):
		new_student = self.database.create_student("email@email.com", "password1", "   John ".strip(), self.database.get_school(1))
		self.assertEqual(new_student.get_name(), "John")