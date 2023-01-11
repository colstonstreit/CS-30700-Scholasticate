function acceptUserUtil(accepted_id) {
    console.log("acceptUserUtil called in acceptedUsersUtil.js!");

    userID = window.sessionStorage.getItem('userID');
    if (userID == null || userID == accepted_id) return;

    fetch(`/acceptUser/${accepted_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    });

    // Redirect window to message
    let redirect = "/messages/user/";
    redirect += data.sender_id;
    window.location.href = redirect;

}