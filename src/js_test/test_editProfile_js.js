//load the file to be tested
eval(fs.readFileSync(static_directory + "editProfile.js").toString());

// course.course_name is course number (CS 307)
// course.course_title is course name (Software Engineering I)

class Course {
  constructor(course_name, course_title) {
    this.course_name = course_name;
    this.course_title = course_title;
  }
}

empty = null;
genericJSONObject = {};
genericJSONObjectMissingTitle = {course_name: "CS 25200"};
genericJSONObjectMissingName = { course_title: "Systems Programming"};

// Use Course constructor to make things easier. Same thing basically
emptyCourse = new Course(null, null);
courseMissingTitle = new Course("STAT 41600", null);
courseMissingName = new Course(null, "Probability");
softwareEng = new Course("CS 30700", "Software Engineering");

