function searchQueryByInput() {
  var input = document.getElementById(".searchPrompt").value;
  var friendQualifier = document.querySelector('.friendCheckbox').checked;
  var nameQualifier = document.querySelector('.nameCheckbox').checked;
  var schoolQualifier = document.querySelector('.schoolCheckbox').checked;
  var filteredUserList = [];

  if (friendQualifier) {
    // getFriendList from current user, store in filteredUserList
  } else {
    filteredUserList = getUserList();
  }
  if (nameQualifier) {
    filteredUserList = searchByName(input, filteredUserList);
  } else if (schoolQualifier) {
    filteredUserList = searchBySchool(input, filteredUserList);
  }
  return filteredUserList;
}

function searchByName(nameInput, originalUserList) {
  var filteredUserList = [];
  for (const userElement of originalUserList) {
    const userGivenName = userElement.getGivenName()
    if (userGivenName.includes(nameInput)) {
      filteredUserList.push(userElement)
    }
  }
  return filteredUserList;
}

function searchBySchool(schoolInput, originalUserList) {
  var filteredUserList = [];
  for (const userElement of originalUserList) {
    const userSchool = userElement.getSchool()
    if (userSchool.includes(schoolInput)) {
      filteredUserList.push(userElement)
    }
  }
  return filteredUserList;
}

function getUsersAndGroups(filters = [], changeToMiles = false, requireSharing = false) {
  return fetch(`/getUsersAndGroups/${window.sessionStorage.getItem('userID')}?require_sharing=${requireSharing}`)
    .then(data => data.json())
    .then(entityDistanceJSONList => {
      let list = [];
      for (entityDistanceJSON of entityDistanceJSONList) {
        entity = JSON.parse(entityDistanceJSON["entityInfo"]);
        entity.distance = entityDistanceJSON["distance"];
        entity.type = entityDistanceJSON["type"];
        if (changeToMiles) entity.distance *= 0.621371;
        list.push(entity);
      }

      let filteredList = filter(list, filters);
      return filteredList;
    })
    .catch(err => console.log(err));
}

function filter(list, filters) {
  let filteredList = [];
  for (entity of list) {
    if (entity.type == "student" && entity.student_id == window.sessionStorage.getItem("userID")) {
      filteredList.push(entity);
      continue;
    }
    passesFilters = true;
    for (f of filters) {
      passesFilters = f(entity);
      if (passesFilters == false) break;
    }
    if (passesFilters) filteredList.push(entity);
  }

  return filteredList;
}

function getCourseList(schoolName) {
  schoolID = getSchoolID(schoolName);
  return schoolID;

  // Retrieve Class List from Database
}
