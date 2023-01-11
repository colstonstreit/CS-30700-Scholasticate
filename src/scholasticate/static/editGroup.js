var group = JSON.parse(document.getElementById("group").innerText);

function onLoad() {


    group = JSON.parse(document.getElementById("group").innerText);

    document.getElementById("name").defaultValue = group.name;
    document.getElementById("schedule").defaultValue = group.schedule;
    document.getElementById("descriptionBox").defaultValue = group.description;
    document.getElementById("max_members").defaultValue = group.max_members;
    document.getElementById("latitude").defaultValue = group.latitude;
    document.getElementById("longitude").defaultValue = group.longitude;
    MapManager.zoomTo(group.latitude, group.longitude, 15);

    // Zoom to study group on map and create marker
    marker = MapManager.createMarker(group.latitude, group.longitude, "#FF0000", "<p>Group Location!</p>");
    MapManager.addMarker("group", id = "groupLocation", marker);
    document.getElementById("public").checked = group.public != 0;

    lockCourseDropdown();

}

function lockCourseDropdown() {

    let course = group.course;
    console.log(group);

    let dropdown = document.getElementById("coursesDropdown");

    dropdown.innerHTML += `<option disabled selected value="${course.course_id}">${course.course_name} - ${course.course_title}</option>`
}