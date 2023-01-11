import unittest
import tempfile, os, sqlite3
from scholasticate.web import run_website
from flask import current_app

class Test_flask(unittest.TestCase):
	def setUp(self):
		app = run_website(config={'DATABASE_IN_MEMORY': True, 'SECRET_KEY': "test", 'TESTING': True}, run=False)
		self.client = app.test_client()
	
	def test_basic(self):
		rv = self.client.get('/')
		self.assertEqual(rv.status, '200 OK')
	
	def test_profile(self):

		# John Purdue
		rv = self.client.get('profile/1')
		self.assertEqual(rv.status, '200 OK')

		# Throw 404 error if not found
		rv = self.client.get('profile/5')
		self.assertEqual(rv.status, '404 NOT FOUND')

	def test_profile_edit(self):

		# Throw 403 if we try editing without logging in
		rv = self.client.get('profile/1/edit')
		self.assertEqual(rv.status, '403 FORBIDDEN')

	def test_course(self):

		rv = self.client.get('course/1')
		self.assertEqual(rv.status, '200 OK')
		self.assertIn(b'CS 307', rv.data)
		self.assertIn(b'Software Engineering I', rv.data)
		self.assertIn(b'Xiangyu Zhang', rv.data)
		self.assertIn(b'John Purdue', rv.data)
		self.assertIn(b'CS 307 Group', rv.data)

	def test_search(self):

		rv = self.client.get('search?query=john')
		self.assertIn(b'John Purdue', rv.data)

		rv = self.client.get('search?query=307')
		self.assertIn(b'Software Engineering I', rv.data)