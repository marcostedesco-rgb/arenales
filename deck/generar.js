const pptxgen = require("pptxgenjs");

// ---------------------------------------------------------------- identidad
const VERDE      = "004226";  // verde corporativo del plan
const VERDE_CARD = "0A5534";  // tarjeta sobre fondo verde
const CREMA      = "FBFAF8";  // fondo de las diapositivas claras
const VERDE_TINT = "E3EEE8";  // tarjeta positiva
const ROJO_TINT  = "F8E9E8";  // tarjeta de alerta
const BEIGE      = "E2D4CB";  // badge de meta
const GRIS       = "6B6B6B";
const BLANCO     = "FFFFFF";
const TITULO     = "Calibri";
const CUERPO     = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";           // 10" x 5.625"
pres.author = "Librería Arenales";
pres.title  = "Análisis de stock y rotación";

const eur = n => "€" + n.toLocaleString("es-ES",
  { maximumFractionDigits: 0, useGrouping: "always" });

// helper: tarjeta redondeada
const tarjeta = (s, x, y, w, h, fill, opts = {}) =>
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, fill: { color: fill }, rectRadius: 0.06,
    line: opts.line || { color: fill }, ...(opts.shadow ? { shadow: opts.shadow } : {}),
  });

// =========================================================== 1 · PORTADA
{
  const s = pres.addSlide();
  s.background = { color: VERDE };

  s.addText("ANEXO AL PLAN DE REACTIVACIÓN", {
    x: 0.6, y: 1.45, w: 6, h: 0.3, fontFace: CUERPO, fontSize: 11,
    color: BEIGE, charSpacing: 2, bold: true, margin: 0,
  });
  s.addText("Análisis de stock\ny rotación", {
    x: 0.6, y: 1.85, w: 6.2, h: 1.5, fontFace: TITULO, fontSize: 40,
    bold: true, color: BLANCO, lineSpacing: 44, margin: 0,
  });
  s.addText("Qué dicen los datos cuando se cruza el inventario\ncontra 13 meses de ventas reales", {
    x: 0.62, y: 3.45, w: 6, h: 0.7, fontFace: CUERPO, fontSize: 14,
    color: "C8DCD0", lineSpacing: 22, margin: 0,
  });
  s.addText("Stock a mayo 2026  ·  Ventas junio 2025 – junio 2026  ·  Fuente: Geslib", {
    x: 0.62, y: 4.45, w: 6.5, h: 0.3, fontFace: CUERPO, fontSize: 10,
    color: "8FB3A0", margin: 0,
  });

  // bloque de cifra a la derecha
  tarjeta(s, 7.05, 1.85, 2.5, 1.95, VERDE_CARD);
  s.addText(eur(53221), {
    x: 7.05, y: 2.15, w: 2.5, h: 0.75, fontFace: TITULO, fontSize: 34,
    bold: true, color: BLANCO, align: "center", margin: 0,
  });
  s.addText("de capital parado\nen las estanterías", {
    x: 7.05, y: 2.95, w: 2.5, h: 0.7, fontFace: CUERPO, fontSize: 12,
    color: "C8DCD0", align: "center", lineSpacing: 17, margin: 0,
  });

  s.addNotes("Anexo preparado para la reunión de socios. Refuerza el Eje 01 del plan (liberar caja del stock) con medición real en vez de estimación.");
}

// =========================================================== 2 · MÉTODO
{
  const s = pres.addSlide();
  s.background = { color: CREMA };

  s.addText("Qué hicimos", {
    x: 0.6, y: 0.5, w: 8, h: 0.6, fontFace: TITULO, fontSize: 34,
    bold: true, color: VERDE, margin: 0,
  });
  s.addText("Por primera vez cruzamos las dos fuentes que hasta ahora mirábamos por separado", {
    x: 0.62, y: 1.12, w: 8.8, h: 0.3, fontFace: CUERPO, fontSize: 13,
    color: GRIS, margin: 0,
  });

  const pasos = [
    ["1", "El inventario completo", "2.780 títulos y 3.863 ejemplares con su valor a PVP, exportados de Geslib."],
    ["2", "13 meses de ventas", "Todas las ventas de mostrador del 3 de junio de 2025 al 26 de junio de 2026, título por título."],
    ["3", "El cruce", "Cada título del stock contra su histórico real de venta. Sin muestras ni estimaciones."],
  ];
  pasos.forEach(([n, tit, txt], i) => {
    const y = 1.65 + i * 1.12;
    tarjeta(s, 0.6, y, 8.8, 0.95, BLANCO, { line: { color: "E8E6E2" } });
    s.addShape(pres.ShapeType.ellipse, {
      x: 0.85, y: y + 0.24, w: 0.47, h: 0.47, fill: { color: VERDE }, line: { color: VERDE },
    });
    s.addText(n, {
      x: 0.85, y: y + 0.24, w: 0.47, h: 0.47, fontFace: TITULO, fontSize: 16,
      bold: true, color: BLANCO, align: "center", valign: "middle", margin: 0,
    });
    s.addText(tit, {
      x: 1.55, y: y + 0.16, w: 7.5, h: 0.3, fontFace: TITULO, fontSize: 15,
      bold: true, color: VERDE, margin: 0,
    });
    s.addText(txt, {
      x: 1.55, y: y + 0.48, w: 7.6, h: 0.32, fontFace: CUERPO, fontSize: 12,
      color: GRIS, margin: 0,
    });
  });

  s.addText("Lo hace un programa: se le dan los dos archivos y devuelve siempre el mismo resultado. Auditable y repetible todas las semanas.", {
    x: 0.62, y: 5.02, w: 8.8, h: 0.3, fontFace: CUERPO, fontSize: 10.5,
    color: GRIS, italic: true, margin: 0,
  });
}

// =========================================================== 3 · HALLAZGO
{
  const s = pres.addSlide();
  s.background = { color: CREMA };

  s.addText("El hallazgo principal", {
    x: 0.6, y: 0.5, w: 8, h: 0.6, fontFace: TITULO, fontSize: 34,
    bold: true, color: VERDE, margin: 0,
  });
  s.addText("El stock no rota despacio: en su mayor parte no rota", {
    x: 0.62, y: 1.12, w: 8.8, h: 0.3, fontFace: CUERPO, fontSize: 13,
    color: GRIS, margin: 0,
  });

  const kpis = [
    ["85%", "de los títulos no vendió\nni una sola vez en 13 meses", ROJO_TINT],
    [eur(53221), "de capital inmovilizado\n(83% del valor del stock)", ROJO_TINT],
    ["30,2", "meses de rotación\nEl estándar del sector son 6", ROJO_TINT],
    [eur(2129), "de venta media mensual\ncontra " + eur(64266) + " en estantería", VERDE_TINT],
  ];
  kpis.forEach(([cifra, txt, fill], i) => {
    const x = 0.6 + i * 2.24;
    tarjeta(s, x, 1.62, 2.06, 1.5, fill);
    s.addText(cifra, {
      x, y: 1.78, w: 2.06, h: 0.55, fontFace: TITULO, fontSize: 27,
      bold: true, color: VERDE, align: "center", margin: 0,
    });
    s.addText(txt, {
      x: x + 0.1, y: 2.38, w: 1.86, h: 0.62, fontFace: CUERPO, fontSize: 10,
      color: "4A4A4A", align: "center", lineSpacing: 13, margin: 0,
    });
  });

  tarjeta(s, 0.6, 3.35, 8.8, 1.62, VERDE);
  s.addText("Los dos errores conviven", {
    x: 0.95, y: 3.58, w: 8.2, h: 0.35, fontFace: TITULO, fontSize: 18,
    bold: true, color: BLANCO, margin: 0,
  });
  s.addText(
    "Hay dinero parado en libros que nadie compra y, al mismo tiempo, faltan ejemplares de los libros que sí se venden. " +
    "De los diez títulos más vendidos del año, cinco están hoy en cero ejemplares.",
    { x: 0.95, y: 4.0, w: 8.1, h: 0.75, fontFace: CUERPO, fontSize: 13,
      color: "C8DCD0", lineSpacing: 19, margin: 0 });

  s.addNotes("85% son 2.364 títulos de 2.780. La rotación se calcula como valor del stock dividido por venta media mensual.");
}

// =========================================================== 4 · SEGMENTOS
{
  const s = pres.addSlide();
  s.background = { color: CREMA };

  s.addText("Dónde está la plata", {
    x: 0.6, y: 0.45, w: 8, h: 0.6, fontFace: TITULO, fontSize: 34,
    bold: true, color: VERDE, margin: 0,
  });
  s.addText("Cada título del inventario quedó clasificado en una de estas seis categorías", {
    x: 0.62, y: 1.07, w: 8.8, h: 0.3, fontFace: CUERPO, fontSize: 13,
    color: GRIS, margin: 0,
  });

  s.addChart(pres.ChartType.bar, [{
    name: "Valor en estantería",
    labels: ["Reponer", "Destacar", "Vigilar", "Mantener", "Liquidar", "Devolver"],
    values: [137, 2519, 3232, 5156, 24813, 28409],
  }], {
    x: 0.6, y: 1.5, w: 5.15, h: 3.45,
    barDir: "bar", chartColors: [VERDE], barGapWidthPct: 45,
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: "4A4A4A",
    dataLabelFontFace: CUERPO, dataLabelFontSize: 10,
    dataLabelFormatCode: '#,##0 "€"',
    catAxisLabelColor: "4A4A4A", catAxisLabelFontFace: CUERPO, catAxisLabelFontSize: 11,
    valAxisHidden: true, valGridLine: { style: "none" },
    catGridLine: { style: "none" }, showLegend: false,
    valAxisMaxVal: 34000, plotArea: { fill: { color: CREMA } },
    chartArea: { fill: { color: CREMA } },
  });

  const filas = [
    ["Devolver", "1.748 títulos · 1 ejemplar cada uno", "Cero ventas. Devolución al distribuidor."],
    ["Liquidar", "616 títulos · 1.424 ejemplares", "Cero ventas y stock repetido. Mesa de descuento."],
    ["Mantener", "264 títulos", "Rotación baja pero viva. Sin acción."],
    ["Vigilar", "60 títulos · 214 ejemplares", "Una sola venta y varios ejemplares. Revisar en un mes."],
    ["Destacar", "53 títulos · 167 ejemplares", "Venden y hay stock. Al mostrador."],
    ["Reponer", "39 títulos · 6 ejemplares", "Venden y no hay. Pedido urgente."],
  ];
  filas.forEach(([tit, dato, accion], i) => {
    const y = 1.52 + i * 0.575;
    s.addText(tit, {
      x: 6.0, y, w: 1.3, h: 0.22, fontFace: TITULO, fontSize: 12.5,
      bold: true, color: VERDE, margin: 0,
    });
    s.addText(dato, {
      x: 6.0, y: y + 0.21, w: 3.45, h: 0.2, fontFace: CUERPO, fontSize: 9.5,
      color: "4A4A4A", margin: 0,
    });
    s.addText(accion, {
      x: 6.0, y: y + 0.375, w: 3.45, h: 0.2, fontFace: CUERPO, fontSize: 9,
      color: GRIS, italic: true, margin: 0,
    });
  });

  s.addText("Devolver y liquidar concentran " + eur(53221) + ": el 83% del valor del inventario.", {
    x: 0.62, y: 5.05, w: 8.8, h: 0.3, fontFace: CUERPO, fontSize: 11,
    color: VERDE, bold: true, margin: 0,
  });
}

// =========================================================== 5 · SACAR
{
  const s = pres.addSlide();
  s.background = { color: CREMA };

  s.addText("Lo que hay que sacar", {
    x: 0.6, y: 0.45, w: 8, h: 0.6, fontFace: TITULO, fontSize: 34,
    bold: true, color: VERDE, margin: 0,
  });
  s.addText("Los diez títulos que más capital retienen sin haber vendido nunca", {
    x: 0.62, y: 1.07, w: 8.8, h: 0.3, fontFace: CUERPO, fontSize: 13,
    color: GRIS, margin: 0,
  });

  const libros = [
    ["Cubanías", 15, 279], ["Quicksilver Saga Alquimia & Fae vol. 1", 10, 240],
    ["Golpe militar y dictadura en Argentina", 9, 189],
    ["La destrucción por el soneto", 5, 180], ["Selected Paintings", 4, 156],
    ["Concierto mambí", 10, 150], ["De Venezuela al Kurdistán", 5, 118],
    ["De ética y política", 4, 114], ["Libro de Jóveno", 7, 105],
    ["Navidades de miedo", 4, 96],
  ];

  tarjeta(s, 0.6, 1.5, 5.35, 3.05, BLANCO, { line: { color: "E8E6E2" } });

  s.addText("TÍTULO", { x: 0.85, y: 1.66, w: 3.2, h: 0.2, fontFace: CUERPO,
    fontSize: 8.5, bold: true, color: GRIS, charSpacing: 1, margin: 0 });
  s.addText("EJEMPL.", { x: 4.1, y: 1.66, w: 0.75, h: 0.2, fontFace: CUERPO,
    fontSize: 8.5, bold: true, color: GRIS, align: "right", charSpacing: 1, margin: 0 });
  s.addText("VALOR", { x: 4.9, y: 1.66, w: 0.8, h: 0.2, fontFace: CUERPO,
    fontSize: 8.5, bold: true, color: GRIS, align: "right", charSpacing: 1, margin: 0 });

  libros.forEach(([t, u, v], i) => {
    const y = 1.93 + i * 0.255;
    s.addText(t, { x: 0.85, y, w: 3.2, h: 0.22, fontFace: CUERPO, fontSize: 10,
      color: "3A3A3A", margin: 0 });
    s.addText(String(u), { x: 4.1, y, w: 0.75, h: 0.22, fontFace: CUERPO, fontSize: 10,
      color: "3A3A3A", align: "right", margin: 0 });
    s.addText(eur(v), { x: 4.9, y, w: 0.8, h: 0.22, fontFace: CUERPO, fontSize: 10,
      bold: true, color: VERDE, align: "right", margin: 0 });
  });

  tarjeta(s, 6.2, 1.5, 3.2, 3.05, VERDE);
  s.addText("El patrón", {
    x: 6.5, y: 1.72, w: 2.7, h: 0.3, fontFace: TITULO, fontSize: 16,
    bold: true, color: BLANCO, margin: 0,
  });
  s.addText("El stock muerto no está repartido al azar. Se concentra en dos familias:", {
    x: 6.5, y: 2.08, w: 2.65, h: 0.5, fontFace: CUERPO, fontSize: 10.5,
    color: "C8DCD0", lineSpacing: 14, margin: 0,
  });
  s.addText("Ensayo político e histórico latinoamericano", {
    x: 6.5, y: 2.62, w: 2.65, h: 0.35, fontFace: CUERPO, fontSize: 11,
    bold: true, color: BLANCO, lineSpacing: 14, margin: 0,
  });
  s.addText("Arte y diseño de precio alto", {
    x: 6.5, y: 3.05, w: 2.65, h: 0.22, fontFace: CUERPO, fontSize: 11,
    bold: true, color: BLANCO, margin: 0,
  });
  s.addText("Son compras por convicción, no por demanda. No hay que dejar de traerlas: hay que traerlas de a un ejemplar y por pedido.", {
    x: 6.5, y: 3.4, w: 2.65, h: 0.9, fontFace: CUERPO, fontSize: 10.5,
    color: "C8DCD0", lineSpacing: 14, margin: 0,
  });

  tarjeta(s, 0.6, 4.68, 8.8, 0.6, ROJO_TINT);
  s.addText([
    { text: "El peor caso del inventario:  ", options: { bold: true, color: VERDE } },
    { text: "El diseño de sentido — 19 ejemplares, " + eur(475) + " en estantería, una sola venta en 13 meses.", options: { color: "4A4A4A" } },
  ], { x: 0.9, y: 4.68, w: 8.3, h: 0.6, fontFace: CUERPO, fontSize: 12,
       valign: "middle", margin: 0 });
}

// =========================================================== 6 · REPONER
{
  const s = pres.addSlide();
  s.background = { color: CREMA };

  s.addText("Lo que falta comprar", {
    x: 0.6, y: 0.45, w: 8.8, h: 0.6, fontFace: TITULO, fontSize: 34,
    bold: true, color: VERDE, margin: 0,
  });
  s.addText("Treinta y nueve títulos venden bien y están agotados o casi. Cada día sin ellos es venta perdida.", {
    x: 0.62, y: 1.07, w: 8.8, h: 0.3, fontFace: CUERPO, fontSize: 13,
    color: GRIS, margin: 0,
  });

  const rep = [
    ["Píldoras antieméticas", 24, 0, 480],
    ["Las gratitudes", 22, 1, 438],
    ["Nonadanadie", 20, 0, 400],
    ["Perro cubano", 19, 0, 244],
    ["Hamnet (17ª ed.)", 10, 0, 240],
    ["Loco de Dios en el fin del mundo", 10, 1, 239],
    ["Comerás flores", 11, 1, 219],
    ["Misión en París", 9, 1, 197],
  ];

  s.addText("TÍTULO", { x: 0.85, y: 1.56, w: 3.9, h: 0.2, fontFace: CUERPO,
    fontSize: 8.5, bold: true, color: GRIS, charSpacing: 1, margin: 0 });
  s.addText("VENDIDOS", { x: 4.85, y: 1.56, w: 1.1, h: 0.2, fontFace: CUERPO,
    fontSize: 8.5, bold: true, color: GRIS, align: "right", charSpacing: 1, margin: 0 });
  s.addText("EN STOCK", { x: 6.05, y: 1.56, w: 1.1, h: 0.2, fontFace: CUERPO,
    fontSize: 8.5, bold: true, color: GRIS, align: "right", charSpacing: 1, margin: 0 });
  s.addText("FACTURADO", { x: 7.25, y: 1.56, w: 1.9, h: 0.2, fontFace: CUERPO,
    fontSize: 8.5, bold: true, color: GRIS, align: "right", charSpacing: 1, margin: 0 });

  rep.forEach(([t, v, st, f], i) => {
    const y = 1.85 + i * 0.38;
    tarjeta(s, 0.6, y - 0.05, 8.8, 0.34, i % 2 ? BLANCO : "F4F2EE",
      { line: { color: i % 2 ? BLANCO : "F4F2EE" } });
    s.addText(t, { x: 0.85, y, w: 3.9, h: 0.24, fontFace: CUERPO, fontSize: 11,
      color: "3A3A3A", margin: 0 });
    s.addText(String(v), { x: 4.85, y, w: 1.1, h: 0.24, fontFace: CUERPO, fontSize: 11,
      color: "3A3A3A", align: "right", margin: 0 });
    s.addText(st === 0 ? "0" : String(st), {
      x: 6.05, y, w: 1.1, h: 0.24, fontFace: CUERPO, fontSize: 11,
      bold: st === 0, color: st === 0 ? "B03A2E" : "3A3A3A", align: "right", margin: 0 });
    s.addText(eur(f), { x: 7.25, y, w: 1.9, h: 0.24, fontFace: CUERPO, fontSize: 11,
      bold: true, color: VERDE, align: "right", margin: 0 });
  });

  tarjeta(s, 0.6, 4.95, 8.8, 0.5, VERDE_TINT);
  s.addText("Los cuatro primeros facturaron " + eur(1562) + " en el año y hoy no queda ni un ejemplar de tres de ellos.", {
    x: 0.9, y: 4.95, w: 8.3, h: 0.5, fontFace: CUERPO, fontSize: 11.5,
    color: VERDE, bold: true, valign: "middle", margin: 0,
  });
}

// =========================================================== 7 · EJE 01
{
  const s = pres.addSlide();
  s.background = { color: VERDE };

  s.addText("QUÉ SIGNIFICA PARA EL EJE 01", {
    x: 0.6, y: 0.5, w: 8.8, h: 0.25, fontFace: CUERPO, fontSize: 10.5,
    bold: true, color: BEIGE, charSpacing: 2, margin: 0,
  });
  s.addText("La meta de caja del plan se queda corta", {
    x: 0.6, y: 0.82, w: 8.8, h: 0.6, fontFace: TITULO, fontSize: 32,
    bold: true, color: BLANCO, margin: 0,
  });

  tarjeta(s, 0.6, 1.72, 4.25, 1.5, VERDE_CARD);
  s.addText("META ACTUAL DEL PLAN", {
    x: 0.9, y: 1.92, w: 3.7, h: 0.22, fontFace: CUERPO, fontSize: 9.5,
    bold: true, color: "8FB3A0", charSpacing: 1, margin: 0 });
  s.addText(eur(8000) + " – " + eur(12000), {
    x: 0.9, y: 2.2, w: 3.7, h: 0.55, fontFace: TITULO, fontSize: 28,
    bold: true, color: BLANCO, margin: 0 });
  s.addText("estimado sin medición", {
    x: 0.9, y: 2.78, w: 3.7, h: 0.25, fontFace: CUERPO, fontSize: 11,
    color: "8FB3A0", margin: 0 });

  tarjeta(s, 5.15, 1.72, 4.25, 1.5, BEIGE);
  s.addText("POTENCIAL SEGÚN EL ANÁLISIS", {
    x: 5.45, y: 1.92, w: 3.7, h: 0.22, fontFace: CUERPO, fontSize: 9.5,
    bold: true, color: "7A6A5E", charSpacing: 1, margin: 0 });
  s.addText(eur(34414), {
    x: 5.45, y: 2.2, w: 3.7, h: 0.55, fontFace: TITULO, fontSize: 28,
    bold: true, color: VERDE, margin: 0 });
  s.addText("casi el triple del techo previsto", {
    x: 5.45, y: 2.78, w: 3.7, h: 0.25, fontFace: CUERPO, fontSize: 11,
    color: "7A6A5E", margin: 0 });

  s.addText("Cómo se compone", {
    x: 0.6, y: 3.42, w: 8.8, h: 0.3, fontFace: TITULO, fontSize: 15,
    bold: true, color: BLANCO, margin: 0 });

  const comp = [
    ["Devolución al distribuidor", eur(17045), "1.748 ejemplares · se asume que el depósito reconoce el 60% del PVP"],
    ["Liquidación en tienda", eur(17369), "1.424 ejemplares · se asume un descuento medio del 30%"],
  ];
  comp.forEach(([tit, cifra, nota], i) => {
    const y = 3.82 + i * 0.66;
    s.addText(tit, { x: 0.62, y, w: 3.3, h: 0.25, fontFace: CUERPO, fontSize: 12.5,
      bold: true, color: BLANCO, margin: 0 });
    s.addText(cifra, { x: 3.95, y, w: 1.15, h: 0.25, fontFace: TITULO, fontSize: 13.5,
      bold: true, color: BEIGE, align: "right", margin: 0 });
    s.addText(nota, { x: 5.3, y: y + 0.02, w: 4.1, h: 0.4, fontFace: CUERPO, fontSize: 9.5,
      color: "8FB3A0", lineSpacing: 12, margin: 0 });
  });

  s.addText("Las dos hipótesis de recupero hay que confirmarlas con Trevenque y con los comerciales antes de comprometer la cifra.", {
    x: 0.62, y: 5.1, w: 8.8, h: 0.3, fontFace: CUERPO, fontSize: 10,
    color: "8FB3A0", italic: true, margin: 0 });

  s.addNotes("Las dos tasas (60% devolución, 30% descuento) son supuestos configurables. Con las tasas reales el número se recalcula solo.");
}

// =========================================================== 8 · DECISIONES
{
  const s = pres.addSlide();
  s.background = { color: CREMA };

  s.addText("Lo que hay que decidir", {
    x: 0.6, y: 0.5, w: 8.8, h: 0.6, fontFace: TITULO, fontSize: 34,
    bold: true, color: VERDE, margin: 0 });
  s.addText("Cuatro decisiones que salen de este análisis y no estaban en el plan de agosto", {
    x: 0.62, y: 1.12, w: 8.8, h: 0.3, fontFace: CUERPO, fontSize: 13,
    color: GRIS, margin: 0 });

  const decisiones = [
    ["1", "Autorizar la devolución masiva", "1.748 ejemplares sin ninguna venta. Hay que acordar la tasa de recompra con cada distribuidor.", "Agosto"],
    ["2", "Montar la mesa de liquidación", "616 títulos con ejemplares repetidos. Definir el descuento: 30% es la hipótesis de trabajo.", "Agosto"],
    ["3", "Pedido urgente de reposición", "39 títulos que venden y están en cero. Es la única acción que sube la venta esta misma semana.", "Inmediato"],
    ["4", "Regla de compra por rotación", "Ensayo y arte, de a un ejemplar y por pedido. Narrativa hispanoamericana, reposición automática.", "Septiembre"],
  ];
  decisiones.forEach(([n, tit, txt, plazo], i) => {
    const y = 1.62 + i * 0.87;
    tarjeta(s, 0.6, y, 8.8, 0.74, BLANCO, { line: { color: "E8E6E2" } });
    s.addShape(pres.ShapeType.ellipse, {
      x: 0.85, y: y + 0.19, w: 0.38, h: 0.38, fill: { color: VERDE }, line: { color: VERDE } });
    s.addText(n, { x: 0.85, y: y + 0.19, w: 0.38, h: 0.38, fontFace: TITULO, fontSize: 13,
      bold: true, color: BLANCO, align: "center", valign: "middle", margin: 0 });
    s.addText(tit, { x: 1.42, y: y + 0.12, w: 5.6, h: 0.26, fontFace: TITULO, fontSize: 13.5,
      bold: true, color: VERDE, margin: 0 });
    s.addText(txt, { x: 1.42, y: y + 0.39, w: 6.3, h: 0.28, fontFace: CUERPO, fontSize: 10.5,
      color: GRIS, margin: 0 });
    tarjeta(s, 7.95, y + 0.2, 1.2, 0.34, BEIGE);
    s.addText(plazo, { x: 7.95, y: y + 0.2, w: 1.2, h: 0.34, fontFace: CUERPO, fontSize: 10,
      bold: true, color: VERDE, align: "center", valign: "middle", margin: 0 });
  });

  s.addText("Este cruce pasa a hacerse todas las semanas de forma automática: el informe llega los lunes con la lista actualizada.", {
    x: 0.62, y: 5.15, w: 8.8, h: 0.3, fontFace: CUERPO, fontSize: 10.5,
    color: VERDE, italic: true, margin: 0 });
}

pres.writeFile({ fileName: "/root/arenales/deck/Anexo_Stock_Rotacion_Arenales.pptx" })
  .then(f => console.log("OK:", f));
