var port = process.env.PORT || 3000;

var path = require('path');
var express = require('express');
var http = require('http');
var fs = require('fs');

var app = express();


app.use(express.static(__dirname));

function send(res, data, type, next) {
	sendNoNext(res, data, type);
	next();
}

function sendNoNext(res, data, type) {
	// console.error("Type", type);
	try {
		if (!type.startsWith("image/")) {
			res.header("Content-Type", type);
		}
		res.header("Content-Type-Options", "nosniff");
	} catch (e) {
		console.error(e);
	}
	res.send(data);
}

function magic(path, type) {
    query = path.indexOf("?");
    if (query >= 0) {
	    path = path.substr(query);
    }
    var hash = path.indexOf("#");
    if (hash > 0) {
		path = path.substr(hash);
    }
    app.get(path, async function(req, res, next) {
	var url = req._parsedUrl.pathname;
	try {
		while (url.startsWith("/")) {
			url = url.substr(1);
		}
		console.error(req.ip+":  Requested", url);
		url = __dirname+"/"+ url;
		if (fs.existsSync(url)) {
			console.error("Reading", url);
			var data = await fs.promises.readFile(url);
			if (type.startsWith("image") || type.startsWith("audio") || type.startsWith("video")) {
				sendNoNext(res, data, type);
			} else {
				sendNoNext(res, data.toString(), type);
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

magic("*.gif", "image/gif");
magic("*.jpg", "image/jpeg");
magic("*.JPG", "image/jpeg");
magic("*.jpeg", "image/jpeg");
magic("*.png", "image/png");
magic("*.mpg", "video/mpeg");
magic("*.mp4", "video/mp4");
magic("*.ogv", "video/ogg");
magic("*.wav", "audio/wav");
magic("*.mp3", "audio/mpeg3");
magic("*.ply", "application/octet-stream");
magic("*.stl", "application/octet-stream");
magic("*.vs", "x-shader/x-vertex");
magic("*.fs", "x-shader/x-fragment");
// magic("*.vs", "text/plain");//"x-shader/x-vertex");
// magic("*.fs", "text/plain");//"x-shader/x-fragment");
magic("*.js", "text/javascript");
magic("*.py", "text/python");
magic("/dist/*.mjs", "text/javascript");
magic("/src/main/node/*.mjs", "text/javascript");
magic("*.js.map", "application/json");
magic("*.csv", "text/csv");
magic("/*.xhtml", "application/xhtml+xml");
magic("/*.xsd", "application/xml");
magic("/*.html", "text/html");
magic("*.xslt", "text/xsl");
magic("*.css", "text/css");
magic("*.swf", "application/x-shockwave-flash");
magic("/**/schema/*.json", "text/json");
magic("*.x3d", "model/x3d+xml");
magic("*.x3dv", "model/x3d+vrml");
magic("*.wrl", "model/vrml");
magic("*.gltf", "text/json");
magic("*.glb", "application/octet-stream");
magic("*.bin", "application/octet-stream");
/*
magic("*.xml", "text/xml");
*/


http.createServer({
}, app)
.listen(port, '127.0.0.1', function () {
  console.log('Example app listening on port', port, "! Go to http://localhost:"+port+"/");
});
