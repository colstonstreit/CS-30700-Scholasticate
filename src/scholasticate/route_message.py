import json
import time
from scholasticate.location import Location
from flask import render_template, request, url_for, redirect, session, flash, abort
import scholasticate.database as db
from scholasticate.util import getUsefulUserInformation, render_template_wrapper, get_session_student

def route(app):

	@app.route('/messages', methods=['GET'])
	def viewMessages():

		database = db.Database()
		student, studentID = get_session_student(database, session)
		if type(student) == int:
			abort(student)

		conversations = student.get_conversations()

		all_students = student.get_school().get_students()

		new_conversations = []
		for possible_student in all_students:
			exists = False
			for existing in conversations:
				if possible_student == existing:
					exists = True
			if possible_student == student:
				exists = True
			if exists == False:
				new_conversations.append(possible_student)

		return render_template_wrapper('messages.html', conversations=conversations, new_conversations=new_conversations, study_groups=student.get_study_groups())

	@app.route('/messages/user/<user_id>', methods=['GET'])
	def viewDirectMessages(user_id):

		database = db.Database()
		sender, senderID = get_session_student(database, session)
		if type(sender) == int:
			abort(sender)

		recipient = database.get_student(user_id)
		if recipient is None:
			abort(404)

		sender.read_conversation(recipient)
		return render_template_wrapper('directConversation.html', sender=sender, recipient=recipient)

	@app.route('/messages/user/<user_id>/getConversationJSON', methods=['GET'])
	def getDirectConversationJSON(user_id):

		database = db.Database()
		thisStudent, thisStudentID = get_session_student(database, session)
		if type(thisStudent) == int:
			abort(thisStudent)

		if not user_id:
			abort(404)
		otherStudent = database.get_student(int(user_id))
		if otherStudent is None:
			abort(404)

		thisStudent.read_conversation(otherStudent)
		conversation = thisStudent.get_conversation(otherStudent)
		conversation_output = []
		for message in conversation:
			conversation_output.append({
				"sender_id": message.get_sender().get_id(),
				"sender_name": message.get_sender().get_name(),
				"toMe": message.get_recipient() == thisStudent,
				"message": message.get_message(),
				"time_sent": message.get_time_sent(),
				"direct_message_id": message.get_id(),
				"read": not message.is_unread()
			})

		return json.dumps(conversation_output)

	@app.route('/messages/user/<user_id>/sendMessage', methods=['POST'])
	def sendDirectMessage(user_id):

		database = db.Database()
		sender, senderID = get_session_student(database, session)
		if type(sender) == int:
			abort(sender)

		recipient = database.get_student(user_id)
		if recipient is None:
			abort(403)

		message = request.form.get("message")
		if message is None:
			abort(403)

		database.create_direct_message(sender, recipient, str(message), int(time.time()))

		### Send notification or combine with existing notification if there is one
		alreadyHasUnreadMessage = False
		for notification in recipient.get_notifications():
			if notification.get_type() == "UnreadDirectMessage":
				data = json.loads(notification.get_json_data())
				if data['sender_id'] == senderID:
					notification.set_time_stamp(int(time.time()))
					data['messages'].append(str(message))
					notification.set_json_data(json.dumps(data))
					alreadyHasUnreadMessage = True
					break
		if not alreadyHasUnreadMessage:
			if recipient.wants_notifications_of_type('UnreadDirectMessage'):
				database.create_notification(recipient, "UnreadDirectMessage", json.dumps({'sender_id': sender.get_id(), 'sender_name': sender.get_name(), 'messages': [str(message)]}))

		return "success"

	@app.route('/messages/user/<user_id>/deleteMessage', methods=['POST'])
	def deleteDirectMessage(user_id):
		
		database = db.Database()
		student, studentID = get_session_student(database, session)
		if type(student) == int:
			abort(student)

		directMessage = database.get_direct_message(int(request.json.get('direct_message_id')))
		if directMessage is None or directMessage.get_sender() != student:
			abort(403)

		directMessage.delete()
		return "200"

	@app.route('/messages/group/<study_group_id>', methods=['GET'])
	def viewGroupMessages(study_group_id):

		database = db.Database()
		sender, senderID = get_session_student(database, session)
		if type(sender) == int:
			abort(sender)

		group = database.get_study_group(study_group_id)
		if (group is None) or (not sender.is_in_study_group(group)):
			abort(403)

		### Read messages, delete notifications (Daniel, I didn't make read receipts or anything. Just notifications for group messages)
		sender.read_group_conversation(group)

		### Pass through group members
		members = group.get_members()
		membersList = []
		for member in members:
			membersList.append(json.loads(member.serialize()))

		return render_template_wrapper('groupConversation.html', sender=sender, study_group=group, members=json.dumps(membersList))

	@app.route('/messages/group/<study_group_id>/getConversationJSON', methods=['GET'])
	def getGroupConversationJSON(study_group_id):

		database = db.Database()
		thisStudent, userID = get_session_student(database, session)
		if type(thisStudent) == int:
			abort(thisStudent)

		database = db.Database()
		thisStudent = database.get_student(userID)

		group = database.get_study_group(study_group_id)
		if (group is None) or (not thisStudent.is_in_study_group(group)):
			abort(403)

		### Read messages, delete notifications (Daniel, I didn't make read receipts or anything. Just notifications for group messages)
		thisStudent.read_group_conversation(group)

		conversation = group.get_conversation()
		conversation_output = []
		for message in conversation:
			conversation_output.append({
				"sender_id": message.get_sender().get_id(),
				"sender_name": message.get_sender().get_name(),
				"toMe": message.get_sender() != thisStudent,
				"message": message.get_message(),
				"time_sent": message.get_time_sent(),
				"group_message_id": message.get_id(),
				"readUsers": json.dumps(message.get_read_student_ids())
			})

		return json.dumps(conversation_output)

	@app.route('/messages/group/<study_group_id>/sendMessage', methods=['POST'])
	def sendGroupMessage(study_group_id):

		database = db.Database()
		sender, senderID = get_session_student(database, session)
		if type(sender) == int:
			abort(sender)

		group = database.get_study_group(study_group_id)
		if (group is None) or (not sender.is_in_study_group(group)):
			abort(400)

		message = request.form.get("message")
		if message is None:
			abort(400)

		database.create_group_message(sender, group, str(message), int(time.time()))

		### Send notification or combine with existing notification if there is one
		messageData = {'sender_id': sender.get_id(), 'sender_name': sender.get_name(), 'message': str(message)}
		for member in group.get_members():
			if member.get_id() == sender.get_id():
				continue
			alreadyHasUnreadMessage = False
			for notification in member.get_notifications():
				if notification.get_type() == "UnreadGroupMessage":
					data = json.loads(notification.get_json_data())
					if data['group_id'] == group.get_id():
						data['messages'].append(messageData)
						notification.set_time_stamp(int(time.time()))
						notification.set_json_data(json.dumps(data))
						alreadyHasUnreadMessage = True
						break
			if not alreadyHasUnreadMessage:
				if member.wants_notifications_of_type('UnreadGroupMessage'):
					database.create_notification(member, "UnreadGroupMessage", json.dumps({ 'group_id': group.get_id(), 'group_name': group.get_name(), 'messages': [messageData]}))

		return "success"

	@app.route('/messages/group/<study_group_id>/deleteMessage', methods=['POST'])
	def deleteGroupMessage(study_group_id):
		userID = session.get("userID")
		if userID is None:
			return redirect(url_for('auth.login'))

		database = db.Database()
		thisStudent = database.get_student(int(userID))
		groupMessage = database.get_group_message(int(request.json.get('group_message_id')))
		if groupMessage is None or groupMessage.get_sender() != thisStudent:
			abort(400)

		groupMessage.delete()
		return "200"