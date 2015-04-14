import unittest
from biicode.common.edition.parsing.nodejs.js_parser import NodeJSParser


texto = """
var moduleA = require( "./module-a.js" );
var moduleB = require( "../../module-b.js" );
var moduleC = require( "/my-library/module-c.js" );

var moduleA = require( "module-a" );
var moduleB = require( "module-b.js" );

var utils = require( "utils" );
"""

complex_test = r'''/*global Buffer require exports console setTimeout */
var net = require("net"),
    util = require("fran/rediss/lib/util.js"),
    Queue = require("fran/rediss/lib/queue.js"),
    to_array = require("fran/rediss/lib/to_array.js"),
    events = require("events"),
    crypto = require("crypto"),
    parsers = [], commands,
    connection_id = 0,
    default_port = 6379,
    default_host = "127.0.0.1";
var a = parsers.push(require("./lib/parser/javascript"));
var c = parsers.push(require("./lib/parser/hiredis"));
'''

require_haml = r'''
var FILE = require("file");
var ASSERT = require("assert");

var Haml = require("luispedraza/haml_js/lib/haml.js");

FILE.glob("test/*.haml").forEach(function(hamlFile) {
exports["test " + hamlFile] = function() {
var scopeFile = hamlFile.replace(/haml$/, "js");
var htmlFile = hamlFile.replace(/haml$/, "html");

var haml = FILE.read(hamlFile);
var expected = FILE.read(htmlFile);
var scope = FILE.exists(scopeFile) ? eval("("+FILE.read(scopeFile)+")") : {};

var js = Haml.compile(haml);
var js_opt = Haml.optimize(js);
var actual = Haml.execute(js_opt, scope.context, scope.locals);
ASSERT.equal(actual.trim(), expected.trim());
}
});

if (module == require.main)
    require("os").exit(require("test").run(exports));
'''

texto2 = """#!/usr/bin/env node

var http = require("http");
var url = require("url");

var _ = require("lodash");
/*var _ = require("pepe");*/
/*var _ = require("pepe2");*/
//var _ = require("pepe3");
var PETFINDER_KEY = "3a62ece31719a64dcf6726980917d7ad";

/**
 * @constructor
 * Our simple petfinder class. For more information on the Petfinder API and all
 * of its options, see http://www.petfinder.com/developers/api-docs
 *
 * The following usage restrictions apply to users of the API:
 * - Total requests per day: 10,000
 * - Records per request: 1,000
 * - Maximum records per search: 2,000
 *
 * @param  {String} key Your Petfinder API key. For more information, see
 * http://www.petfinder.com/developers/api-key
 * @return {Object} A petfinder instance.
 */
function petfinder(key) {
    var self = this;
    self.KEY = key;

    /**
     * @private
     * Internal method which merges the supplied object with a default set of
     * HTTP request parameters for the Petfinder API.
     *
     * @param {Object} opts The object to merge into our default set of HTTP
     * request variables.
     * @return {Object} The merged default and supplied objects.
     */
    self._httpOptions = function (opts) {
        var defaultOpts = {
            "protocol": "http:",
            "host": "api.petfinder.com",
            "query": {
                "format": "json",
                "key": self.KEY
            }
        };
        // Seems underscore.js and lodash don't really handle nested object
        // merging too well, so lets merge the nested query objects ourselves.
        _.defaults(defaultOpts.query, opts.query);
        _.defaults(defaultOpts, opts);
        return defaultOpts;
    };

    /**
     * @private
     * Internal method which creates an HTTP GET request from the supplied URL
     * object and calls the specified callback function with the chunked data as
     * a JSON object.
     *
     * @param {Object} opts The URL object to pass to the `http.get()`
     * method.
     * @param {Function} callback The callback function to call with the JSON
     * output from the HTTP request.
     */
    self._httpGet = function (opts, callback) {
        var uri = url.format(opts);
        http.get(uri, function (res) {
            var data = "";
            res.on("data", function (chunk) {
                // Save the chunked data (as a string) to the data variable.
                data += chunk.toString();
            });
            res.on("end", function () {
                // Convert the data string to a JSON object and pass it to the
                // specified callback function.
                callback(JSON.parse(data));
                // console.log(uri);
            });
        });
    }

    self.breed = {
        /**
         * The "/breed.list" route. This route calls the Petfinder "/breed.list"
         * API to query for a list of dogs.
         *
         * @param {Function} callback The callback function to call once the
         * list of animals has been received from the Petfinder API.
         */
        list: function (callback) {
            var options = self._httpOptions({
                "pathname": "/breed.list",
                "query": {
                    "animal": "dog"
                }
            });

            // Invoke the HTTP GET request and call the specified callback when
            // finished.
            self._httpGet(options, callback);
        }
    };

    self.pet = {
        /**
         * The "/pet.find" route. This route calls the Petfinder "/pet.find" API
         * to find dogs for the specified zip-code.
         *
         * @param {Number} location The zip-code to search.
         * @param {Object} opts An object containing a bunch of optional
         * arguments to send to the "/pet.find" request.
         * @param {Function} callback The callback function to call after we
         * get a response from the HTTP GET request.
         */
        find: function (location, opts, callback) {
            var options = self._httpOptions({
                "pathname": "/pet.find",
                "query": {
                    "animal": "dog",
                    "location": location
                }
            });

            opts = opts || {};

            // Merge the optional `opts` in to the `options.query` object.
            _.extend(options.query, opts);

            // Invoke the HTTP GET request and call the specified callback when
            // finished.
            self._httpGet(options, callback);
        },

        /**
         * The "/pet.get" route. This route calls the Petfinder "/pet.get" API
         * to get the pet with a specified `id`.
         *
         * @param {Number} id The id of the animal that we want to get info for.
         * @param {Function} callback The callback function to call after we
         * get a response from the HTTP GET request.
         */
        get: function (id, callback) {
            var options = self._httpOptions({
                "pathname": "/pet.get",
                "query": {
                    "id": id
                }
            });

            // Invoke the HTTP GET request and call the specified callback when
            // finished.
            self._httpGet(options, callback);
        },

        /**
         * The "/pet.getRandom" route. This route calls the Petfinder
         * "/pet.getRandom" API to get a random dog and return its basic info.
         *
         * @param {Function} callback The callback function to call after we
         * get a response from the HTTP GET request.
         */
        getRandom: function (callback) {
            var options = self._httpOptions({
                "pathname": "/pet.getRandom",
                "query": {
                    "animal": "dog",
                    "output": "basic"
                }
            });

            // Invoke the HTTP GET request and call the specified callback when
            // finished.
            self._httpGet(options, callback);
        }
    };
};

// Create a new `petfinder` object using our API key.
var pf = new petfinder(PETFINDER_KEY);

// Find 10 senior dogs in the 94089 (Sunnyvale, CA) area.
// http://api.petfinder.com/pet.find?format=json&key=3a62ece31719a64dcf6726980917d7ad&animal=dog&location=94089&age=senior&count=10
pf.pet.find(94089, {"age":"senior", "count":10}, function (data) {
    console.log("get by location:");
    // Loop over the array of pets and display their id/name/sex/age.
    data.petfinder.pets.pet.forEach(nameSexAge);
});

// Get a pet by its numeric id.
// http://api.petfinder.com/pet.get?format=json&key=3a62ece31719a64dcf6726980917d7ad&id=24395698
pf.pet.get(24395698, function (data) {
    console.log("get by id:");
    nameSexAge(data.petfinder.pet);
});

// Get a random dog.
// http://api.petfinder.com/pet.getRandom?format=json&key=3a62ece31719a64dcf6726980917d7ad&animal=dog&output=basic
pf.pet.getRandom(function (data) {
    console.log("get random dog:");
    nameSexAge(data.petfinder.pet);
});

// Get a list of dog breeds.
// http://api.petfinder.com/breed.list?format=json&key=3a62ece31719a64dcf6726980917d7ad&animal=dog
pf.breed.list(function (data) {
    var breeds = data.petfinder.breeds.breed;
    // Iterate over the array of breeds and remove that nested `$t` variable.
    breeds = breeds.map(function (breed) {
        return breed.$t;
    });
    console.log("get list of breeds:");
    console.log("\t", breeds.slice(0, 5).join(", "));
});

function nameSexAge(data) {
    console.log("\t[%d] %s/%s/%s", data.id.$t, data.name.$t, data.sex.$t, data.age.$t);
}
"""

texto3 = """
var moduleA =require            (                       "./module-a.js"         );
var moduleB =require( "../../module-b.js" );
var moduleC =require( "/my-library/module-c.js" );

var moduleA =require            (                 "module-a" );
var moduleB =require             (                   "module-b.js" );

var utils =require( "utils" );
var utils =dummyrequire( "dummy" );
var utils =requiredummy( "dummy" );
"""

texto4 = """
var moduleA =require            (                       './module-a.js'         );
var moduleB =require( '../../module-b.js' );
//bii://fran/images/data.png
var moduleC =require( '/my-library/module-c.js' );

var moduleA =require            (                 'module-a' );
var moduleB =require             (                   'module-b.js' );

var utils =require( 'utils' );
var utils =dummyrequire( 'dummy' );
var utils =requiredummy( 'dummy' );
//bii://data.txt
"""


class TestNodeParser(unittest.TestCase):
    def test_parserNodeTypes(self):
        node = NodeJSParser()
        node.parse(texto)
        obtained = [ref.name for ref in node.requires]
        expected = ['./module-a.js', '../../module-b.js', '/my-library/module-c.js', 'module-a',
                    'module-b.js', 'utils']
        self.assertItemsEqual(expected, obtained)

    def test_parserNodeCode(self):
        node = NodeJSParser()
        node.parse(texto2)
        obtained = [ref.name for ref in node.requires]
        expected = ['http', 'url', 'lodash']
        self.assertItemsEqual(expected, obtained)

    def test_parserNodeRequireSpectrum(self):
        node = NodeJSParser()
        node.parse(texto3)
        obtained = [ref.name for ref in node.requires]
        expected = ['./module-a.js', '../../module-b.js', '/my-library/module-c.js', 'module-a',
                    'module-b.js', 'utils']
        self.assertItemsEqual(expected, obtained)

    def test_parserNodeRequireSpectrum2(self):
        node = NodeJSParser()
        node.parse(texto4)

        obtained = [ref.name for ref in node.requires]
        expected = ['./module-a.js', '../../module-b.js', '/my-library/module-c.js', 'module-a',
                    'module-b.js', 'utils']
        self.assertItemsEqual(expected, obtained)

    def test_parser_references(self):
        node = NodeJSParser()
        node.parse(texto4)

        obtained = [ref.name for ref in node.references]
        expected = ['data.txt', 'fran/images/data.png']
        self.assertItemsEqual(expected, obtained)

    def test_parser_redis(self):
        node = NodeJSParser()
        node.parse(complex_test)
        obtained = [ref.name for ref in node.requires]

        expected = ['net', 'fran/rediss/lib/util.js', 'fran/rediss/lib/queue.js',
                'fran/rediss/lib/to_array.js', 'events', 'crypto', './lib/parser/javascript',
                './lib/parser/hiredis']
        self.assertItemsEqual(expected, obtained)

    def test_parse_haml(self):
        node = NodeJSParser()
        node.parse(require_haml)
        obtained = [ref.name for ref in node.requires]

        expected = ['file', 'assert', 'luispedraza/haml_js/lib/haml.js', 'os', 'test']
        self.assertItemsEqual(expected, obtained)


if __name__ == "__main__":
    unittest.main()
