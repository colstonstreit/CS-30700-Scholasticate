function onLoad() {
    var group = JSON.parse(document.getElementById("group").innerText);
    var membersJSON = JSON.parse(document.getElementById("members").innerText);
    var select = document.getElementById("groupMembers");
    for (memberJSON of membersJSON) {
        var member = JSON.parse(memberJSON);
        var memberOption = document.createElement("option");
        memberOption.value = member.student_id;
        memberOption.text = member.name;
        select.add(memberOption, null);
    }
}