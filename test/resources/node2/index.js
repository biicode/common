var sumador = require("./suma.js");
var restador = require("./resta");

/**
 * New node file
 */
var resultado = sumador.suma(1,1);
var resultado2 = restador.resta(2,1);
console.log("Resultado "+resultado+" "+resultado2);