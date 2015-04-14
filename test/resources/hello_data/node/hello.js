
/**
 * New node file
 */
var fs = require("fs");
var path = require("path");
var hello = function hello() {
	//bii://data.bmp
	//bii://data.xml
    process.stdout.write(fs.readFileSync(path.resolve(__dirname, "data/data.bmp")).toString()); 
    process.stdout.write(" ");
    process.stdout.write(fs.readFileSync(path.resolve(__dirname, "data/data.xml")).toString()); 
};
exports.hello = hello;
