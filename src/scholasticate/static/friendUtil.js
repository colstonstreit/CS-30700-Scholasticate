
function sendFriendRequest(profileID) {
  userID = window.sessionStorage.getItem('userID');
  if (userID == null || userID == profileID) return;

  fetch(`/sendFriendRequest/${profileID}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  }).then(response => response.json())
    .then(response => {
      if (response == 200) {
        alert("Request sent successfully.");
        window.location.reload(false);
      }
    })
    .catch(error => alert(`Request failed: Error: ${error}`));
}

function acceptFriendRequest(profileID) {
  userID = window.sessionStorage.getItem('userID');
  if (userID == null || userID == profileID) return;

  fetch(`/acceptFriendRequest/${profileID}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  }).then(response => response.json())
    .then(response => {
      if (response == 200) {
        alert("Successfully accepted request.");
        window.location.reload(false);
      }
    })
    .catch(error => alert(`Request failed: Error: ${error}`));
}

function rejectFriendRequest(profileID) {
  userID = window.sessionStorage.getItem('userID');
  if (userID == null || userID == profileID) return;

  fetch(`/rejectFriendRequest/${profileID}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  }).then(response => response.json())
    .then(response => {
      if (response == 200) {
        alert("Successfully rejected request.");
        window.location.reload(false);
      }
    })
    .catch(error => alert(`Request failed: Error: ${error}`));
}

function cancelFriendRequest(profileID) {
  userID = window.sessionStorage.getItem('userID');
  if (userID == null || userID == profileID) return;

  fetch(`/cancelFriendRequest/${profileID}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  }).then(response => response.json())
    .then(response => {
      if (response == 200) {
        alert("Successfully cancelled request.");
        window.location.reload(false);
      }
    })
    .catch(error => alert(`Request failed: Error: ${error}`));
}

function removeFriend(profileID) {
  userID = window.sessionStorage.getItem('userID');
  if (userID == null || userID == profileID) return;

  data = { friend1: profileID, friend2: userID };
  fetch(`/removeFriend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  }).then(response => response.json())
    .then(response => {
      if (response == 200) {
        alert("Friend removed successfully.");
        window.location.reload(false);
      }
    })
    .catch(error => alert(`Request failed: Error: ${error}`));
}