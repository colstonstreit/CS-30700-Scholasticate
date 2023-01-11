import json
from scholasticate.location import Location
from flask import render_template, request, url_for, redirect, session
import scholasticate.database as db
from scholasticate.util import getUsefulUserInformation, render_template_wrapper

def route(app):
	@app.route('/sendFriendRequest/<recipient_id>', methods=['POST'])
	def sendFriendRequest(recipient_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		database = db.Database()
		recipient = database.get_student(int(recipient_id))
		sender = database.get_student(int(userID))
		database.create_friend_request(sender, recipient)

		### Send notification to recipient
		if recipient.wants_notifications_of_type('ReceivedFriendRequest'):
			data = {'sender_id': sender.get_id(), 'sender_name': sender.get_name()}
			database.create_notification(recipient, "ReceivedFriendRequest", json.dumps(data))

		return "200"

	@app.route('/acceptFriendRequest/<sender_id>', methods=['POST'])
	def acceptFriendRequest(sender_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		database = db.Database()
		sender = database.get_student(int(sender_id))
		recipient = database.get_student(int(userID))
		if (sender is None or recipient is None):
			return "Invalid ID!"
		request = database.find_friend_request(sender, recipient)
		if request is None:
			return "No friend request found to accept!"

		sender.add_friend(recipient)

		### Send notification to sender indicating acceptance
		if sender.wants_notifications_of_type('AcceptedFriendRequest'):
			data = {'recipient_id': recipient.get_id(), 'recipient_name': recipient.get_name()}
			database.create_notification(sender, "AcceptedFriendRequest", json.dumps(data))

		### Delete friend request notification for other user
		for notification in recipient.get_notifications():
			data = json.loads(notification.get_json_data())
			if notification.get_type() == "ReceivedFriendRequest" and data['sender_id'] == sender.get_id():
				notification.delete()

		request.delete()
		return "200"

	@app.route('/rejectFriendRequest/<sender_id>', methods=['POST'])
	def rejectFriendRequest(sender_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		database = db.Database()
		sender = database.get_student(int(sender_id))
		recipient = database.get_student(int(userID))
		if (sender is None or recipient is None):
			return "Invalid ID!"
		request = database.find_friend_request(sender, recipient)
		if request is None:
			return "No friend request found to reject!"

		### Delete friend request notification for other user
		for notification in recipient.get_notifications():
			data = json.loads(notification.get_json_data())
			if notification.get_type() == "ReceivedFriendRequest" and data['sender_id'] == sender.get_id():
				notification.delete()

		request.delete()
		return "200"

	@app.route('/cancelFriendRequest/<recipient_id>', methods=['POST'])
	def cancelFriendRequest(recipient_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		database = db.Database()
		recipient = database.get_student(int(recipient_id))
		sender = database.get_student(int(userID))
		if (sender is None or recipient is None):
			return "Invalid ID!"
		request = database.find_friend_request(sender, recipient)
		if request is None:
			return "No friend request found to cancel!"

		request.delete()
		return "200"

	@app.route('/removeFriend', methods=['POST'])
	def removeFriend():
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		id1 = request.json.get("friend1")
		id2 = request.json.get("friend2")
		if (id1 is None or id2 is None):
			return "400"
		student1 = db.Database().get_student(int(id1))
		student2 = db.Database().get_student(int(id2))
		student1.remove_friend(student2)
		return "200"