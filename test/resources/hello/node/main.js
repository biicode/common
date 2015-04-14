var pretty = require("./pretty");
/**
 * New node file
 */
//os.EOL dont work in ubuntu node package version. This line should work in any windows.
var nl = (process.platform === 'win32' ? '\r\n' : '\n')
//For print parameters, testing purpouse
process.argv.forEach(function (val, index, array) {
	process.stdout.write(val + nl);
});

pretty.pretty();