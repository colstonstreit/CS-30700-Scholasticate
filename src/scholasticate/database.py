import sqlite3

import os, time
from scholasticate.friend_request import Friend_Request
from scholasticate.profile_picture import Profile_Picture
from scholasticate.school import School
from scholasticate.major import Major
from scholasticate.course import Course
from scholasticate.student import Student
from scholasticate.clothing import Clothing
from scholasticate.availability import Availability
from scholasticate.study_group import Study_group
from scholasticate.study_group_invitation import Study_group_invitation
from scholasticate.direct_message import Direct_message
from scholasticate.group_message import Group_message
from scholasticate.notification import Notification
from flask import current_app

class Database:
	def __init__(self, *, in_memory=False):
		if in_memory or current_app.config['DATABASE_IN_MEMORY']:
			self.conn = sqlite3.connect(':memory:')
			sqlFile = open(os.path.join(os.path.dirname(__file__), '../database.sql'))
			self.conn.executescript(sqlFile.read())
			sqlFile = open(os.path.join(os.path.dirname(__file__), '../test/test_data.sql'))
			self.conn.executescript(sqlFile.read())
			self.conn.commit()
			sqlFile.close()
		else:
			self.conn = sqlite3.connect(current_app.config['DATABASE'])
			# Run database.sql if there isn't anything yet
			if os.path.getsize(current_app.config['DATABASE']) == 0:
				sqlFile = open(os.path.join(os.path.dirname(__file__), '../database.sql'))
				self.conn.executescript(sqlFile.read())

		self.conn.row_factory = sqlite3.Row
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.conn.commit()

	def get_school(self, school_id):
		result = self.conn.execute('SELECT COUNT(*) FROM schools WHERE school_id = ?', (school_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return School(self, school_id)

	def get_all_schools(self):
		schools = self.conn.execute('SELECT * FROM schools').fetchall()

		output = []
		for i in schools:
			output.append(self.get_school(i['school_id']))

		return output

	def create_profile_picture(self, student, string):
		cursor = self.conn.cursor()
		cursor.execute('INSERT INTO profile_pictures(student_id, picture_string) VALUES(?, ?)', (student.get_id(), string))
		picture_id = cursor.lastrowid
		cursor.close()
		self.conn.commit()
		return self.get_profile_picture(picture_id)

	def get_profile_picture(self, picture_id):
		result = self.conn.execute('SELECT COUNT(*) FROM profile_pictures WHERE picture_id = ?', (picture_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return Profile_Picture(self, picture_id)

	def get_major(self, major_id):
		result = self.conn.execute('SELECT COUNT(*) FROM majors WHERE major_id = ?', (major_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return Major(self, major_id)

	def get_course(self, course_id):
		result = self.conn.execute('SELECT COUNT(*) FROM courses WHERE course_id = ?', (course_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return Course(self, course_id)

	def get_student(self, student_id, force=False):
		result = self.conn.execute('SELECT COUNT(*) FROM students WHERE student_id = ?', (student_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			student = Student(self, student_id)
			if student.is_deactivated() and not force:
				return None
			return student

	def get_online_students(self, self_student=None, require_sharing=False):
		students = self.get_all_schools()[0].get_students()
		ret = []
		for student in students:
			lastUpdated = student.get_location_last_updated()
			if (not student.is_invisible() and (require_sharing != True or student.is_sharing())
					or self_student == student) and lastUpdated is not None: # and int(time.time()) - int(lastUpdated) >= 1800:
				ret.append(student)
		return ret

	def create_student(self, email, hashpw, name, school):
		cursor = self.conn.cursor()
		#bios are empty string by default
		cursor.execute('INSERT INTO students(email, password, name, school_id, bio) VALUES(?, ?, ?, ?, "")', (email, hashpw, name, school.get_id()))
		student_id = cursor.lastrowid
		cursor.close()
		self.conn.commit()
		return self.get_student(student_id)

	def get_clothing(self, clothing_id):
		result = self.conn.execute('SELECT COUNT(*) FROM wearing_clothings WHERE wearing_clothing_id = ?', (clothing_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return Clothing(self, clothing_id)

	def get_time_availability(self, time_id):
		result = self.conn.execute('SELECT COUNT(*) FROM time_availability WHERE time_id = ?', (time_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return Availability(self, time_id)

	def get_study_group(self, study_group_id):
		result = self.conn.execute('SELECT COUNT(*) FROM study_groups WHERE study_group_id = ?', (study_group_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return Study_group(self, study_group_id)

	def get_public_study_groups(self):
		result = self.conn.execute('SELECT * FROM study_groups WHERE public = TRUE').fetchall()
		output = []
		for i in result:
			output.append(self.get_study_group(i['study_group_id']))
		return output

	def create_study_group(self, course, location, name, max_members):
		cursor = self.conn.cursor()
		#descriptions and schedules are empty string by default and study groups are private by default
		cursor.execute('INSERT INTO study_groups(course_id, latitude, longitude, name, description, max_members, schedule, public) VALUES(?, ?, ?, ?, "", ?, "", FALSE)', (course.get_id(), location.latitude, location.longitude, name, max_members))
		study_group_id = cursor.lastrowid
		cursor.close()
		self.conn.commit()
		return self.get_study_group(study_group_id)

	def get_study_group_invitation(self, study_group_invitation_id):
		result = self.conn.execute('SELECT COUNT(*) FROM study_group_invitations WHERE study_group_invitation_id = ?', (study_group_invitation_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return Study_group_invitation(self, study_group_invitation_id)

	def find_study_group_invitation(self, student, group):
		result = self.conn.execute('SELECT study_group_invitation_id FROM study_group_invitations WHERE recipient_student_id = ? AND study_group_id = ?', (student.get_id(), group.get_id(),)).fetchone()
		if result is None:
			return None
		else:
			return Study_group_invitation(self, result[0])

	def create_study_group_invitation(self, study_group, sender, recipient):
		cursor = self.conn.cursor()
		cursor.execute('INSERT INTO study_group_invitations(study_group_id, sender_student_id, recipient_student_id) VALUES(?, ?, ?)', (study_group.get_id(), sender.get_id(), recipient.get_id()))
		invite_id = cursor.lastrowid
		cursor.close()
		self.conn.commit()
		return self.get_study_group_invitation(invite_id)

	def create_friend_request(self, sender, recipient):
		cursor = self.conn.cursor()
		cursor.execute('INSERT INTO friend_requests(sender_student_id, recipient_student_id) VALUES(?, ?)', (sender.get_id(), recipient.get_id()))
		request_id = cursor.lastrowid
		cursor.close()
		self.conn.commit()
		return self.get_friend_request(request_id)

	def get_friend_request(self, friend_request_id):
		result = self.conn.execute('SELECT COUNT(*) FROM friend_requests WHERE friend_request_id = ?', (friend_request_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return Friend_Request(self, friend_request_id)

	def find_friend_request(self, sender, recipient):
		result = self.conn.execute('SELECT friend_request_id FROM friend_requests WHERE recipient_student_id = ? AND sender_student_id = ?', (recipient.get_id(), sender.get_id(),)).fetchone()
		if result is None:
			return None
		else:
			return Friend_Request(self, result[0])

	"""Searches the database for users whose name or email partially matches the search term."""
	def search_student(self, search_term):
		students = self.conn.execute("SELECT student_id FROM students WHERE ( LOWER(name) LIKE ? OR LOWER(email) LIKE ? )", ('%' + search_term.lower() + '%', '%' + search_term.lower() + '%',)).fetchall()
		output = []
		for i in students:
			output.append(self.get_student(i['student_id']))
		return output

	"""Searches the database for users whose email matches the search term.
	If exact is True, only an exact match counts; otherwise a partial match will count."""
	def search_student_email(self, search_term, exact = True):
		students = None
		if exact:
			students = self.conn.execute("SELECT student_id FROM students WHERE LOWER(email) = ?", (search_term.lower(),)).fetchall()
		else:
			students = self.conn.execute("SELECT student_id FROM students WHERE LOWER(email) LIKE ?", ('%' + search_term.lower() + '%',)).fetchall()
		output = []
		for i in students:
			output.append(self.get_student(i['student_id']))
		return output

	def search_course(self, search_term):
		# TODO: maybe format the search term? (e.g. 'CS307' should be able to find 'CS 307')
		courses = self.conn.execute("SELECT * FROM courses WHERE ( LOWER(course_name) LIKE ? OR LOWER(course_title) LIKE ? ) LIMIT 25", ('%' + search_term.lower() + '%', '%' + search_term.lower() + '%',)).fetchall()
		output = []
		for i in courses:
			output.append(self.get_course(i['course_id']))
		return output

	def search_group(self, search_term, public_only=True):
		courses = None
		if public_only:
			courses = self.conn.execute("SELECT * FROM study_groups WHERE public = TRUE AND LOWER(name) LIKE ?", ('%' + search_term.lower() + '%',)).fetchall()
		else:
			courses = self.conn.execute("SELECT * FROM study_groups WHERE LOWER(name) LIKE ?", ('%' + search_term.lower() + '%',)).fetchall()

		output = []
		for i in courses:
			output.append(self.get_study_group(i['study_group_id']))
		return output

	def get_direct_message(self, direct_message_id):
		result = self.conn.execute('SELECT COUNT(*) FROM direct_messages WHERE direct_message_id = ?', (direct_message_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return Direct_message(self, direct_message_id)

	def create_direct_message(self, sender, recipient, message, time_sent):
		cursor = self.conn.cursor()
		cursor.execute('INSERT INTO direct_messages(sender_student_id, recipient_student_id, message, unread, time_sent) VALUES(?, ?, ?, TRUE, ?)', (sender.get_id(), recipient.get_id(), message, time_sent))
		message_id = cursor.lastrowid
		cursor.close()
		self.conn.commit()
		return self.get_direct_message(message_id)

	def get_group_message(self, group_message_id):
		result = self.conn.execute('SELECT COUNT(*) FROM group_messages WHERE group_message_id = ?', (group_message_id, )).fetchone()
		if(result[0] == 0):
			return None
		else:
			return Group_message(self, group_message_id)

	def create_group_message(self, sender, group, message, time_sent):
		cursor = self.conn.cursor()
		cursor.execute('INSERT INTO group_messages(sender_student_id, study_group_id, message, time_sent) VALUES(?, ?, ?, ?)', (sender.get_id(), group.get_id(), message, time_sent))
		message_id = cursor.lastrowid
		cursor.close()
		self.conn.commit()
		return self.get_group_message(message_id)

	def get_notification(self, notification_id):
		result = self.conn.execute('SELECT COUNT(*) FROM notifications WHERE notification_id = ?', (notification_id, )).fetchone()
		if (result[0] == 0):
			return None
		else:
			return Notification(self, notification_id)

	def create_notification(self, student, type, json_data):
		time_stamp = int(time.time())
		cursor = self.conn.cursor()
		cursor.execute('INSERT INTO notifications(student_id, type, json_data, time_stamp) VALUES(?, ?, ?, ?)', (student.get_id(), type, json_data, time_stamp))
		notification_id = cursor.lastrowid
		cursor.close()
		self.conn.commit()
		return self.get_notification(notification_id)

	def get_students_with_course(self, course_id, require_current=True):
		students = []
		if require_current:
			students = self.conn.execute('SELECT student_id FROM attended_courses WHERE course_id = ? AND is_current = ?', (course_id, True, )).fetchall()
		else:
			students = self.conn.execute('SELECT student_id FROM attended_courses WHERE course_id = ?', (course_id, )).fetchall()

		output = []
		for i in students:
			output.append(self.get_student(i['student_id']))
		return output


