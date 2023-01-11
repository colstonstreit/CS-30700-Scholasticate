var group;
var membersJSON;
var select;



function onLoad() {

    group = JSON.parse(document.getElementById("group").innerText);
    membersJSON = JSON.parse(document.getElementById("members").innerText);
    select = document.getElementById("groupMembers");

    for (memberJSON of membersJSON) {
        var member = JSON.parse(memberJSON);
        var memberOption = document.createElement("option");
        memberOption.value = member.student_id;
        memberOption.text = member.name;
        select.add(memberOption, null);
    }

}