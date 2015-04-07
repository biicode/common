var hello = require("./hello");
%INCLUDE_EXTERNAL_PRETTY%

/**
 * New node file
 */
var pretty = function pretty() {
	process.stdout.write("* ");
	hello.hello();
	process.stdout.write(" *\n");
	
	%CALL_EXTERNAL_PRETTY%
};
exports.pretty = pretty;