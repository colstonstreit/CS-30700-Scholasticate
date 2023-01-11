import math, json, time, re
from scholasticate.location import Location
import enum
from datetime import datetime
# from flask_login import UserMixin

class Account_Status(enum.IntEnum):
	NORMAL = 0
	DEACTIVATED = 1
	BANNED = 2 # not implemented

class Student:
	def __init__(self, database, student_id):
		self.is_authenticated = False
		self.is_active = True
		self.database = database
		self.student_id = student_id

	def __eq__(self, other):
		return other is not None and self.student_id == other.student_id

	def serialize(self, public_info = True):
		phrase = public_info and "student_id, name, bio, school_id, latitude, longitude, location_last_updated, invisible, sharing" or "*"
		result = self.database.conn.execute('SELECT ' + phrase + ' FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		if result is None:
			return "[]"
		result = dict(result)
		picture = self.database.conn.execute('SELECT picture_string FROM profile_pictures WHERE student_id = ?', (self.student_id, )).fetchone()
		if picture is not None:
			result['picture_string'] = picture['picture_string']

		currentCourseObjects = self.get_current_courses()
		currentCourses = []
		for courseObject in currentCourseObjects:
			currentCourses.append(courseObject.serialize())
		result['currentCourses'] = currentCourses

		pastCourseObjects = self.get_past_courses()
		pastCourses = []
		for courseObject in pastCourseObjects:
			pastCourses.append(courseObject.serialize())
		result['pastCourses'] = pastCourses

		return json.dumps(result)

	def get_id(self):
		return self.student_id

	def get_hashpw(self):
		result = self.database.conn.execute('SELECT password FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		return result['password']

	def set_hashpw(self, hashpw):
		self.database.conn.execute('UPDATE students SET password = ? WHERE student_id = ?', (hashpw, self.student_id))
		self.database.conn.commit()

	def get_security_answer(self):
		result = self.database.conn.execute('SELECT security_answer FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		return result['security_answer']

	def set_security_answer(self, new_answer):
		self.database.conn.execute('UPDATE students SET security_answer = ? WHERE student_id = ?', (new_answer, self.student_id))
		self.database.conn.commit()

	def get_security_question(self):
		result = self.database.conn.execute('SELECT security_question FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		return result['security_question']

	def set_security_question(self, new_question):
		self.database.conn.execute('UPDATE students SET security_question = ? WHERE student_id = ?', (new_question, self.student_id))
		self.database.conn.commit()

	def get_name(self):
		result = self.database.conn.execute('SELECT name FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		return result['name']

	def set_name(self, name):
		self.database.conn.execute('UPDATE students SET name = ? WHERE student_id = ?', (name, self.student_id))
		self.database.conn.commit()

	def get_email(self):
		result = self.database.conn.execute('SELECT email FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		return result['email']

	def get_school(self):
		result = self.database.conn.execute('SELECT school_id FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		return self.database.get_school(result['school_id'])

	def get_bio(self):
		result = self.database.conn.execute('SELECT bio FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		return result['bio']

	def set_bio(self, bio):
		self.database.conn.execute('UPDATE students SET bio = ? WHERE student_id = ?', (bio, self.student_id))
		self.database.conn.commit()

	def get_profile_picture(self):
		result = self.database.conn.execute('SELECT picture_id FROM profile_pictures WHERE student_id = ?', (self.student_id,)).fetchone()
		if result is None or result['picture_id'] is None:
			return None
		else:
			return self.database.get_profile_picture(result['picture_id'])

	def set_profile_picture(self, photo):
		self.database.conn.execute('UPDATE profile_pictures SET picture_string = ? WHERE student_id = ?', (photo.get_string(), self.get_id()))
		self.database.conn.commit()

	def is_admin(self):
		result = self.database.conn.execute('SELECT is_admin FROM students where student_id = ?', (self.student_id,)).fetchone()
		return bool(result['is_admin'])

	def is_invisible(self):
		result = self.database.conn.execute('SELECT invisible FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		return bool(result['invisible'])

	def set_invisible(self, invisible):
		self.database.conn.execute('UPDATE students SET invisible = ? WHERE student_id = ?', (invisible, self.student_id))
		self.database.conn.commit()

	def is_sharing(self):
		result = self.database.conn.execute('SELECT sharing FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		return bool(result['sharing'])

	def set_sharing(self, sharing):
		self.database.conn.execute('UPDATE students SET sharing = ? WHERE student_id = ?', (sharing, self.student_id))
		self.database.conn.commit()

	def get_location(self):
		result = self.database.conn.execute('SELECT latitude, longitude FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		if result is None or result['latitude'] is None or result['longitude'] is None:
			return None
		else:
			return Location(result['latitude'], result['longitude'])

	def set_location(self, location):
		self.database.conn.execute('UPDATE students SET latitude = ?, longitude = ? WHERE student_id = ?', (location.latitude, location.longitude, self.student_id))
		self.database.conn.commit()
		self.set_location_last_updated(int(time.time()))

	def get_location_last_updated(self):
		result = self.database.conn.execute('SELECT location_last_updated FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		if result['location_last_updated'] is None:
			return None
		else:
			return result['location_last_updated']

	def set_location_last_updated(self, location_last_updated):
		self.database.conn.execute('UPDATE students SET location_last_updated = ? WHERE student_id = ?', (location_last_updated, self.student_id))
		self.database.conn.commit()

	def get_current_courses(self):
		courses = self.database.conn.execute('SELECT course_id FROM attended_courses WHERE student_id = ? AND is_current = TRUE', (self.student_id,)).fetchall()

		output = []
		for i in courses:
			output.append(self.database.get_course(i['course_id']))

		return output

	def add_current_course(self, course):
		self.database.conn.execute('INSERT INTO attended_courses(student_id, course_id, is_current) VALUES(?, ?, TRUE) ON CONFLICT DO NOTHING', (self.student_id, course.get_id()))
		self.database.conn.commit()

	def remove_current_course(self, course):
		self.database.conn.execute('DELETE FROM attended_courses WHERE student_id = ? AND course_id = ? AND is_current = TRUE', (self.student_id, course.get_id()))
		self.database.conn.commit()

	def get_past_courses(self):
		courses = self.database.conn.execute('SELECT course_id FROM attended_courses WHERE student_id = ? AND is_current = FALSE', (self.student_id,)).fetchall()

		output = []
		for i in courses:
			output.append(self.database.get_course(i['course_id']))

		return output

	def add_past_course(self, course):
		self.database.conn.execute('INSERT INTO attended_courses(student_id, course_id, is_current) VALUES(?, ?, FALSE) ON CONFLICT DO NOTHING', (self.student_id, course.get_id()))
		self.database.conn.commit()

	def remove_past_course(self, course):
		self.database.conn.execute('DELETE FROM attended_courses WHERE student_id = ? AND course_id = ? AND is_current = FALSE', (self.student_id, course.get_id()))
		self.database.conn.commit()

	def get_friends(self):
		students = self.database.conn.execute('SELECT friend_b_id AS student_id FROM student_friends WHERE friend_a_id = ? UNION SELECT friend_a_id AS student_id FROM student_friends WHERE friend_b_id = ?', (self.student_id, self.student_id)).fetchall()

		output = []
		for i in students:
			s = self.database.get_student(i['student_id'])
			if s is not None:
				output.append(s)

		return output

	def add_friend(self, friend):
		self.database.conn.execute('INSERT INTO student_friends(friend_a_id, friend_b_id) VALUES(?, ?) ON CONFLICT DO NOTHING', (self.student_id, friend.get_id()))
		self.database.conn.commit()

	def remove_friend(self, friend):
		self.database.conn.execute('DELETE FROM student_friends WHERE friend_a_id = ? AND friend_b_id = ?', (self.student_id, friend.get_id()))
		self.database.conn.execute('DELETE FROM student_friends WHERE friend_b_id = ? AND friend_a_id = ?', (self.student_id, friend.get_id()))
		self.database.conn.commit()

	def get_blockeds(self):
		students = self.database.conn.execute('SELECT blocked_student_id FROM student_blockeds WHERE blocker_student_id = ?', (self.student_id,)).fetchall()

		output = []
		for i in students:
			s = self.database.get_student(i['blocked_student_id'])
			if s is not None:
				output.append(s)

		return output

	def add_blocked(self, blocked):
		self.database.conn.execute('INSERT INTO student_blockeds(blocker_student_id, blocked_student_id) VALUES(?, ?) ON CONFLICT DO NOTHING', (self.student_id, blocked.get_id()))
		self.database.conn.commit()

	def remove_blocked(self, blocked):
		self.database.conn.execute('DELETE FROM student_blockeds WHERE blocker_student_id = ? AND blocked_student_id = ?', (self.student_id, blocked.get_id()))
		self.database.conn.commit()


	def get_accepted_users(self):
		students = self.database.conn.execute('SELECT accepted_student_id FROM student_accepted_users WHERE acceptor_student_id = ?', (self.get_id(), )).fetchall()

		output = []
		for i in students:
			s = self.database.get_student(i['accepted_student_id'])
			if s is not None:
				output.append(s)

		return output


	def add_accepted(self, accepted):

		self.database.conn.execute('INSERT INTO student_accepted_users(acceptor_student_id, accepted_student_id) VALUES(?,?) ON CONFLICT DO NOTHING', (self.get_id(), accepted.get_id()))
		self.database.conn.commit()

	def remove_accepted(self, accepted):
		self.database.conn.execute('DELETE FROM student_accepted_users WHERE acceptor_student_id = ? AND accepted_student_id = ?', (self.get_id(), accepted.get_id()))
		self.database.conn.commit()











	def get_clothing(self):
		clothings = self.database.conn.execute('SELECT wearing_clothing_id FROM wearing_clothings WHERE student_id = ?', (self.student_id,)).fetchall()
		output = []
		for i in clothings:
			output.append(self.database.get_clothing(i['wearing_clothing_id']))
		return output

	def add_clothing(self, article, brand, color):
		cursor = self.database.conn.cursor()
		cursor.execute('INSERT INTO wearing_clothings(student_id, article, brand, color_red, color_green, color_blue) VALUES(?, ?, ?, ?, ?, ?)', (self.student_id, article, brand, color[0], color[1], color[2]))
		clothing_id = cursor.lastrowid
		cursor.close()
		self.database.conn.commit()
		return self.database.get_clothing(clothing_id)

	def remove_clothing(self, article, brand, color):
		cursor = self.database.conn.cursor()
		cursor.execute('DELETE FROM wearing_clothings WHERE student_id = ? AND article = ? AND brand = ? AND color_red = ? AND color_green = ? AND color_blue = ?', (self.student_id, article, brand, color[0], color[1], color[2]))
		cursor.close()
		self.database.conn.commit()

	def get_schedule(self):
		schedule = self.database.conn.execute('SELECT time_id FROM time_availability WHERE student_id = ?', (self.student_id,)).fetchall()
		output = []
		for i in schedule:
			output.append(self.database.get_time_availability(i['time_id']))
		return output

	def add_time(self, weekday, start_time, end_time):
		cursor = self.database.conn.cursor()
		cursor.execute('INSERT INTO time_availability(student_id, weekday, start_time, end_time) VALUES(?, ?, ?, ?)', (self.student_id, weekday, start_time, end_time))
		time_id = cursor.lastrowid
		cursor.close()
		self.database.conn.commit()
		return self.database.get_time_availability(time_id)

	def delete_time(self, weekday, start_time, end_time):
		cursor = self.database.conn.cursor()
		cursor.execute('DELETE FROM time_availability WHERE student_id = ? AND weekday = ? AND start_time = ? AND end_time = ?', (self.student_id, weekday, start_time, end_time))
		cursor.close()
		self.database.conn.commit()

	# Calculates current distance in km from every user (or group) online and sorts them in ascending order.
	def calculateRelativeDistances(self, entityList):
		distances = []
		location = self.get_location()
		if location is None:
			return []
		(lat1, long1) = (location.latitude, location.longitude)
		for entity in entityList:
			if (entity.get_location() is None):
				continue
			(lat2, long2) = (entity.get_location().latitude, entity.get_location().longitude)
			distKm = Location.distanceBetween(lat1, long1, lat2, long2)
			distances.append({"entityInfo": entity.serialize(),
												"distance": distKm,
												"type": "student" if hasattr(entity, "student_id") else "group"})

		return sorted(distances, key = lambda x: x["distance"])

	def get_study_groups(self):
		group_members = self.database.conn.execute('SELECT study_group_id FROM study_group_members WHERE student_id = ?', (self.student_id, )).fetchall()

		output = []
		for i in group_members:
			output.append(self.database.get_study_group(i['study_group_id']))

		return output

	def is_in_study_group(self, study_group):
		count = self.database.conn.execute('SELECT COUNT(*) AS count FROM study_group_members WHERE student_id = ? AND study_group_id = ?', (self.student_id, study_group.get_id())).fetchall()
		return count[0]['count'] > 0

	"""Returns all groups that a student can send invites for.
	A student can send an invite if and only if they are in the group, and the group is private."""
	def get_invitable_groups(self):
		groups = self.database.conn.execute('SELECT study_group_id FROM study_group_members WHERE student_id = ?', (self.student_id,)).fetchall()

		output = []
		for i in groups:
			group = self.database.get_study_group(i['study_group_id'])
			if not group.is_public():
				output.append(group)

		return output

	# TODO: unit tests
	def get_study_group_sent_invitations(self):
		invitations = self.database.conn.execute('SELECT study_group_invitation_id FROM study_group_invitations WHERE sender_student_id = ?', (self.student_id, )).fetchall()

		output = []
		for i in invitations:
			output.append(self.database.get_study_group_invitation(i['study_group_invitation_id']))

		return output

	# TODO: unit tests
	def get_study_group_received_invitations(self):
		invitations = self.database.conn.execute('SELECT study_group_invitation_id FROM study_group_invitations WHERE recipient_student_id = ?', (self.student_id, )).fetchall()

		output = []
		for i in invitations:
			output.append(self.database.get_study_group_invitation(i['study_group_invitation_id']))

		return output

	def get_conversations(self):
		students = self.database.conn.execute('SELECT sender_student_id AS student_id FROM direct_messages WHERE recipient_student_id = ? UNION SELECT recipient_student_id AS student_id FROM direct_messages WHERE sender_student_id = ?', (self.student_id, self.student_id)).fetchall()

		output = []
		for i in students:
			s = self.database.get_student(i['student_id'])
			if s is not None:
				output.append(s)

		return output

	def get_unread_conversations(self):
		students = self.database.conn.execute('SELECT sender_student_id FROM direct_messages WHERE recipient_student_id = ? AND unread = TRUE GROUP BY sender_student_id', (self.student_id, )).fetchall()

		output = []
		for i in students:
			s = self.database.get_student(i['sender_student_id'])
			if s is not None:
				output.append(s)

		return output

	def read_conversation(self, other_student):
		cursor = self.database.conn.cursor()
		cursor.execute('UPDATE direct_messages SET unread = FALSE WHERE recipient_student_id = ? AND sender_student_id = ?', (self.student_id, other_student.get_id())).fetchall()
		cursor.close()
		self.database.conn.commit()

		### Clear out notifications
		for notification in self.get_notifications():
			if notification.get_type() == "UnreadDirectMessage":
				data = json.loads(notification.get_json_data())
				if data['sender_id'] == other_student.get_id():
					self.database.conn.execute('DELETE FROM notifications WHERE notification_id = ?', (notification.get_id(), ))
					self.database.conn.commit()

	def read_group_conversation(self, group):

		### Mark all messages as read by this user
		messageRows = self.database.conn.execute('SELECT group_message_id FROM group_messages WHERE study_group_id = ? AND sender_student_id <> ?', (group.get_id(), self.student_id)).fetchall()
		cursor = self.database.conn.cursor()
		for messageRow in messageRows:
			message = self.database.get_group_message(messageRow['group_message_id'])
			usersRead = message.get_read_student_ids()
			if self.student_id not in usersRead:
				usersRead.append(self.student_id)
				cursor.execute('UPDATE group_messages SET users_read_json = ? WHERE group_message_id = ?', (json.dumps(usersRead), message.get_id()))
		cursor.close()
		self.database.conn.commit()

		### Clear out notifications
		for notification in self.get_notifications():
			if notification.get_type() == "UnreadGroupMessage":
				data = json.loads(notification.get_json_data())
				if data['group_id'] == group.get_id():
					self.database.conn.execute('DELETE FROM notifications WHERE notification_id = ?', (notification.get_id(), ))
					self.database.conn.commit()

	def get_conversation(self, other_student):
		messages = self.database.conn.execute('SELECT direct_message_id FROM direct_messages WHERE (sender_student_id = ? AND recipient_student_id = ?) OR (sender_student_id = ? AND recipient_student_id = ?) ORDER BY time_sent', (other_student.get_id(), self.student_id, self.student_id, other_student.get_id()))

		output = []
		for i in messages:
			output.append(self.database.get_direct_message(i['direct_message_id']))

		return output

	def get_sent_friend_requests(self):
		requests = self.database.conn.execute('SELECT friend_request_id FROM friend_requests WHERE sender_student_id = ?', (self.student_id, ))

		output = []
		for i in requests:
			output.append(self.database.get_friend_request(i['friend_request_id']))

		return output

	def get_received_friend_requests(self):
		requests = self.database.conn.execute('SELECT friend_request_id FROM friend_requests WHERE recipient_student_id = ?', (self.student_id, ))

		output = []
		for i in requests:
			output.append(self.database.get_friend_request(i['friend_request_id']))

		return output

	def get_notifications(self):
		notifications = self.database.conn.execute('SELECT notification_id FROM notifications WHERE student_id = ? ORDER BY time_stamp', (self.student_id, )).fetchall()
		output = []
		for notification in notifications:
			output.append(self.database.get_notification(notification['notification_id']))
		return output

	def get_settings_json(self):
		settings_json = self.database.conn.execute('SELECT settings_json FROM students WHERE student_id = ?', (self.get_id(), )).fetchone()
		return settings_json['settings_json'];

	def wants_notifications_of_type(self, type):
		settings = json.loads(self.get_settings_json())
		if 'notifications' in settings:
			if type in settings['notifications']:
				return settings['notifications'][type] == 1
		### By default return True
		return True

	def set_settings_json(self, settings_json):
		self.database.conn.execute('UPDATE students SET settings_json = ? WHERE student_id = ?', (settings_json, self.get_id()))
		self.database.conn.commit()

	def is_deactivated(self):
		result = self.database.conn.execute('SELECT account_status FROM students WHERE student_id = ?', (self.student_id,)).fetchone()
		return int(result['account_status']) == Account_Status.DEACTIVATED

	def deactivate(self):
		self.database.conn.execute('UPDATE students SET account_status = ?, name = ?, email = ?, password = ? WHERE student_id = ?', (Account_Status.DEACTIVATED, "", self.student_id, "", self.student_id))

		# Remove deactivated user from all groups
		# TODO: Handle the situation where the user owns a group
		self.database.conn.execute('DELETE FROM study_group_members WHERE student_id = ?', (self.student_id, ))

		self.database.conn.commit()

	def check_for_upcoming_study_sessions(self):
		timeNow = datetime.now()
		weekday = timeNow.strftime('%A')
		hour = int(timeNow.strftime('%H'))
		minute = int(timeNow.strftime('%M'))
		dayMap = {'M': 'Monday', 'T': 'Tuesday', 'W': 'Wednesday', 'R': 'Thursday',
							'F': 'Friday', 'S': 'Saturday', 'U': 'Sunday'}
		nextDayMap = {'Sunday': 'Monday', 'Monday': 'Tuesday', 'Tuesday': 'Wednesday', 'Wednesday': 'Thursday',
									'Thursday': 'Friday', 'Friday': 'Saturday', 'Saturday': 'Sunday'}

		### Match strings of type MWF 3:00-17:40
		pattern = re.compile('[MTWRFSU]+ [0-9]?[0-9]:[0-9][0-9]\-[0-9]?[0-9]:[0-9][0-9]')

		### Loop through groups' schedules and see if any have a time in a correct format
		for group in self.get_study_groups():
			schedule = group.get_schedule()
			for meetingString in pattern.findall(schedule):
				tokens = meetingString.split(' ')
				for day in tokens[0]:
					if dayMap[day] == weekday or hour == 23 and dayMap[day] == nextDayMap[weekday]:
						startTime = tokens[1].split('-')[0]
						startHour = int(startTime[0 : startTime.find(':')])
						startMinute = int(startTime[startTime.find(':') + 1 : ])
						if startHour == (hour + 1) % 24:
							startHour = (startHour - 1 + 24) % 24
							startMinute += 60
						elif startHour != hour:
							break
						### See if meeting time is within 30 minutes; if so, send notification if desired
						if startMinute - minute <= 30 and startMinute - minute >= 0:
							notificationData = {'group_id': group.get_id(), 'group_name': group.get_name(), 'startTime': startTime, 'minutesUntil': startMinute - minute}
							alreadyHasReceivedNotification = False
							for notification in self.get_notifications():
								if notification.get_type() == "UpcomingStudySession":
									data = json.loads(notification.get_json_data())
									if data['group_id'] == group.get_id():
										notification.set_time_stamp(int(time.time()))
										notification.set_json_data(json.dumps(notificationData))
										alreadyHasReceivedNotification = True
										break
							if not alreadyHasReceivedNotification:
								if self.wants_notifications_of_type('UpcomingStudySession'):
									self.database.create_notification(self, "UpcomingStudySession", json.dumps(notificationData))
						break


