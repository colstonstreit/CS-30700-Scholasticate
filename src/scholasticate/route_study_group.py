import json
from scholasticate.location import Location
from flask import render_template, request, url_for, redirect, session, flash
import scholasticate.database as db
from scholasticate.util import getUsefulUserInformation, render_template_wrapper, name_validity_check

def route(app):

	@app.route('/group/<group_id>', methods=['GET'])
	def viewGroup(group_id):
		database = db.Database()
		studyGroup = database.get_study_group(group_id)

		if (studyGroup is None):
			flash("Not a valid group!")
			return redirect(url_for("index"))

		groupMembers = studyGroup.get_members()
		groupMembersSerialized = []
		for member in groupMembers:
			groupMembersSerialized.append(member.serialize())

		userID = session.get('userID')
		student = database.get_student(int(userID))

		if student is None:
			return redirect(url_for('auth.login'))

		if studyGroup.is_public() or student in groupMembers:
			return render_template_wrapper('displayGroup.html', group=studyGroup.serialize(), members=json.dumps(groupMembersSerialized), owner=studyGroup.get_owner().serialize(), invite="")
		else:
			invite = database.find_study_group_invitation(student, studyGroup)
			if invite is not None:
				return render_template_wrapper('displayGroup.html', group=studyGroup.serialize(), members=json.dumps(groupMembersSerialized), owner=studyGroup.get_owner().serialize(), invite=invite.serialize())
			else:
				flash("This group is private, you cannot view it. Try logging into a different account.")
				return redirect(url_for('index'))

	@app.route('/group/<group_id>/edit', methods=['GET'])
	def editGroupProfile(group_id):
		#TODO make sure user is in the group
		userID = session.get('userID')
		database = db.Database()
		sessionStudent = database.get_student(userID)

		studyGroup = database.get_study_group(group_id)

		if (studyGroup is None):
			flash("Not a valid group!")
			return redirect(url_for("viewGroup", group_id = group_id))
		elif (studyGroup.is_owner(sessionStudent)):
			return render_template_wrapper('editGroup.html', group=studyGroup.serialize(), group_id=group_id)
		else:
			flash("You don't own this group!")
			return redirect(url_for("viewGroup", group_id=group_id))


	@app.route('/creategroup', methods=['GET'])
	def createGroup():
		userID = session.get('userID')
		if (userID is None):
			return redirect(url_for('auth.login'))
		database = db.Database()
		student = database.get_student(int(userID))
		if student is None:
			return redirect(url_for('auth.login'))

		return render_template_wrapper('createGroup.html')

	@app.route('/creategroup', methods=['POST'])
	def createGroupPost():
		userID = session.get('userID')
		if (userID is None):
			return redirect(url_for('auth.login'))

		database = db.Database()

		thisStudent = database.get_student(int(userID))
		if thisStudent is None:
			return redirect(url_for('auth.login'))

		name = request.form.get("group_name")
		name = name.strip()

		namecheck = name_validity_check(name)
		if namecheck != True:
			flash(namecheck)
			return redirect(url_for('createGroup'))

		course = database.get_course(request.form.get("courseSelect"))
		if (course is None):
			flash("Not a valid course!")
			return redirect(url_for('createGroup'))

		max_members = request.form.get("max_members")
		group = database.create_study_group(course, Location(0, 0), name, max_members)
		if group is None:
			flash("Failed to create group!")
			return redirect(url_for('createGroup'))

		longitude = 0.0
		latitude = 0.0
		if (request.form.get("latitude") != ""):
			latitude = float(request.form.get("latitude"))
		if (request.form.get("longitude") != ""):
			longitude = float(request.form.get("longitude"))
		group.set_location(Location(latitude, longitude))

		group.add_member(thisStudent)
		group.set_owner(thisStudent)
		public = 1 if request.form.get("public") == "on" else 0
		group.set_public(public)
		group.set_schedule(request.form.get("schedule"))
		group.set_description(request.form.get("description"))

		return redirect(url_for('editGroupProfile', group_id = group.get_id()))

	@app.route('/group/<group_id>/edit', methods=['POST'])
	def editGroupProfile_Post(group_id):

		userID = session.get('userID')
		if (userID is None):
			return redirect(url_for('auth.login'))

		database = db.Database()

		thisStudent = database.get_student(int(userID))
		if thisStudent is None:
			return redirect(url_for('auth.login'))

		group = database.get_study_group(int(group_id))
		if not group.is_owner(thisStudent):
			flash("You don't own this group!")
			return redirect(url_for('viewGroup', group_id=group_id))

		name = request.form.get("name")
		schedule = request.form.get("schedule")
		description = request.form.get("description")
		longitude = 0.0
		latitude = 0.0
		if (request.form.get("latitude") is not None):
			latitude = float(request.form.get("latitude"))
		if (request.form.get("longitude") is not None):
			longitude = float(request.form.get("longitude"))
		max_members = request.form.get("max_members")
		checked = 1 if request.form.get("public") == "on" else 0
		group.set_name(name)
		group.set_schedule(schedule)
		group.set_description(description)
		group.set_location(Location(latitude, longitude))
		group.set_max_members(max_members)
		group.set_public(checked)
		return redirect(url_for('viewGroup', group_id=group_id))

	@app.route('/group/<group_id>/join', methods=['POST'])
	def joinPublicGroup(group_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		database = db.Database()
		thisStudent = database.get_student(int(userID))
		if thisStudent is None:
			return redirect(url_for('auth.login'))

		group = database.get_study_group(int(group_id))

		if thisStudent in group.get_members():
			flash("You are already in this group!")
			return redirect(url_for('viewGroup', group_id=group_id))

		if not group.get_public():
			flash("You must be invited to join a private group!")
			return redirect(url_for('viewGroup', group_id=group_id))

		if len(group.get_members()) == int(group.get_max_members()):
			flash("You cannot join this group. Too many members!")
			return redirect(url_for('viewGroup', group_id=group_id))

		### Send notifications to other members about the user joining
		for member in group.get_members():
			if member.wants_notifications_of_type("MemberJoinedGroup"):
				data = {"group_id": group.get_id(), "group_name": group.get_name(), "member_id": thisStudent.get_id(), "member_name": thisStudent.get_name()}
				database.create_notification(member, "MemberJoinedGroup", json.dumps(data))

		group.add_member(thisStudent)
		schedule = group.get_schedule().split(" ")
		if (len(schedule) == 2):
			scheduleTimes = schedule[1].split("-")
			if (len(scheduleTimes) == 2):
				thisStudent.delete_time(schedule[0], scheduleTimes[0], scheduleTimes[1])

		return redirect(url_for('viewGroup', group_id=group_id))

	@app.route('/group/<group_id>/leave', methods=['POST'])
	def leaveGroup(group_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		database = db.Database()
		thisStudent = database.get_student(int(userID))
		if thisStudent is None:
			return redirect(url_for('auth.login'))

		group = database.get_study_group(int(group_id))

		if thisStudent not in group.get_members():
			flash("You are not in this group!")
			return redirect(url_for('viewGroup', group_id=group_id))

		if group.is_owner(thisStudent):
			flash("You cannot quit a group you own!")
			return redirect(url_for('viewGroup', group_id=group_id))

		group.remove_member(thisStudent)

		for member in group.get_members():
			if member.wants_notifications_of_type("MemberLeftGroup"):
				data = {"group_id": group.get_id(), "group_name": group.get_name(), "member_id": thisStudent.get_id(), "member_name": thisStudent.get_name()}
				database.create_notification(member, "MemberLeftGroup", json.dumps(data))

		return redirect(url_for('viewGroup', group_id=group_id))

	@app.route('/group/<group_id>/disband', methods=['POST'])
	def disbandGroup(group_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		database = db.Database()
		thisStudent = database.get_student(int(userID))
		if thisStudent is None:
			return redirect(url_for('auth.login'))

		group = database.get_study_group(int(group_id))

		if not group.is_owner(thisStudent):
			flash("You must own the group to disband it!")
			return redirect(url_for('viewGroup', group_id=group_id))

		groupName = group.get_name()
		group.delete()
		flash("Successfully disbanded group " + groupName + "!")
		return redirect(url_for('index'))

	@app.route('/group/<group_id>/transfer', methods=['GET'])
	def transferGroup(group_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))
		database = db.Database()
		sessionStudent = database.get_student(int(userID))
		if sessionStudent is None:
			return redirect(url_for('auth.login'))

		studyGroup = database.get_study_group(int(group_id))
		studyGroupMembers = studyGroup.get_members()
		groupMembersSerialized = []
		for member in studyGroupMembers:
			if userID != member.get_id():
				groupMembersSerialized.append(member.serialize())

		if (studyGroup is None):
			flash("Invalid group!")
			return redirect(url_for('viewGroup', group_id=group_id))
		elif (studyGroup.is_owner(sessionStudent)):
			return render_template_wrapper('transferOwnership.html', group=studyGroup.serialize(), group_id=group_id, members=json.dumps(groupMembersSerialized))
		else:
			flash("You are not the owner of this group! You cannot transfer ownership here!")
			return redirect(url_for('viewGroup', group_id=group_id))

	@app.route('/group/<group_id>/transfer', methods=['POST'])
	def transferGroupPost(group_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))

		database = db.Database()
		thisStudent = database.get_student(int(userID))
		if thisStudent is None:
			return redirect(url_for('auth.login'))

		group = database.get_study_group(int(group_id))

		if not group.is_owner(thisStudent):
			flash("You must own the group to transfer it!")
			return redirect(url_for('viewGroup', group_id=group_id))

		otherStudentId = request.form.get("groupMembers")
		if otherStudentId is None:
			flash("You have to select another student to be the new owner!")
			return redirect(url_for('transferGroup', group_id=group_id))

		otherStudent = database.get_student(int(request.form.get("groupMembers")))
		if otherStudent is None:
			flash("That is not a valid student!")
			return redirect(url_for('transferGroup', group_id=group_id))
		if otherStudent == thisStudent:
			flash("You cannot transfer to yourself!")
			return redirect(url_for('transferGroup', group_id=group_id))
		if otherStudent not in group.get_members():
			flash("That student is not in this group!")
			return redirect(url_for('transferGroup', group_id=group_id))

		group.set_owner(otherStudent)
		flash("Set owner of the group to " + otherStudent.get_name() + ".")
		return redirect(url_for('viewGroup', group_id=group_id))

	@app.route('/group/<group_id>/removeMember', methods=['GET'])
	def removeFromGroup(group_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))
		database = db.Database()
		sessionStudent = database.get_student(int(userID))
		if sessionStudent is None:
			return redirect(url_for('auth.login'))

		studyGroup = database.get_study_group(int(group_id))
		studyGroupMembers = studyGroup.get_members()
		groupMembersSerialized = []
		for member in studyGroupMembers:
			if userID != member.get_id():
				groupMembersSerialized.append(member.serialize())

		if (studyGroup is None):
			flash("Invalid group!")
			return redirect(url_for('viewGroup', group_id=group_id))
		elif (studyGroup.is_owner(sessionStudent)):
			return render_template_wrapper('groupMemberRemoval.html', group=studyGroup.serialize(), group_id=group_id, members=json.dumps(groupMembersSerialized))
		else:
			flash("You are not the owner of this group! You cannot remove a member!")
			return redirect(url_for('viewGroup', group_id=group_id))

	@app.route('/group/<group_id>/removeMember', methods=['POST'])
	def removeFromGroupPost(group_id):
		userID = session.get('userID')
		if userID is None:
			return redirect(url_for('auth.login'))
		database = db.Database()
		thisStudent = database.get_student(int(userID))
		if thisStudent is None:
			return redirect(url_for('auth.login'))
		group = database.get_study_group(int(group_id))
		if not group.is_owner(thisStudent):
			flash("You must own the group to remove a member from it!")
			return redirect(url_for('viewGroup', group_id=group_id))

		otherStudentId = request.form.get("groupMembers")
		if otherStudentId is None:
			flash("You have to select another student to remove!")
			return redirect(url_for('removeFromGroup', group_id=group_id))

		otherStudent = database.get_student(int(request.form.get("groupMembers")))
		if otherStudent is None:
			flash("That is not a valid student!")
			return redirect(url_for('removeFromGroup', group_id=group_id))
		if otherStudent == thisStudent:
			flash("You cannot remove yourself!")
			return redirect(url_for('removeFromGroup', group_id=group_id))
		if otherStudent not in group.get_members():
			flash("That student is not in this group!")
			return redirect(url_for('removeFromGroup', group_id=group_id))

		group.remove_member(otherStudent)
		flash("Removed the following from the group: " + otherStudent.get_name() + ".")
		return redirect(url_for('viewGroup', group_id=group_id))
