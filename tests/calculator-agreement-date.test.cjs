const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const files = [
  "calculadora/galerias/index.html",
  "calculadora/paradas/index.html",
  "calculadora/lightbox/index.html",
];

function extraerFecha(source) {
  const inicio = source.indexOf("function fechaAcuerdo(valor)");
  assert.ok(inicio >= 0, "Falta formateador de fecha del acuerdo.");
  const fin = source.indexOf("\n      }", inicio) + "\n      }".length;
  const context = { Date, Intl, Number };
  vm.createContext(context);
  vm.runInContext(source.slice(inicio, fin) + "\nglobalThis.fechaAcuerdo = fechaAcuerdo;", context);
  return context.fechaAcuerdo;
}

for (const file of files) {
  const source = fs.readFileSync(file, "utf8");
  const scripts = [...source.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((match) => match[1]);
  assert.ok(scripts.length > 0, `${file}: no hay script inline para validar.`);
  scripts.forEach((script) => new vm.Script(script));
  assert.match(source, /<input type="date" id="fechaInicio"/, `${file}: falta input date nativo.`);
  assert.match(source, /Fecha de inicio del acuerdo/, `${file}: falta etiqueta de acuerdo.`);
  assert.match(source, /Inicio del acuerdo: /, `${file}: fecha no llega al PDF/propuesta.`);
  const fechaAcuerdo = extraerFecha(source);
  const resultado = fechaAcuerdo("2027-01-15");
  assert.match(resultado, /15/, `${file}: día cambió por zona horaria.`);
  assert.match(resultado.toLowerCase(), /enero/, `${file}: mes cambió por zona horaria.`);
  assert.match(resultado, /2027/, `${file}: año cambió por zona horaria.`);
}

const galerias = fs.readFileSync("calculadora/galerias/index.html", "utf8");
assert.match(galerias, /<input type="date" id="multiFechaInicio"/, "Galerías multimarca: falta input date.");
assert.match(galerias, /\[\["fechaInicio", "multiFechaInicio"\], \["multiFechaInicio", "fechaInicio"\]\]/, "Galerías: la fecha debe sincronizar ambos modos.");
assert.match(galerias, /\$\("multiFechaInicio"\)\.value/, "Galerías multimarca: fecha no llega al PDF.");

console.log("calculator-agreement-date: OK");
