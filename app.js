// --- START OF FILE app.js ---

var port = process.env.PORT || 3000;

import { dirname } from 'path';
import path from 'path';
import express from 'express';
import fs from 'fs';
import http from 'http';
import { globSync } from 'node:fs';
import { glob } from 'node:fs/promises';
import { fileURLToPath } from 'url';

// import { runAndSend } from './src/main/node/runAndSend';
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

var app = express();
app.use(express.static(__dirname));

function send(res, data, type, next, outfile) {
	sendNoNext(res, data, type, outfile);
	next();
}

function sendNoNext(res, data, type, outfile) {
	// console.error("Type", type);
	try {
		if (!type.startsWith("image/")) {
			res.header("Content-Type", type);
		}
		res.header("Content-Type-Options", "nosniff");
	} catch (e) {
		console.error(e);
	}
	console.log("    Replied with File", outfile);
	res.send(data);
}

function magic(path, type) {
    // The path argument to magic() is now a regular expression, so string operations are not needed.
    app.get(path, async function(req, res, next) {
	res.setHeader('Content-Type', type);
	var url = req.path;
	try {
		while (url.startsWith("/")) {
			url = url.substr(1);
		}
		console.log(req.ip+":  Requested", url);
		var wind = url.indexOf("www.web3d.org");
		if (wind >= 0) {
			url = url.substring(wind);
			var cwind = config.examples().indexOf("www.web3d.org");
			url = config.examples().substr(0, cwind) + url;
		} else {
			url = __dirname+"/"+ url;
		}
		if (fs.existsSync(url)) {
			console.log("Reading", url);
			var data = await fs.promises.readFile(url);
			if (type.startsWith("image") || type.startsWith("audio") || type.startsWith("video")) {
				sendNoNext(res, data, type, url);
			} else {
				sendNoNext(res, data.toString(), type, url);
			}
		} else {
			console.error("File does not exist", url);
		}
	} catch (e) {
		console.error(e, "Couldn't read", url);
		next();
	}
    });
}

// EXPRESS 5 FIX: All 'magic' calls and app.get calls below now use Regular Expressions for routing.
magic(/.*\.gif$/i, "image/gif");
magic(/.*\.jpg$/i, "image/jpeg");
magic(/.*\.jpeg$/i, "image/jpeg");
magic(/.*\.png$/i, "image/png");
magic(/.*\.mpg$/i, "video/mpeg");
magic(/.*\.mp4$/i, "video/mp4");
magic(/.*\.ogv$/i, "video/ogg");
magic(/.*\.wav$/i, "audio/wav");
magic(/.*\.mp3$/i, "audio/mpeg3");
magic(/.*\.ply$/i, "application/octet-stream");
magic(/.*\.stl$/i, "application/octet-stream");
magic(/.*\.rb$/i, "application/octet-stream");
magic(/.*\.clj$/i, "application/octet-stream");
magic(/.*\.vs$/i, "x-shader/x-vertex");
magic(/.*\.fs$/i, "x-shader/x-fragment");
magic(/.*\.js$/i, "text/javascript");
magic(/.*\.py$/i, "text/python");
magic(/\/dist\/.*\.mjs$/i, "text/javascript");
magic(/\/src\/main\/node\/.*\.mjs$/i, "text/javascript");
magic(/.*\.js\.map$/i, "application/json");
magic(/.*\.csv$/i, "text/csv");
magic(/.*\.xhtml$/i, "application/xhtml+xml");
magic(/.*\.xsd$/i, "application/xml");
magic(/.*\.html$/i, "text/html");
magic(/.*\.xslt$/i, "text/xsl");
magic(/.*\.css$/i, "text/css");
magic(/.*\.swf$/i, "application/x-shockwave-flash");
magic(/.*\/schema\/.*\.json$/i, "text/json");
magic(/.*\.x3d$/i, "model/x3d+xml");
magic(/.*\.x3dv$/i, "model/x3d+vrml");
magic(/.*\.wrl$/i, "model/vrml");
magic(/.*\.gltf$/i, "text/json");
magic(/.*\.glb$/i, "application/octet-stream");
magic(/.*\.bin$/i, "application/octet-stream");
magic(/.*\.zip$/i, "application/zip");
magic(/.*\.wasm$/i, "application/octet-stream");


http.createServer({}, app) .listen(port, '127.0.0.1', function () {
  console.log('Example app listening on port', port, "! Go to http://localhost:"+port+"/ in your browser.  CTRL-Click on the previous link, or copy and paste the link.  Hint.  Only FreeWRL works right now.  See README.md");
});
