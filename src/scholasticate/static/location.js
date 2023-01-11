/////////////////////////// MAP STUFF ///////////////////////////

// Should really hide this token somewhere
mapboxgl.accessToken = 'pk.eyJ1IjoiY3RzbWFyaW8iLCJhIjoiY2t1OGFiaDh5NXI5bTJwbzJiY2FmMDl2MyJ9.O2x1teMkEO1k1t4VWI_UkQ';

var MapManager = {
  _map: new mapboxgl.Map({
    container: 'map', // container ID
    style: 'mapbox://styles/mapbox/streets-v11', // style URL
    center: [0, 0], // starting position [lng, lat]
    zoom: 1 // starting zoom
  }),
  _mapMarkers: [],
  lastPosClicked: null,
  zoomTo: function(latitude, longitude, zoom = this._map.getZoom()) {
    this._map.flyTo({ center: [longitude, latitude], zoom: zoom, duration: 1500 })
  },
  zoomIn: function() { this._map.zoomIn({duration: 500}) },
  zoomOut: function() { this._map.zoomOut({duration: 500}) },
  zoomToYou: async function() {
    let pos = await requestMyLocation();
    this.zoomTo(pos.coords.latitude, pos.coords.longitude);
  },
  clearMarkers: function() {
    for (let i = this._mapMarkers.length - 1; i >= 0; i--) {
      this._mapMarkers[i].marker.remove();
    }
    this._mapMarkers.length = 0;
  },
  addMarker: function(type, id, marker) {
    marker.addTo(this._map);
    this._mapMarkers.push({
      "type": type,
      "id": id,
      "marker": marker
    });
  },
  createMarker: function(latitude, longitude, color, popupHTML) {
    return new mapboxgl.Marker({ color: color })
              .setLngLat([longitude, latitude])
              .setPopup(new mapboxgl.Popup().setHTML(popupHTML));
  },
  createMarkerWithIcon: function(latitude, longitude, iconLink, popupHTML) {
    const el = document.createElement('div');
    el.style.backgroundImage = `url(${iconLink})`;
    el.style.width = `40px`;
    el.style.height = `40px`;
    el.style.backgroundSize = '100%';
    el.style.display = `block`;
    el.style.border = `none`;
    el.style.borderRadius = `50%`;
    el.style.cursor = `pointer`;
    el.style.padding = `0`;
    return new mapboxgl.Marker(el)
      .setLngLat([longitude, latitude])
      .setPopup(new mapboxgl.Popup().setHTML(popupHTML));
  }
}
MapManager._map.on('zoomend', () => window.sessionStorage.setItem("mapBounds", JSON.stringify(MapManager._map.getBounds())))
MapManager._map.on('dragend', () => window.sessionStorage.setItem("mapBounds", JSON.stringify(MapManager._map.getBounds())))
if ((boundsJSON = window.sessionStorage.getItem("mapBounds")) != null) {
  bounds = JSON.parse(boundsJSON);
  MapManager._map.fitBounds([[bounds._sw.lng, bounds._sw.lat], [bounds._ne.lng, bounds._ne.lat]], {duration: 0});
}
MapManager._map.on('click', e => {
  lastPosClicked = {latitude: e.lngLat.lat, longitude: e.lngLat.lng};
  latBox = document.getElementById("latitude");
  longBox = document.getElementById("longitude");
  if (latBox != null && longBox != null) {
    latBox.value = lastPosClicked.latitude;
    longBox.value = lastPosClicked.longitude;
    MapManager.clearMarkers();
    marker = MapManager.createMarker(latBox.value, longBox.value, "#FF0000", "<p>Group Location!</p>");
    MapManager.addMarker("group", id="groupLocation", marker);
    MapManager.zoomTo(latBox.value, longBox.value);
  }
});

/////////////////////////// LOCATION STUFF ///////////////////////////

function refreshLocations() {

  // Update current user's location
  updateMyLocation();

  let id = window.sessionStorage.getItem("userID");
  if (id == null) return;

  var friendsJSON = JSON.parse(document.getElementById("friends").innerText);
  var friends = [];
  for (friendJSON of friendsJSON) {
    friends.push(JSON.parse(friendJSON));
  }
  var friendRequestsJSON = JSON.parse(document.getElementById("friendRequests").innerText);
  var sentFriendRequests = [];
  var receivedFriendRequests = [];
  for (friendRequestJSON of friendRequestsJSON) {
    friendRequest = JSON.parse(friendRequestJSON);
    if (friendRequest.sender_student_id == id) sentFriendRequests.push(friendRequest);
    else if (friendRequest.recipient_student_id == id) receivedFriendRequests.push(friendRequest);
  }

  filters = []
  nameSearchQuery = document.getElementById("query").value;
  distanceSearchQuery = document.getElementById("distanceQuery").value;
  if (nameSearchQuery != "") filters.push(entity => entity.name.indexOf(nameSearchQuery) != -1);
  if (distanceSearchQuery != "Anywhere") filters.push(entity => entity.distance < distanceSearchQuery);

  // Grab other users' and groups' locations and distances from database and update them in the table and on the map!
  getUsersAndGroups(filters, false, true).then(entities => {

    if (entities == null) return;

    table = document.getElementById("userListTable");
    document.getElementById("userList").style.display = "initial";
    table.innerHTML = "<tr><th>Type</th><th>Name</th><th>Distance (km)</th></tr>"
    id = window.sessionStorage.getItem("userID");

    // Clear map
    MapManager.clearMarkers();

    for (entity of entities) {
      distance = Math.round(entity.distance * 100) / 100;

      if (entity.type == "student") {
        student = entity;
        // Figure out if this student is a friend
        isFriend = false;
        for (friend of friends) {
          if (student.student_id == friend.student_id) {
            isFriend = true;
            break;
          }
        }
        receivedFriendRequestFromStudent = false;
        for (friendRequest of receivedFriendRequests) {
          if (friendRequest.sender_student_id == student.student_id) {
            receivedFriendRequestFromStudent = true;
            break;
          }
        }
        sentFriendRequestToStudent = false;
        for (friendRequest of sentFriendRequests) {
          if (friendRequest.recipient_student_id == student.student_id) {
            sentFriendRequestToStudent = true;
            break;
          }
        }

        // Add to table if student isn't you
        if (entity.student_id != id) {
          if (isFriend) {
            table.innerHTML += `<tr><td>Student</td><td><a style="color: green;" href="/profile/${student.student_id}">${student.name} (Friend)</a></td><td>${distance}</td>`;
          } else {
            table.innerHTML += `<tr><td>Student</td><td><a href="/profile/${student.student_id}">${student.name}</a></td><td>${distance}</td>`;
          }
        }
      } else if (entity.type == "group") {
        group = entity;
        table.innerHTML += `<tr><td>Group</td><td><a href="/group/${group.study_group_id}">${group.name}</a></td><td>${distance}</td>`;
      }

      // If entity has a location, add to map
      if (entity.latitude != null && entity.longitude != null) {

        popupHTML = "";

        if (entity.type == "student") {
          student = entity;

          markerColor = "";

          if (student.picture_string != undefined && student.picture_string != "") {
            popupHTML += `<img width="96" height="96" src="${student.picture_string}" alt="Profile Picture">`;
          } else {
            popupHTML += `<img width="96" height="96" src="/static/img/defaultProfilePic.png">`
          }

          if (student.student_id == id) {
            markerColor = "#FF0000"; // you are red
            popupHTML += `<p><a href="/profile/${student.student_id}"><b>You!</b></a></p>`;
          } else if (isFriend) {
            markerColor = "#00FF00"; // friends are green
            popupHTML += `<p><a href="/profile/${student.student_id}"><b>${student.name} (Friend)</b></a></p>`;
          } else {
            markerColor = "#0000FF"; // others are blue
            popupHTML += `<p><a href="/profile/${student.student_id}"><b>${student.name}</b></a></p>`;
          }
          popupHTML += `<p>${student.bio}</p>`;
          if (student.student_id != id) {
            popupHTML += `<p><i>${distance} km away</i></p>`
          }

          if (isFriend) {
            popupHTML += `<button type="button" onclick="removeFriend(${student.student_id});">Remove Friend</button>`;
          } else if (sentFriendRequestToStudent) {
            popupHTML += `<button type="button" onclick="cancelFriendRequest(${student.student_id});">Cancel Friend Request</button>`;
          } else if (receivedFriendRequestFromStudent) {
            popupHTML += `<button type="button" onclick="acceptFriendRequest(${student.student_id});">Accept Friend Request</button>`;
            popupHTML += `<button type="button" onclick="rejectFriendRequest(${student.student_id});">Reject Friend Request</button>`;
          } else if (student.student_id != id) {
            popupHTML += `<button type="button" onclick="sendFriendRequest(${student.student_id});">Add Friend</button>`;
          }

          if (student.student_id != id) {
            popupHTML += `<a href="/messages/user/${student.student_id}"><button type="button">Send Message</button></a>`;
          }

          MapManager.addMarker("student", student.student_id, MapManager.createMarker(student.latitude, student.longitude, markerColor, popupHTML));

        } else if (entity.type == "group") {
          group = entity;
          popupHTML = `<p><a href="/group/${group.study_group_id}"><b>${group.name}</b></a></p>`;
          popupHTML += `<p>${group.description}</p>`;
          MapManager.addMarker("group", group.study_group_id,
            MapManager.createMarkerWithIcon(group.latitude, group.longitude, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSHrKdzjVqbqBKyFWmq2XzN1tN16OrHFdLuYQ&usqp=CAU", popupHTML));
        }

      }
    }
  });
}

// Updates the global position variable. I can't figure out how to make it synchronous so I can just return it.
function updateMyLocation() {
  requestMyLocation()
    .then(pos => {
      document.getElementById("yourLocation").innerHTML = pos.coords.latitude + ", " + pos.coords.longitude;
      window.localStorage.setItem("LocationLastUpdated", new Date().toUTCString());
      document.getElementById("lastUpdated").innerHTML = "Location last updated: " + window.localStorage.getItem("LocationLastUpdated");

      // Send location info to server
      userID = window.sessionStorage.getItem("userID");
      if (userID == null) {
        MapManager.clearMarkers();
        MapManager.addMarker("student", "guest", MapManager.createMarker(pos.coords.latitude, pos.coords.longitude, "#FF0000", `<p>You!</p>`));
        return;
      }

      const data = { latitude: pos.coords.latitude,
                     longitude: pos.coords.longitude };

      fetch(`/setLocation/${userID}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      }).then(response => response.json())
        .catch(error => console.error('Error:', error));

    })
    .catch((err) => {
      console.error(err.message);
    });
}

function requestMyLocation() {
  let options = {
    enableHighAccuracy: true,
    timeout: 5000,   // time in millis when error callback will be invoked
    maximumAge: 0,      // max cached age of gps data, also in millis
  };

  return new Promise(function (resolve, reject) {
    navigator.geolocation.getCurrentPosition(
      pos => { resolve(pos); },
      err => { reject(err); },
      options);
  });
}
