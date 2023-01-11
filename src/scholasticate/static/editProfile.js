var filteredCourses = [];
var selectedCourses;
var pastCourses;
var allClothingItems;
var allTimeAvailabilities;

function onLoad() {
  allClothingItems = JSON.parse(document.getElementById("allClothingItems").innerText);
  allTimeAvailabilities = JSON.parse(document.getElementById("availabilityList").innerText);
  var studentInfo = JSON.parse(document.getElementById("studentInfo").innerText);
  selectedCourses = UserInfo.currentCourses;
  pastCourses = UserInfo.pastCourses;

  document.getElementById("name").defaultValue = studentInfo.student.name;
  document.getElementById("bio").defaultValue = studentInfo.student.bio;
  if (studentInfo.profile_picture == null) {
    document.getElementById("profilePicture").filename = 'img/defaultProfilePic.png'
    document.getElementById("profilePicture").src = "/static/img/defaultProfilePic.png";
  } else {
    document.getElementById("profilePicture").src = studentInfo.profile_picture.picture_string;
    document.getElementById("basePhotoString").defaultValue = studentInfo.profile_picture.picture_string;
  }
  document.getElementById('newAvailabilities').defaultValue = JSON.stringify(allTimeAvailabilities);
  document.getElementById('newClothingItems').defaultValue = JSON.stringify(allClothingItems);

  initializeWardrobeList();
  initializeAvailabilityTable();
  updateAvailabilityTable();
  updateUI();
}

function updateUI() {
  updateSelectedCoursesList();
  updateCourseFormFieldText();
  updateCourseSelectDropdown();
}

function convertImage(file) {
  var reader = new FileReader();
  reader.onloadend = function() {
    console.log('RESULT', reader.result);
    document.getElementById('basePhotoString').defaultValue = reader.result;
  }
  reader.readAsDataURL(file);
}

function updateCourseFormFieldText() {
  let courseIds = [];
  for (let course of selectedCourses) {
    courseIds.push(course.course_id);
  }
  document.getElementById("courseIds").defaultValue = JSON.stringify(courseIds);

  let pastCourseIds = [];
  for (let course of pastCourses) {
    pastCourseIds.push(course.course_id);
  }
  document.getElementById("courseHistoryIds").defaultValue = JSON.stringify(pastCourseIds);
}

function updateCourseSelectDropdown() {
  let dropdown = document.getElementById("courseSelect");
  dropdown.innerHTML = "<option disabled selected value>Please select a course</option>";

  let html = "<option disabled selected value>Please select a course</option>";
  let courseFilter = document.getElementById("courseFilter").value;

  var req = new XMLHttpRequest();
  req.addEventListener("load", function () {
    filteredCourses = JSON.parse(this.responseText);
    for (course of filteredCourses) {
      html += `<option value="${course.course_id}">${course.course_name} - ${course.course_title}</option>`;
    }
    dropdown.innerHTML = html;
  });

  req.open("GET", "/searchCourses/" + encodeURIComponent(courseFilter));
  req.send();
}

function initializeWardrobeList() {
  let list = document.getElementById("wardrobeList");
  list.innerHTML = "<tr><th colspan='4'>Wardrobe</th></tr>";
  list.innerHTML += `<tr><td>Article Type</td><td>Brand</td><td>Color</td></tr>`;
  let redRange = document.getElementById("redSlider");
  let greenRange = document.getElementById("greenSlider");
  let blueRange = document.getElementById("blueSlider");
  redRange.value = 0;
  greenRange.value = 0;
  blueRange.value = 0;
  count = 0;
  for (let item of allClothingItems) {
    item.temp_id = count++;
    let color = convertColorToHex(parseInt(item.color_red), parseInt(item.color_green), parseInt(item.color_blue))
    list.innerHTML += `<tr><td>${item.article}</td><td>${item.brand}</td><td bgcolor=${color}></td><td><button type="button" onclick="removeWardrobeItem(${item.temp_id})">Remove</button></td></tr>`
  }
}

function resetWardrobeList() {
  let list = document.getElementById("wardrobeList");
  list.innerHTML = "<tr><th colspan='4'>Wardrobe</th></tr>";
  list.innerHTML += `<tr><td>Article Type</td><td>Brand</td><td>Color</td></tr>`;
  let redRange = document.getElementById("redSlider");
  let greenRange = document.getElementById("greenSlider");
  let blueRange = document.getElementById("blueSlider");
  redRange.value = 0;
  greenRange.value = 0;
  blueRange.value = 0;
  updateRedText(0);
  updateGreenText(0);
  updateBlueText(0);
  for (let item of allClothingItems) {
    let color = convertColorToHex(parseInt(item.color_red), parseInt(item.color_green), parseInt(item.color_blue))
    list.innerHTML += `<tr><td>${item.article}</td><td>${item.brand}</td><td bgcolor=${color}></td><td><button type="button" onclick="removeWardrobeItem(${item.temp_id})">Remove</button></td></tr>`
  }
  document.getElementById("newClothingItems").defaultValue = JSON.stringify(allClothingItems);
}

function updateWardrobeList() {
  let colorText = document.getElementById("colorText");
  let clothingName = document.getElementById("clothingName");
  let clothingBrand = document.getElementById("clothingBrand");
  let list = document.getElementById("wardrobeList");
  let redText = document.getElementById("redText");
  let greenText = document.getElementById("greenText");
  let blueText = document.getElementById("blueText");
  let newClothingObject = {};
  newClothingObject['color_red'] = redText.innerText;
  newClothingObject['color_green'] = greenText.innerText;
  newClothingObject['color_blue'] = blueText.innerText;
  newClothingObject['article'] = clothingName.value;
  newClothingObject['brand'] = clothingBrand.value;
  newClothingObject['student_id'] = UserInfo.student.student_id;
  newClothingObject['temp_id'] = allClothingItems.length;
  allClothingItems.push(newClothingObject);
  list.innerHTML += `<tr><td>${clothingName.value}</td><td>${clothingBrand.value}</td><td bgcolor=${colorText.innerText}></td><td><button type="button" onclick="removeWardrobeItem(${newClothingObject['temp_id']})">Remove</button></td></tr>`
  document.getElementById("newClothingItems").defaultValue = JSON.stringify(allClothingItems);
}

function removeWardrobeItem(tempID) {
  let clothingIndex = allClothingItems.findIndex((element) => element['temp_id'] == tempID);
  if (clothingIndex >= 0) {
    allClothingItems.splice(clothingIndex, 1);
    resetWardrobeList();
  }
}

function updateRedText(value) {
  let label = document.getElementById("redText");
  label.innerHTML = value;
}

function updateGreenText(value) {
  let label = document.getElementById("greenText");
  label.innerHTML = value;
}

function updateBlueText(value) {
  let label = document.getElementById("blueText");
  label.innerHTML = value;
}

function updateBoxColor() {
  let redRange = document.getElementById("redSlider");
  let greenRange = document.getElementById("greenSlider");
  let blueRange = document.getElementById("blueSlider");
  hexValueColor = convertColorToHex(parseInt(redRange.value),
                                    parseInt(greenRange.value),
                                    parseInt(blueRange.value));
  let rectangle = document.getElementById("colorPreview");
  rectangle.style.fill = hexValueColor;
  let colorText = document.getElementById("colorText");
  colorText.innerText = hexValueColor;
}

function convertColorToHex(redVal, greenVal, blueVal) {
  redHex = redVal.toString(16);
  if (redHex.length == 1) {
    redHex = "0" + redHex
  }
  greenHex = greenVal.toString(16);
  if (greenHex.length == 1) {
    greenHex = "0" + greenHex
  }
  blueHex = blueVal.toString(16);
  if (blueHex.length == 1) {
    blueHex = "0" + blueHex
  }
  return '#' + redHex + greenHex + blueHex
}

function updateSelectedCoursesList() {
  let list = document.getElementById("selectedCoursesList");
  list.innerHTML = "<tr><th colspan='2'>Selected Courses</th></tr>";
  for (let course of selectedCourses) {
    list.innerHTML += `<tr><td>${course.course_name} - ${course.course_title}</td><td><button type="button" onclick="toggleCourse(${course.course_id})">Remove</button></td></tr>`
  }

  let pastList = document.getElementById("selectedHistoryList");
  pastList.innerHTML = "<tr><th colspan='2'>Course History</th></tr>";
  for (let course of pastCourses) {
    pastList.innerHTML += `<tr><td>${course.course_name} - ${course.course_title}</td><td><button type="button" onclick="removeFromHistory(${course.course_id})">Remove from History</button></td></tr>`
  }
}

function toggleCourse(courseID) {
  let selectedCoursesIndex = selectedCourses.findIndex(courseEntry => courseEntry.course_id == courseID);
  if (selectedCoursesIndex == -1) {
    let filteredCoursesIndex = filteredCourses.findIndex(courseEntry => courseEntry.course_id == courseID);
    if (filteredCoursesIndex != -1) {
      selectedCourses.push(filteredCourses[filteredCoursesIndex]);
    }
  } else {
    let removedCourse = selectedCourses.splice(selectedCoursesIndex, 1)[0];
    pastCourses.push(removedCourse);
  }
  updateUI();
}

function removeFromHistory(courseID) {
  let pastCoursesIndex = pastCourses.findIndex(courseEntry => courseEntry.course_id == courseID);
  if (pastCoursesIndex >= 0) {
    pastCourses.splice(pastCoursesIndex, 1);
    updateUI();
  }
}

availability = {
  "Sunday": [],
  "Monday": [],
  "Tuesday": [],
  "Wednesday": [],
  "Thursday": [],
  "Friday": [],
  "Saturday": []
};

function initializeAvailabilityTable() {
  for (let timeItem of allTimeAvailabilities) {
    let startTime = timeItem.start_time;
    let endTime = timeItem.end_time;
    let timeString = startTime + "-" + endTime;
    availability[timeItem.weekday].push(timeString);
  }
}

function updateAvailabilityTable() {
  let table = document.getElementById("availability");
  table.innerHTML = "";
  let html = table.innerHTML;
  html += `<tr><th colspan="3">Availability</th></tr>`;
  html += `<tr><th>Day</th><th>Times</th></tr>`;
  for (day in availability) {
    html += "<tr>";
    html += `<td>${day}</td>`;
    html += "<td>";
    if (availability[day].length > 0) {
      style = `style="border: 0px solid black; width: 50%;"`;
      html += `<table style="border: 0px solid black; width: 100%;">`;
      for (time of availability[day]) {
        html += `<tr ${style}><td ${style}>${time}</td><td ${style}><button form="none" onclick="removeTime('${day}', '${time}'); return false;">Remove</button></td></tr>`;
      }
      html += `</table>`;
    } else {
      html += "Unavailable";
    }
    html += "</td>"
    html += `</tr>`;
  }
  table.innerHTML = html;
}

function removeTime(day, time) {
  let timeSegments = time.split("-");
  let timeIndex = allTimeAvailabilities.findIndex(timeEntry => timeEntry.weekday == day &&
                                                             timeEntry.start_time == timeSegments[0] &&
                                                             timeEntry.end_time == timeSegments[1]);
  if (timeIndex >= 0) {
    allTimeAvailabilities.splice(timeIndex, 1);
  }
  let index = availability[day].indexOf(time);
  if (index != -1) {
    availability[day].splice(index, 1);
  }
  document.getElementById('newAvailabilities').defaultValue = JSON.stringify(allTimeAvailabilities);
  updateAvailabilityTable();
}

function addTime() {
  let dayDropdown = document.getElementById('day');
  let weekday = dayDropdown.options[dayDropdown.selectedIndex].text.trim();
  startTime = document.getElementById('startTime').value.trim();
  endTime = document.getElementById('endTime').value.trim();

  valid = (new RegExp(/^[0-9]{1,2}\:[0-9]{2}$/gs)).test(startTime);
  valid |= (new RegExp(/^[0-9]{1,2}\:[0-9]{2}$/gs)).test(endTime);
  if (!valid) {
    alert("Times must be in the form of H:MM or HH:MM.")
    return;
  }

  startHour = parseInt(startTime.substring(0, startTime.length - 3));
  startMinute = parseInt(startTime.substring(startTime.length - 2));
  endHour = parseInt(endTime.substring(0, endTime.length - 3));
  endMinute = parseInt(endTime.substring(endTime.length - 2));
  newStartTime = startHour * 100 + startMinute
  newEndTime = endHour * 100 + endMinute

  invalid = isNaN(startHour) || startHour >= 24 || startHour < 0;
  invalid |= isNaN(startMinute) || startMinute >= 60 || startMinute < 0;
  invalid |= isNaN(endHour) || endHour >= 24 || endHour < 0;
  invalid |= isNaN(endMinute) || endMinute >= 60 || endMinute < 0;
  invalid |= startHour > endHour || (startHour == endHour && startMinute >= endMinute);

  if (invalid) {
    alert("Your times are invalid!");
    return;
  }

  // TODO: UNION TIMES HERE
  conflictingInside = [];
  conflictingLeft = [];
  conflictingRight = [];
  for (let timeItem of availability[weekday]) {
    timeItemSegments = timeItem.split("-");
    startTimeSegments = timeItemSegments[0].split(":");
    endTimeSegments = timeItemSegments[1].split(":");
    startTimeInt = parseInt(startTimeSegments[0] + startTimeSegments[1]);
    endTimeInt = parseInt(endTimeSegments[0] + endTimeSegments[1]);
    if (newStartTime < startTimeInt && newEndTime > endTimeInt) {
      conflictingInside.push(timeItem);
    } else if (newStartTime < endTimeInt && newEndTime > endTimeInt) {
      conflictingLeft.push(timeItem);
    } else if (newEndTime > startTimeInt && newStartTime < startTimeInt) {
      conflictingRight.push(timeItem);
    }
  }
  console.log(conflictingInside, conflictingLeft, conflictingRight)
  if (conflictingInside.length == 1) {
    removeTime(weekday, conflictingInside[0])
  }
  if (conflictingLeft.length == 1) {
    startTime = conflictingLeft[0].split("-")[0]
    removeTime(weekday, conflictingLeft[0])
  }
  if (conflictingRight.length == 1) {
    endTime = conflictingRight[0].split("-")[1]
    removeTime(weekday, conflictingRight[0])
  }

  time = startTime + '-' + endTime;
  availability[weekday].push(time);
  newAvailabilityObject = {};
  newAvailabilityObject['weekday'] = weekday;
  newAvailabilityObject['start_time'] = startTime;
  newAvailabilityObject['end_time'] = endTime;
  newAvailabilityObject['student_id'] = UserInfo.student.student_id;
  newAvailabilityObject['temp_id'] = allTimeAvailabilities.length;
  allTimeAvailabilities.push(newAvailabilityObject)
  document.getElementById('newAvailabilities').defaultValue = JSON.stringify(allTimeAvailabilities);
  updateAvailabilityTable();
}
