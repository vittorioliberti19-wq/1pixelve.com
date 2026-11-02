const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync("calculadora/lightbox/index.html", "utf8");
const start = source.indexOf("      const CFG = {");
const end = source.indexOf("      function mostrar(", start);
assert.ok(start >= 0 && end > start, "No se encontró bloque de cálculo Light Box.");
const cercano = (actual, esperado) => assert.ok(Math.abs(actual - esperado) < 1e-8, `${actual} ≉ ${esperado}`);

function calcular({ circuitos, meses, prepago = false, divisas = false, extra = "0" }) {
  const inputs = {
    prepago: { checked: prepago },
    divisas: { checked: divisas },
    descExtra: { value: extra },
    cliente: { value: "" }, rif: { value: "" }, email: { value: "" }, direccion: { value: "" },
    fechaInicio: { value: "" }, firmante: { value: "" }, cedulaFirmante: { value: "" }, cargoFirmante: { value: "" },
  };
  const document = {
    getElementById: (id) => inputs[id],
    querySelector: (selector) => selector.includes('plazo') ? { value: String(meses) } : null,
    querySelectorAll: (selector) => selector.includes('circuito') ? circuitos.map((value) => ({ value: String(value) })) : [],
  };
  const context = { document, Intl, Number, Math, Array };
  vm.createContext(context);
  vm.runInContext(source.slice(start, end) + "\nglobalThis.resultado = calcular; globalThis.formatoPorcentaje = porcentaje;", context);
  const resultado = context.resultado();
  if (resultado) resultado.formatoPorcentaje = context.formatoPorcentaje;
  return resultado;
}

for (const meses of [3, 6, 12]) {
  const esperado = { 3: 3700, 6: 3400, 12: 3160 }[meses];
  for (const [cantidad, descuento] of [[1, 0], [2, 0.1], [3, 0.15], [4, 0.2]]) {
    const r = calcular({ circuitos: Array.from({ length: cantidad }, (_, i) => i + 1), meses });
    assert.equal(r.precioBase, esperado, `${meses} meses tarifa`);
    assert.equal(r.descVolumenPct, descuento, `${cantidad} circuitos descuento`);
    cercano(r.total, esperado * cantidad * meses * (1 - descuento));
  }
}

const completo = calcular({ circuitos: [1, 2, 3, 4], meses: 3, prepago: true, divisas: true, extra: "10" });
assert.equal(completo.lista, 44400);
assert.equal(completo.descVolumen, 8880);
assert.equal(completo.descPrepago, 7104);
cercano(completo.descDivisas, 5683.2);
cercano(completo.descExtra, 2273.28);
cercano(completo.total, 20459.52);
cercano(completo.mensual, 6819.84);
assert.equal(completo.descExtraPct, 0.1);
assert.equal(completo.formatoPorcentaje(0.29), "29,00%", "No debe filtrar artefactos de punto flotante.");

assert.equal(calcular({ circuitos: [1], meses: 3, extra: "0" }).descExtra, 0);
assert.equal(calcular({ circuitos: [1], meses: 3, extra: "100" }).total, 0);
assert.equal(calcular({ circuitos: [1], meses: 3, extra: "NaN" }).descExtraPct, 0);
assert.equal(calcular({ circuitos: [1], meses: 3, extra: "-1" }).descExtraPct, 0);
assert.equal(calcular({ circuitos: [1], meses: 3, extra: "101" }).descExtraPct, 1);
const sinQuinto = calcular({ circuitos: [1, 2, 3, 4, 5], meses: 3 });
assert.equal(sinQuinto.n, 4, "No hay quinto circuito.");
assert.deepEqual(sinQuinto.sel, [1, 2, 3, 4]);
assert.equal(calcular({ circuitos: [], meses: 3 }), null);

console.log("lightbox-pricing: OK");
