/**
 * EP2-Data Integrity Checker
 * Copyright (CC-BY-NC-SA-4.0)
 *
 * A simple test suite that verifies all data files are valid JSON arrays with ids etc.
*/
const assert = require('assert');
const fs = require('fs');
const UUID_REGEX = /^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$/;

// NOTE: Mocha supports dynamically generated "parameterzied" tests, but not when the test cases are obtained dynamically.
// Therefore we must fetch the list of files to test on synchronously before we begin. Ah well.

var dataFiles = fs.readdirSync(".")
	.filter((name) => name.endsWith('.json'))
	.filter((name) => ['package.json', 'package-lock.json'].indexOf(name) === -1);
console.log(`Found ${dataFiles.length} JSON data files.`);

// Suite 1 - Validate all files have correct JSON syntax!
describe("JSON Data Files", function() {
	var dataContents = new Map();

	describe("Validate JSON Syntax", function() {
		dataFiles.forEach((fileName) => {
			it(`${fileName} has valid JSON syntax`, function(done) {
				fs.readFile(fileName, function(err, data) {
					if (err) done(err);
					dataContents.set(fileName, JSON.parse(data));
					done();
				});
			});
		});
	});

	describe("Data Structure", function() {
		dataFiles.forEach(function(fileName) {
			it(`${fileName} is an Array of Objects with id's`, function() {
				if (!dataContents.has(fileName)) {
					this.skip(); // It didn't parse right
				} else {
					let fileData = dataContents.get(fileName);
					(fileData instanceof Array) || assert.fail(`${fileName}'s root element is not an Array`);
					fileData.forEach((dataItem, i) => {
						("id" in dataItem) || assert.fail(`Item ${i} in ${fileName} missing id`);
						(dataItem.id != '') || assert.fail(`Item ${i} in ${fileName} has blank id`);
						(UUID_REGEX.test(dataItem.id)) || assert.fail(`Item ${i} in ${fileName} is not a UUID`);
					});
				}
			});
		})
	});

	describe("Data Validity", function() {
		it("ids are unique", function() {
			let allDiscoveredIds = new Map();
			dataContents.forEach((fileData, fileName) => {
				if (!(fileData instanceof Array))
					return;
				fileData.forEach((dataItem, i) => {
					if (!("id" in dataItem) || dataItem.id == '') {
						return; // Skip, will have been reported in other tests.
					} else if (allDiscoveredIds.has(dataItem.id)) {
						assert.fail(`Item ${i} in ${fileName} (id=${dataItem.id}) has the same id as ${allDiscoveredIds.get(dataItem.id)}`);
					}
					allDiscoveredIds.set(dataItem.id, `Item ${i} in ${fileName}`);
				});
			});
		});
	});
});
