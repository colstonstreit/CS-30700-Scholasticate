import unittest
import scraper.__main__ as scraper

def utilCreateCourse(name, professor, title):
	output = scraper.CourseListing()
	output.name = name
	output.professor = professor
	output.title = title
	return output

class Test_scraper_pr(unittest.TestCase):
	def test_deduplicateCourses(self):
		testInput = [
			utilCreateCourse("AAA 10000", "John A. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 10000", "John A. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 10000", "John B. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 20000", "John A. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 10000", "John A. Smith", "Least Boring Class")
		]
		
		expected = [
			utilCreateCourse("AAA 10000", "John A. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 10000", "John B. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 20000", "John A. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 10000", "John A. Smith", "Least Boring Class")
		]
		
		self.assertEqual(scraper.deduplicateCourses(testInput), expected)
	
	def test_combineCourses(self):
		testInput = [
			utilCreateCourse("AAA 10000", "John A. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 10000", "John B. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 20000", "John A. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 10000", "John A. Smith", "Least Boring Class")
		]
		
		expected = [
			utilCreateCourse("AAA 10000", "John A. Smith\nJohn B. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 20000", "John A. Smith", "Most Boring Class"),
			utilCreateCourse("AAA 10000", "John A. Smith", "Least Boring Class")
		]
		
		self.assertEqual(scraper.combineCourses(testInput), expected)
		
