
DROP TABLE IF EXISTS schools;

CREATE TABLE schools(
	school_id INTEGER PRIMARY KEY NOT NULL,
	name TEXT NOT NULL,
	latitude REAL NOT NULL,
	longitude REAL NOT NULL
);

INSERT INTO schools(school_id, name, latitude, longitude) VALUES
(1, "Purdue University", 40.42397490770524, -86.92118923770037);

CREATE UNIQUE INDEX index_school_name ON schools(name);

DROP TABLE IF EXISTS majors;

CREATE TABLE majors(
	major_id INTEGER PRIMARY KEY NOT NULL,
	school_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	FOREIGN KEY(school_id) REFERENCES schools(school_id)
);

DROP TABLE IF EXISTS courses;

CREATE TABLE IF NOT EXISTS courses(
	course_id INTEGER PRIMARY KEY NOT NULL,
	school_id INTEGER NOT NULL,
	course_name TEXT NOT NULL,
	professor_name TEXT NOT NULL,
	course_title TEXT NOT NULL,
	FOREIGN KEY(school_id) REFERENCES schools(school_id)
);

DROP TABLE IF EXISTS students;

CREATE TABLE students(
	student_id INTEGER PRIMARY KEY NOT NULL,
	password TEXT NOT NULL,
	security_question TEXT,
	security_answer TEXT,
	email TEXT NOT NULL,
	name TEXT NOT NULL,
	school_id INTEGER NOT NULL,
	bio TEXT NOT NULL,
	location_last_updated INTEGER,
	latitude REAL,
	longitude REAL,
	is_admin BOOLEAN DEFAULT 0 NOT NULL,
	invisible BOOLEAN DEFAULT 0 NOT NULL,
	sharing BOOLEAN DEFAULT 0 NOT NULL,
	account_status INTEGER DEFAULT 0 NOT NULL,
	settings_json TEXT DEFAULT '{"notifications": {"MemberJoinedGroup": 1, "MemberLeftGroup": 1, "InvitedToGroup": 1, "ReceivedFriendRequest": 1, "AcceptedFriendRequest": 1, "UnreadDirectMessage": 1, "UnreadGroupMessage": 1}, "refresh": {"AutomaticUpdates": 1, "RefreshRate": 60}}' NOT NULL,
	FOREIGN KEY(school_id) REFERENCES schools(school_id)
);

CREATE UNIQUE INDEX index_student_email ON students(email);

INSERT INTO students VALUES(10,'sha256$StCT1zgz$758519356ef4b8f6ca6bbac9fccce7f31dd55e0b3c8c13d7341bbbc8f1cb25b7',NULL,NULL,'jpurdue@purdue.edu','John Purdue',1,'',NULL,NULL,NULL,1,0,0,0,'{"notifications": {"MemberJoinedGroup": 1, "MemberLeftGroup": 1, "InvitedToGroup": 1, "ReceivedFriendRequest": 1, "AcceptedFriendRequest": 1, "UnreadDirectMessage": 1, "UnreadGroupMessage": 1}, "refresh": {"AutomaticUpdates": 1, "RefreshRate": 60}}');

DROP TABLE IF EXISTS profile_pictures;

CREATE TABLE profile_pictures(
	picture_id INTEGER PRIMARY KEY NOT NULL,
	student_id INTEGER NOT NULL,
	picture_string TEXT NOT NULL,
	FOREIGN KEY(student_id) REFERENCES students(student_id)
);

DROP TABLE IF EXISTS wearing_clothings;

CREATE TABLE wearing_clothings(
	wearing_clothing_id INTEGER PRIMARY KEY NOT NULL,
	student_id INTEGER NOT NULL,
	article TEXT NOT NULL,
	brand TEXT,
	color_red INTEGER NOT NULL,
	color_green INTEGER NOT NULL,
	color_blue INTEGER NOT NULL,
	FOREIGN KEY(student_id) REFERENCES students(student_id)
);

DROP TABLE IF EXISTS time_availability;

CREATE TABLE time_availability(
	time_id INTEGER PRIMARY KEY NOT NULL,
	student_id INTEGER NOT NULL,
	weekday TEXT NOT NULL,
	start_time TEXT NOT NULL,
	end_time TEXT NOT NULL,
	FOREIGN KEY(student_id) REFERENCES students(student_id)
);

DROP TABLE IF EXISTS attended_courses;

CREATE TABLE attended_courses(
	attended_course_id INTEGER PRIMARY KEY NOT NULL,
	student_id INTEGER NOT NULL,
	course_id INTEGER NOT NULL,
	is_current BOOLEAN NOT NULL,
	FOREIGN KEY(student_id) REFERENCES students(student_id),
	FOREIGN KEY(course_id) REFERENCES courses(course_id)
);

CREATE UNIQUE INDEX attended_courses_index ON attended_courses(student_id, course_id, is_current);

DROP TABLE IF EXISTS student_friends;

CREATE TABLE student_friends(
	student_friend_id INTEGER PRIMARY KEY NOT NULL,
	friend_a_id INTEGER NOT NULL,
	friend_b_id INTEGER NOT NULL,
	FOREIGN KEY(friend_a_id) REFERENCES students(student_id),
	FOREIGN KEY(friend_b_id) REFERENCES students(student_id)
);

CREATE UNIQUE INDEX student_friends_index ON student_friends(friend_a_id, friend_b_id);

DROP TABLE IF EXISTS student_blockeds;

CREATE TABLE student_blockeds(
	student_blocked_id INTEGER PRIMARY KEY NOT NULL,
	blocker_student_id INTEGER NOT NULL,
	blocked_student_id INTEGER NOT NULL,
	FOREIGN KEY(blocker_student_id) REFERENCES students(student_id),
	FOREIGN KEY(blocked_student_id) REFERENCES students(student_id)
);

CREATE UNIQUE INDEX student_blockeds_index ON student_blockeds(blocker_student_id, blocked_student_id);

DROP TABLE IF EXISTS student_accepted_users;

CREATE TABLE student_accepted_users(
	student_accepted_id INTEGER PRIMARY KEY NOT NULL,
	acceptor_student_id INTEGER NOT NULL,
	accepted_student_id INTEGER NOT NULL,
	FOREIGN KEY(acceptor_student_id) REFERENCES students(student_id),
	FOREIGN KEY(accepted_student_id) REFERENCES students(student_id)
);

CREATE UNIQUE INDEX student_accepted_users_index ON student_accepted_users(acceptor_student_id, accepted_student_id);

DROP TABLE IF EXISTS study_groups;

CREATE TABLE study_groups(
	study_group_id INTEGER PRIMARY KEY NOT NULL,
	public BOOLEAN NOT NULL,
	name TEXT NOT NULL,
	description TEXT NOT NULL,
	max_members INTEGER NOT NULL,
	course_id INTEGER NOT NULL,
	schedule TEXT NOT NULL,
	latitude REAL NOT NULL,
	longitude REAL NOT NULL,
	FOREIGN KEY(course_id) REFERENCES courses(course_id)
);

DROP TABLE IF EXISTS study_group_members;

CREATE TABLE study_group_members(
	study_group_member_id INTEGER PRIMARY KEY NOT NULL,
	study_group_id INTEGER NOT NULL,
	student_id BOOLEAN NOT NULL,
	owner BOOLEAN NOT NULL,
	FOREIGN KEY(study_group_id) REFERENCES study_groups(study_group_id) ON DELETE CASCADE,
	FOREIGN KEY(student_id) REFERENCES students(student_id)
);

CREATE UNIQUE INDEX study_group_members_index ON study_group_members(study_group_id, student_id);

DROP TABLE IF EXISTS study_group_invitations;

CREATE TABLE study_group_invitations(
	study_group_invitation_id INTEGER PRIMARY KEY NOT NULL,
	study_group_id INTEGER NOT NULL,
	sender_student_id INTEGER NOT NULL,
	recipient_student_id INTEGER NOT NULL,
	FOREIGN KEY(study_group_id) REFERENCES study_groups(study_group_id) ON DELETE CASCADE,
	FOREIGN KEY(sender_student_id) REFERENCES students(student_id),
	FOREIGN KEY(recipient_student_id) REFERENCES students(student_id)
);

CREATE UNIQUE INDEX invitations_index ON study_group_invitations(study_group_id, sender_student_id, recipient_student_id);

DROP TABLE IF EXISTS direct_messages;
CREATE TABLE direct_messages(
	direct_message_id INTEGER PRIMARY KEY NOT NULL,
	sender_student_id INTEGER NOT NULL,
	recipient_student_id INTEGER NOT NULL,
	time_sent INTEGER NOT NULL,
	message TEXT NOT NULL,
	unread BOOLEAN NOT NULL,
	FOREIGN KEY(sender_student_id) REFERENCES students(student_id),
	FOREIGN KEY(recipient_student_id) REFERENCES students(student_id)
);

DROP TABLE IF EXISTS group_messages;
CREATE TABLE group_messages(
	group_message_id INTEGER PRIMARY KEY NOT NULL,
	sender_student_id INTEGER NOT NULL,
	study_group_id INTEGER NOT NULL,
	time_sent INTEGER NOT NULL,
	message TEXT NOT NULL,
	users_read_json TEXT DEFAULT "[]" NOT NULL,
	FOREIGN KEY(sender_student_id) REFERENCES students(student_id),
	FOREIGN KEY(study_group_id) REFERENCES study_groups(study_group_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS friend_requests;
CREATE TABLE friend_requests(
	friend_request_id INTEGER PRIMARY KEY NOT NULL,
	sender_student_id INTEGER NOT NULL,
	recipient_student_id INTEGER NOT NULL,
	FOREIGN KEY(sender_student_id) REFERENCES students(student_id),
	FOREIGN KEY(recipient_student_id) REFERENCES students(student_id)
);

CREATE UNIQUE INDEX friend_requests_index ON friend_requests(sender_student_id, recipient_student_id);

DROP TABLE IF EXISTS notifications;
CREATE TABLE notifications(
	notification_id INTEGER PRIMARY KEY NOT NULL,
	student_id INTEGER NOT NULL,
	type TEXT NOT NULL,
	json_data TEXT NOT NULL,
	time_stamp INTEGER NOT NULL,
	FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
);
