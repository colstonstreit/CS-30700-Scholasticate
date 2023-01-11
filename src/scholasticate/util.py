import json
from flask import Flask, render_template, request, url_for, flash, redirect, session, send_from_directory
import re
import scholasticate.database as db

### This function calls render_template but adds an argument containing all of the user's information
### which is put into the base.html file and can be accessed later in other JS files
def render_template_wrapper(*args, **kwargs):
	userInfo = getUsefulUserInformation(all=True)
	return render_template(*args, userInfo=userInfo, **kwargs)

def getUsefulUserInformation(*other, userID=None, getStudent=True, profilePicture=False, school=False, notifications=False,
														friends=False, acceptedUsers=False, clothing=False, currentCourses=False, pastCourses=False, settings=False,
														sentFriendRequests=False, receivedFriendRequests=False,
														studyGroups=False, receivedStudyGroupInvitations=False,
														availability=False, online_status=False, full_status=False, unread_conversations=False, all=False):
	if userID is None:
		userID = session.get("userID")
		if userID is None:
			return None
	database = db.Database()
	student = database.get_student(int(userID))
	if student is None:
		return None

	result = {}

	if getStudent or all:
		result['student'] = json.loads(student.serialize())
	if profilePicture or all:
		profile_picture = student.get_profile_picture()
		if profile_picture is not None:
			result['profile_picture'] = json.loads(profile_picture.serialize())
	if settings or all:
		settings = json.loads(student.get_settings_json())
		result['settings'] = settings
	if school or all:
		school = student.get_school()
		result['school'] = json.loads(school.serialize())
	if friends or all:
		friends = student.get_friends()
		friendsList = []
		for friend in friends:
			friendsList.append(json.loads(friend.serialize()))
		result['friends'] = friendsList
	if clothing or all:
		wardrobe = student.get_clothing()
		wardrobeList = []
		for item in wardrobe:
			wardrobeList.append(json.loads(item.serialize()))
		result['wardrobe'] = wardrobeList
	if currentCourses or all:
		currentCourses = student.get_current_courses()
		currentCourseList = []
		for course in currentCourses:
			currentCourseList.append(json.loads(course.serialize()))
		result['currentCourses'] = currentCourseList
	if pastCourses or all:
		pastCourses = student.get_past_courses()
		pastCourseList = []
		for course in pastCourses:
			pastCourseList.append(json.loads(course.serialize()))
		result['pastCourses'] = pastCourseList
	if sentFriendRequests or all:
		sentFriendRequests = student.get_sent_friend_requests()
		sentRequestsSerialized = []
		for request in sentFriendRequests:
			sentRequestsSerialized.append(json.loads(request.serialize()))
		result['sentFriendRequests'] = sentRequestsSerialized
	if receivedFriendRequests or all:
		receivedFriendRequests = student.get_received_friend_requests()
		receivedRequestsSerialized = []
		for request in receivedFriendRequests:
			receivedRequestsSerialized.append(json.loads(request.serialize()))
		result['receivedFriendRequests'] = receivedRequestsSerialized
	if studyGroups or all:
		studyGroups = student.get_study_groups()
		studyGroupsSerialized = []
		for group in studyGroups:
			studyGroupsSerialized.append(json.loads(group.serialize()))
		result['studyGroups'] = studyGroupsSerialized
	if receivedStudyGroupInvitations or all:
		receivedStudyGroupInvitations = student.get_study_group_received_invitations()
		receivedInvitesSerialized = []
		for invite in receivedStudyGroupInvitations:
			receivedInvitesSerialized.append(json.loads(invite.serialize()))
		result['receivedStudyGroupInvitations'] = receivedInvitesSerialized
	if availability or all:
		schedule = student.get_schedule()
		availabilityList = []
		for time in schedule:
			availabilityList.append(json.loads(time.serialize()))
		result['availability'] = availabilityList
	if full_status or online_status or all:
		online_status = student.get_location_last_updated() is not None and not student.is_invisible()
		result['online_status'] = online_status
		result['sharing'] = student.is_sharing()
	if full_status or all:
		# Only the user should be able to receive info on whether they are invisible or not
		# Otherwise it defeats the purposes of being invisible!
		result['invisible'] = student.is_invisible()
	if unread_conversations or all:
		unreads = student.get_unread_conversations()
		unreadList = []
		for s in unreads:
			unreadList.append({
				"student_id": s.get_id(),
				"student_name": s.get_name()
			})
		result['unread_conversations'] = unreadList
	if notifications or all:
		notifications = student.get_notifications()
		notificationList = []
		for notification in notifications:
			notificationList.append(json.loads(notification.serialize()))
		result['notifications'] = notificationList
	if acceptedUsers or all:
		acceptedUsers = student.get_accepted_users()
		acceptedUsersList = []
		for acceptedUser in acceptedUsers:
			acceptedUsersList.append(json.loads(acceptedUser.serialize()))
		result['acceptedUsers'] = acceptedUsersList

	return json.dumps(result)


regex_invis = "[\u0009\u00ad\u034f\u061c\u115f\u1160\u17b4\u17b5\u180e\u2000-\u200f\u202f\u205f\u2060-\u206F\u2028\u3000\u2800\u3164\uFEFF\uFFA0\u2063]+"
regex_zalgo = "([\u0300-\u036F\u1AB0-\u1AFF\u1DC0-\u1DFF\u20D0-\u20FF\uFE20-\uFE2F\u0483-\u0486\u05C7\u0610-\u061A\u0656-\u065F\u0670\u06D6-\u06ED\u0711\u0730-\u073F\u0743-\u074A\u0F18-\u0F19\u0F35\u0F37\u0F72-\u0F73\u0F7A-\u0F81\u0F84\u0e00-\u0eff\uFC5E-\uFC62]{2,})"

def name_validity_check(name):

	# length limit
	if len(name) < 2:
		return "Name must be at least 2 characters long!"

	if len(name) > 64:
		return "Name must be no more than 64 characters long!"

	# invisible characters
	if re.search(regex_invis, name) is not None:
		return "Name shouldn't contain invalid characters!"

	# zalgotext
	if re.search(regex_zalgo, name) is not None:
		return "Name shouldn't contain invalid characters!"

	return True

"""Returns the student object and ID of the current user of the session, or a status code (403/404) and None if the session or student is not valid.
If match_id is True, the session user must match that id, and the returned student object is that of match_id instead of the session user.
If admin_override is also True, the session user can either be the same user or be an admin; this is generally used for permission checking. The returned user is still the matched user."""
def get_session_student(database, session, match_id=None, admin_override=False):
	userID = session.get('userID')
	if not userID:
		return 403, None

	user = database.get_student(int(userID))
	if not user:
		return 404, None
	
	if match_id is not None:

		if type(match_id) == str:
			match_id = int(match_id)

		if match_id != int(userID) and not (admin_override and user.is_admin()):
			return 403, None
		else:
			student = database.get_student(match_id)
			if student is None:
				return 404, None
			return student, match_id

	return user, int(userID)