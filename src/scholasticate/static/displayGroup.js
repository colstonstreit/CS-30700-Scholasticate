var group;
var membersJSON;
var members;
var invite;
var owner;
var membersListString;
var isMember;
var isOwner;
var hasInvite;


function onLoad() {

    if (/Android|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent)) {
        document.getElementById("body").innerHTML += "<div style='color:red; position:absolute; top:3%; left: 35%; font-size:20px;'>Turn your device sideways for best viewing experience</div>";
    }

    userID = window.sessionStorage.getItem('userID');

    group = JSON.parse(document.getElementById("group").innerText);
    owner = JSON.parse(document.getElementById("owner").innerText);
    membersJSON = JSON.parse(document.getElementById("members").innerText);

    invite = document.getElementById("invite").innerText;
    members = [];
    hasInvite = false;

    if (invite != "") {
        hasInvite = true;
        invite = JSON.parse(invite);
    }

    updateMembersList();

    isOwner = false;
    if (owner.student_id == userID) isOwner = true;

    document.getElementById("name").innerHTML = group.name;
    if (group.description != "") {
        document.getElementById("description").innerHTML = "“" + group.description + "”";
    }
    let course = group.course;
    document.getElementById("course_name").innerHTML = course.course_name + " - " + course.course_title;
    document.getElementById("schedule").innerHTML = group.schedule;
    document.getElementById("latitude").innerHTML = group.latitude;
    document.getElementById("longitude").innerHTML = group.longitude;
    document.getElementById("numMembers").innerHTML = "Members (" + members.length + " / " + group.max_members + ")";
    document.getElementById("ownername").innerHTML += owner.name;

    // Zoom to study group on map and create marker
    MapManager.zoomTo(group.latitude, group.longitude, 18);
    marker = MapManager.createMarker(group.latitude, group.longitude, "#FF0000", "<p>Group Location!</p>");
    MapManager.addMarker("group", id = "groupLocation", marker);

    addButtons();


}

function addButtons() {
    div = document.getElementById("PHbuttonsBox");

    if (!isMember && group.public == 1) {
        div.innerHTML += `<br><br><form action="` + group.study_group_id + `/join" method="POST"><input type="submit" id="PHbutton" name="join" value="Join Group"/></form>`;
    } else if (!isMember && invite != null && invite != "") {
        div.innerHTML += `<br><br><form action="` + group.study_group_id + `/acceptInvite" method="POST"><input type="submit" name="accept" value="Accept Invite"/></form>`;
        div.innerHTML += `<form action="` + group.study_group_id + `/rejectInvite" method="POST"><input type="submit" name="reject" value="Reject Invite"/></form>`;
    } else if (isOwner) {
        div.innerHTML += `<br><form action="` + group.study_group_id + `/edit" method="GET"><input type="submit" id="PHbutton" name="edit" value="Edit Group"/></form>`;
    } else if (isMember) {
        div.innerHTML += `<br><form action="` + group.study_group_id + `/leave" method="POST"><input type="submit" id="PHbutton" name="leave" value="Leave Group"/></form>`;
    }
}

function updateMembersList() {
    isMember = false;
    membersListString = "";
    for (memberJSON of membersJSON) {
        member = JSON.parse(memberJSON);
        members.push(member);

        if (userID != null && member.student_id == userID) isMember = true;
        div = document.getElementById("membersList");
        membersListString += member.name + ", "
    }

    membersListString = membersListString.substr(0, membersListString.length - 2);
    div.innerHTML = membersListString;
}