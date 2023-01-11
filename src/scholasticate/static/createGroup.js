var filteredCourses;

function onLoad() {

    updateUI();
    MapManager.zoomToYou();

}

function updateUI() {
    updateCoursesDropdown();
}

function updateCoursesDropdown() {
    let dropdown = document.getElementById("courseSelect");
    dropdown.innerHTML = "<option disabled selected value>Please select a course</option>";

    let html = "<option disabled selected value>Please select a course</option>";

    let courseFilter = document.getElementById("courseFilter").value;

    var req = new XMLHttpRequest();
    req.addEventListener("load", function() {
        filteredCourses = JSON.parse(this.responseText);
        for (course of filteredCourses) {
            html += `<option value="${course.course_id}">${course.course_name} - ${course.course_title}</option>`;
        }
        dropdown.innerHTML = html;
    });

    req.open("GET", "/searchCourses/" + encodeURIComponent(courseFilter));
    req.send();
}