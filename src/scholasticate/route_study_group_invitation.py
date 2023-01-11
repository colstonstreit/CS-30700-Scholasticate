import json
from scholasticate.location import Location
from flask import render_template, request, url_for, redirect, session, flash
import scholasticate.database as db
from scholasticate.util import getUsefulUserInformation, render_template_wrapper

def route(app):

	@app.route('/profile/<id>/invite', methods=['GET'])
	def invitationPage(id):
		database = db.Database()
		invitee = database.get_student(int(id))
		inviter = database.get_student(int(session.get('userID')))
		groups = []
		for g in inviter.get_invitable_groups():
			groups.append(g.serialize())
		return render_template_wrapper('invitationCreation.html', id=id, groups=json.dumps(groups))

	@app.route('/profile/<id>/invite', methods=['POST'])
	def sendInvitation(id):
		inviter_id = session.get('userID')
		if (inviter_id is None or int(inviter_id) == int(id)):
			flash("You cannot invite yourself!")
			return redirect(url_for('profile', id=id))

		group_id = request.form.get('group_id')
		if not group_id:
			flash("No group id provided!")
			return redirect(url_for('invitationPage', id=id))
		database = db.Database()
		thisStudent = database.get_student(int(inviter_id))
		otherStudent = database.get_student(int(id))

		group = database.get_study_group(int(group_id))
		if group not in thisStudent.get_study_groups():
			flash("You are not in that group!")
			return redirect(url_for('profile', id=id))
		if group in otherStudent.get_study_groups():
			flash("Other user is already in that group!")
			return redirect(url_for('profile', id=id))

		existingInvitation = database.find_study_group_invitation(otherStudent, group)
		if existingInvitation is not None:
			flash("This user has already been invited to that group!")
			return redirect(url_for('profile', id=id))

		if not group.get_public() and not group.is_owner(thisStudent):
			flash("Only the owner can invite into a private group!")
			return redirect(url_for('profile', id=id))
		database.create_study_group_invitation(group, thisStudent, otherStudent)

		### Send notification to user
		if otherStudent.wants_notifications_of_type('InvitedToGroup'):
			data = {'group_id': group.get_id(), 'group_name': group.get_name(), 'sender_id': thisStudent.get_id(), 'sender_name': thisStudent.get_name()}
			database.create_notification(otherStudent, "InvitedToGroup", json.dumps(data))

		flash('Sent an invite for ' + group.get_name() + ' to ' + otherStudent.get_name() + '!')
		return redirect(url_for("profile", id=id))

	@app.route('/group/<group_id>/acceptInvite', methods=['POST'])
	def acceptInvitation(group_id):
		userID = session.get('userID')
		if (userID is None):
			return redirect(url_for('auth.login'))
		database = db.Database()

		thisStudent = database.get_student(userID)
		group = database.get_study_group(int(group_id))
		# TODO check validity of group
		if thisStudent in group.get_members():
			flash("You are already in this group!")
			return redirect(url_for('viewGroup', group_id=group_id))

		invite = database.find_study_group_invitation(thisStudent, group)
		if invite is None:
			flash("You don't have an invite!")
			return redirect(url_for('viewGroup', group_id=group_id))

		### Send notifications to others about the user joining
		for member in group.get_members():
			if member.wants_notifications_of_type("MemberJoinedGroup"):
				data = {"group_id": group.get_id(), "group_name": group.get_name(), "member_id": thisStudent.get_id(), "member_name": thisStudent.get_name()}
				database.create_notification(member, "MemberJoinedGroup", json.dumps(data))

		### Delete notification for invite
		for notification in thisStudent.get_notifications():
			data = json.loads(notification.get_json_data())
			if notification.get_type() == "InvitedToGroup" and data['group_id'] == group.get_id():
				notification.delete()

		group.add_member(thisStudent)
		invite.delete()

		return redirect(url_for("viewGroup", group_id=group_id))

	@app.route('/group/<group_id>/rejectInvite', methods=['POST'])
	def rejectInvitation(group_id):
		userID = session.get('userID')
		if (userID is None):
			return redirect(url_for('auth.login'))

		database = db.Database()

		thisStudent = database.get_student(userID)
		group = database.get_study_group(int(group_id))
		# TODO check validity of group
		if thisStudent in group.get_members():
			flash("You are already in this group!")
			return redirect(url_for('viewGroup', group_id=group_id))

		invite = database.find_study_group_invitation(thisStudent, group)
		if invite is None:
			flash("You don't have an invite!")
			return redirect(url_for('viewGroup', group_id=group_id))

		invite.delete()

		### Delete notification for invite
		for notification in thisStudent.get_notifications():
			data = json.loads(notification.get_json_data())
			if notification.get_type() == "InvitedToGroup" and data['group_id'] == group.get_id():
				notification.delete()

		return redirect(url_for("notifications", id=int(userID)))