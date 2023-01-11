function onLoad() {
  var questionList = document.getElementById("question");
  if (questionList == null) {
    return;
  }
  questionList.innerHTML += `<option value="none" selected disabled hidden>Select an Option</option>`;
  questionList.innerHTML += `<option value="What is your mother's maiden name?">What is your mother's maiden name?</option>`;
  questionList.innerHTML += `<option value="What was your first pet's name?">What was your first pet's name?</option>`;
  questionList.innerHTML += `<option value="What is the street you grew up on?">What is the street you grew up on?</option>`;
}

function checkAnswer() {
  let answer = new String(document.getElementById("answer").value);
  document.getElementById("Submit").disabled = !(answer != null);
}