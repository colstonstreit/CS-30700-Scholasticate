function computeCompatabilityScores() {
  // Array will store tuples of form: {otherUserID, score}
  var relativeUserScores = new Array();

  // Parsing through each profile and computing the compatability score
  // Each score is calcuated based on course similarity and [current relative distance?]

  userCurrentCourseIDs = [];
  for (currentCourse of UserInfo.currentCourses) {
    userCurrentCourseIDs.push(currentCourse.course_id);
  }
  userPastCourseIDs = [];
  for (pastCourse of UserInfo.pastCourses) {
    userPastCourseIDs.push(pastCourse.course_id);
  }

  var profilesJSON = JSON.parse(document.getElementById("onlineProfiles").innerText);
  for (profileJSON of profilesJSON) {
    profile = JSON.parse(profileJSON);
    scoreTuple = [profile, 0.0];
    if (UserInfo.id != profile.student_id) {
      otherCurrentCourseIDs = [];
      for (otherCurrentCourse of profile.currentCourses) {
        otherCurrentCourseIDs.push(JSON.parse(otherCurrentCourse).course_id);
      }
      otherPastCourseIDs = [];
      for (otherPastCourse of profile.pastCourses) {
        otherPastCourseIDs.push(JSON.parse(otherPastCourse).course_id);
      }

      for (otherCurrentID of otherCurrentCourseIDs) {
        for (userCurrentID of userCurrentCourseIDs) {
          if (otherCurrentID == userCurrentID) {
            scoreTuple[1] += 1.0;
          }
        }
        for (userPastID of userPastCourseIDs) {
          if (otherCurrentID == userPastID) {
            scoreTuple[1] += 0.25;
          }
        }
      }
      for (otherPastID of otherPastCourseIDs) {
        for (userCurrentID of userCurrentCourseIDs) {
          if (otherPastID == userCurrentID) {
            scoreTuple[1] += 0.75;
          }
        }
        for (userPastID of userPastCourseIDs) {
          if (otherPastID == userPastID) {
            scoreTuple[1] += 0.25;
          }
        }
      }
      relativeUserScores.push(scoreTuple);
    }
  }
  maxUserScores = getMaxUserScores(relativeUserScores);
  suggestionTable = document.getElementById("suggestionList");
  let numItems = 0;
  for (let item of maxUserScores) {
    if (item == null) continue;
    suggestionProfile = item[0];
    if (UserInfo.id != suggestionProfile.student_id) {
      suggestionTable.innerHTML += `<li>
      ${suggestionProfile.name} <form action="/profile/${suggestionProfile.student_id}"><input type="submit" value="Visit Student!" /></form>
      </li>`;
      numItems++;
    }
  }
  if (numItems == 0) {
    document.getElementById("friendSuggestionsDiv").innerHTML += "There's nobody online to recommend!";
  }
}

function getMaxUserScores(relativeUserScores) {
  var maxScoreElements = [];
  if (relativeUserScores.length >= 3) {
    for (let i = 0; i < 3; i++) {
      let currentMax = -1;
      let currentMaxElement = null;
      for (let scoreElement of relativeUserScores) {
        if (compareUserScores(currentMax, scoreElement) == 1) {
          currentMax = scoreElement[1];
          currentMaxElement = scoreElement;
        }
      }
      maxScoreElements.push(currentMaxElement);
      const index = relativeUserScores.indexOf(currentMaxElement);
      if (index > -1) {
        relativeUserScores.splice(index, 1);
      }
    }
  } else {
    for (let i = 0; i <= relativeUserScores.length; i++) {
      let currentMax = -1;
      let currentMaxElement = null;
      for (let scoreElement of relativeUserScores) {
        if (compareUserScores(currentMax, scoreElement) >= 0) {
          currentMax = scoreElement[1];
          currentMaxElement = scoreElement;
        }
      }
      maxScoreElements.push(currentMaxElement);
      const index = relativeUserScores.indexOf(currentMaxElement);
      if (index > -1) {
        relativeUserScores.splice(index, 1);
      }
    }
  }
  return maxScoreElements;
}

function compareUserScores(scoreA, scoreB) {
  if (scoreA == scoreB[1]) { return 0; }
  return scoreA < scoreB[1] ? 1 : -1
}