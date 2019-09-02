#!/usr/bin/env node
'use strict';

/*
** Simple utility for automatically adding "id"s to data files.
** Adds any missing "id", "resource", and "reference" attributes to objects missing them.
** It will also serve to re-format any file too.
*/

const fs = require('fs');
const {promisify} = require('util');

const args = process.argv.slice(2);
const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);
const INDENTING_LEVEL = 2; // Indent two spaces per style guide.

let resourceName = "Eclipse Phase Second Edition"; // Default
for (let i = args.length - 1; i >= 0; i--) {
	if (args[i] == "--resource") {
		let removed = args.splice(i, 2);
		if (removed.length != 2) {
			console.error("Expected a value after --resource");
			process.exit(-1);
		} else {
			resourceName = removed[1];
		}
	}
}

if (args.length == 0) {
	console.error("Usage: " + __filename + " [--resource 'resource name'] jsonfile [jsonfile...]");
	process.exit(-1);
}

args.forEach(function(fileName) {
	fillMissingIds(fileName).then((newJson) => {
		return writeFileAsync(fileName, newJson);
	}).then(() => {
		console.log(`Updated ${fileName}`);
	}).catch((err) => {
		console.error(`Processing ${fileName} failed:`, err);
	});
});

/** Reads the file, parses, fills in missing UUIDs. */
async function fillMissingIds(fileName) {
	let fileContents = await readFileAsync(fileName);
	let jsonData = JSON.parse(fileContents);

	// Loop thru each data item and figure it out!
	for (let i = jsonData.length - 1; i >= 0; i--) {
		let obj = jsonData[i];
		if (!("resource" in obj) || obj.resource == '') {
			obj.resource = resourceName;
		}
		if (!("reference" in obj)) {
			obj.reference = "";
		}
		if (!("id" in obj) || obj.id == '') {
			obj.id = uuid();
		}
	}

	let newJson = JSON.stringify(jsonData, null, INDENTING_LEVEL);
	return newJson;
}

/** Generate random UUID - https://gist.github.com/jed/982883 */
function uuid(a){return a?(a^Math.random()*16>>a/4).toString(16):([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,uuid)}
