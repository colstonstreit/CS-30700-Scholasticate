var fs = require('fs');

function assertEqual(actual, expected){
	if(actual === expected){
		//do nothing
	}
	else{
		throw "Test Failure: " + actual + " does not equal " + expected;
	}
}

function assertTrue(input){
	assertEqual(true, input);
}

function assertFalse(input){
	assertEqual(false, input);
}

const test_directory = __dirname + "/";
const src_directory = test_directory + "../";
const static_directory = src_directory + "scholasticate/static/";

const files = fs.readdirSync(test_directory);

console.log("Running JS tests.");
for(var i = 0; i < files.length; i++){
	const file = files[i];
	if(file.match('^test.*\\.js$')){
		process.stdout.write("  Running test " + file + ". ");
		eval(fs.readFileSync(test_directory + file).toString());
		console.log("Passed!");
	}
}
console.log("All JS tests passed!");

