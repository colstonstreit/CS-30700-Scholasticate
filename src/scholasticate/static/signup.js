function passwordStrength(strength) {
  if (strength > 55) return "Excellent!";
  if (strength > 35) return "Moderate.";
  if (strength > 15) return "Weak.";
  return "Very weak.";
}

function checkValidEmailAndPassword(e) {
  document.getElementById("Submit").disabled = !(checkValidEmail(e) && checkPassword(e) && checkPasswordConfirmation(e));
}

function checkValidEmail(e) {
  let email = new String(document.getElementById("email").value);
  let emailResult = document.getElementById("emailResult");

  if (getEmailResults(email)) {
    emailResult.innerHTML = `The email address entered is valid!`;
    return true;
  } else {
    emailResult.innerHTML = `The email address entered is not valid.`;
    return false;
  }
}

function getEmailResults(email) {
  const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/
  return emailRegex.test(email)
}

function checkPassword(e) {
  let password = new String(document.getElementById("password").value);
  let result = document.getElementById("passwordResult");

  passwordResults = getPasswordResults(password);

  foundList = passwordResults.descriptions
    .map(desc => `<li>${desc}</li>`)
    .reduce((prev, next) => prev + next);

  result.innerHTML = `Found <br> <ul>${foundList}</ul><b>Score:</b> ${passwordResults.strength}<br>
                      <b>Judgment:</b> ${passwordStrength(passwordResults.strength)}`;
  return passwordResults.valid;
}

function checkPasswordConfirmation(e) {
  let password = new String(document.getElementById("password").value);
  let confirmed_password = new String(document.getElementById("confirm_password").value);
  let result = document.getElementById("passwordResult");
  passwordResults = getPasswordResults(password);

  foundList = passwordResults.descriptions
    .map(desc => `<li>${desc}</li>`)
    .reduce((prev, next) => prev + next);

  if ((confirmed_password != null) && (confirmed_password.localeCompare(password) == 0)) {
    result.innerHTML = `<b>Entered passwords do match!</b><br><br>`;
    result.innerHTML += `Found <br> <ul>${foundList}</ul><b>Score:</b> ${passwordResults.strength}<br>
                      <b>Judgment:</b> ${passwordStrength(passwordResults.strength)}`;
    return passwordResults.valid;
  } else {
    result.innerHTML = `<b>Entered passwords do not match!</b><br><br>`;
    result.innerHTML += `Found <br> <ul>${foundList}</ul><b>Score:</b> ${passwordResults.strength}<br>
                      <b>Judgment:</b> ${passwordStrength(passwordResults.strength)}`;
    return !(passwordResults.valid);
  }
}

function getPasswordResults(password) {

  let foundDescriptions = [`${password.length} ${password.length > 1 || password.length == 0 ? 'Characters' : 'Character'}`];
  let strength = 2 * password.length;

  const checkRegex = (regex, points, desc) => {
    let found = password.match(regex);
    if (found != null) {
      strength += points;
      foundDescriptions.push(desc);
    }
  }

  checkRegex(/.*[A-Z]+.*/g, 5, "Capital Letters");
  checkRegex(/.*[a-z]+.*/g, 5, "Lowercase Letters");
  checkRegex(/.*[0-9]+.*/g, 5, "Numbers");
  checkRegex(/.*[^A-Za-z0-9]+.*/g, 5, "Special Characters");

  satisfiesRequirements = password.length >= 10 && foundDescriptions.length == 5;

  return {
    valid: satisfiesRequirements,
    descriptions: foundDescriptions,
    strength: strength
  };
}