
INSERT INTO majors(major_id, school_id, name) VALUES
(1, 1, "Computer Science"),
(2, 1, "Computer Engineering");

INSERT INTO courses(course_id, school_id, course_name, professor_name, course_title) VALUES
(1, 1, "CS 307", "Xiangyu Zhang", "Software Engineering I"),
(2, 1, "CS 352", "Zhiyuan Li", "Compilers: Principles and Practice"),
(3, 1, "CS 354", "Douglas E. Comer", "Operating Systems"),
(4, 1, "CS 407", "H. E. Dunsmore", "Software Engineering Senior Project");

DELETE FROM students;
INSERT INTO students(student_id, password, security_question, security_answer, email, name, school_id, bio, location_last_updated, latitude, longitude, is_admin, sharing) VALUES
(1, "XXXX", NULL, NULL, "jpurdue@purdue.edu", "John Purdue", 1, "This is my school! he/him/his", NULL, NULL, NULL, 1, 0),
(2, "XXXX", NULL, NULL, "mdaniels@purdue.edu", "Mitch Daniels", 1, "Busy freezing tuition. he/him/his", NULL, NULL, NULL, 0, 0);

INSERT INTO wearing_clothings(wearing_clothing_id, student_id, article, brand, color_red, color_green, color_blue) VALUES
(1, 1, "shirt", NULL, 120, 20, 0),
(2, 2, "hat", "Nike", 255, 255, 0);

INSERT INTO time_availability(time_id, student_id, weekday, start_time, end_time) VALUES
(1, 1, "Sunday", "11:00", "12:00"),
(2, 2, "Monday", "3:00", "7:00");

INSERT INTO attended_courses(attended_course_id, student_id, course_id, is_current) VALUES
(1, 1, 1, TRUE),
(2, 2, 1, FALSE),
(3, 2, 2, TRUE);

INSERT INTO student_friends(student_friend_id, friend_a_id, friend_b_id) VALUES
(1, 1, 2);

INSERT INTO study_groups(study_group_id, public, name, description, max_members, course_id, schedule, latitude, longitude) VALUES
(1, TRUE, "CS 307 Group", "Group for studying for Software Engineering", 5, 1, "Every tuesday", 40.427528179812505, -86.91317399046419);

INSERT INTO study_group_members(study_group_member_id, study_group_id, student_id, owner) VALUES
(1, 1, 1, TRUE),
(2, 1, 2, FALSE);

