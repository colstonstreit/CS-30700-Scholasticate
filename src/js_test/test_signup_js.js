//load the file to be tested
eval(fs.readFileSync(static_directory + "signup.js").toString());

// Passwords must have both lowercase and uppercase letters, a number, a special
// character, and be at least 10 characters
assertFalse(getPasswordResults("A2a?o9sk3").valid);
assertFalse(getPasswordResults("password").valid);
assertFalse(getPasswordResults("Password123").valid);
assertFalse(getPasswordResults("123?#&^(@35").valid);
assertFalse(getPasswordResults("cstreit19").valid);
assertTrue(getPasswordResults("Abc123!!!!").valid);
assertTrue(getPasswordResults("Cstreit19?!&").valid);


