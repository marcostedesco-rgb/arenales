// Librería Arenales — Chat público
// Recomienda solo libros del catálogo real. La API key y el catálogo
// completo nunca llegan al navegador: acá se filtra y se responde con
// {respuesta} y nada más.

import catalogo from './_datos/catalogo.js';

const MODELO = 'claude-sonnet-4-6';
const LIMITE_MENSAJE = 500;
const LIMITE_HISTORIAL = 10;
const LIMITE_MENSAJES_POR_HORA = 15;
const VENTANA_MS = 60 * 60 * 1000;

const intentos = new Map(); // ip -> [timestamps de mensajes en la última hora]

const SYSTEM_PROMPT = `Eres el librero de Librería Arenales, en el barrio de Chamberí, Madrid.
Especializada en literatura hispanoamericana. Cinco estrellas en Google,
club de lectura propio y cuentacuentos los sábados.

Atiendes a alguien que ha entrado en la web. Hablas como un librero de
barrio: cercano, breve, con criterio propio. Castellano de España. Nada de
lenguaje de folleto ni de vendedor.

LO QUE NO SE ROMPE NUNCA:

Solo recomiendas libros que están en la lista de catálogo que te paso. Si
un título no está en esa lista, no existe: no lo menciones, no lo sugieras
y no supongas que lo tenemos. Inventar un título es el único error grave
que puedes cometer.

CÓMO TRABAJAS, EN ESTE ORDEN:

1. Si lo que te piden es vago —"algo bueno", "una novela", "un regalo"—
   haz UNA pregunta corta antes de recomendar. Una, no tres. Las que
   sirven: ¿para ti o para regalar? · ¿qué has leído últimamente que te
   haya gustado? · ¿qué edad tiene? · ¿lo quieres largo o algo que se lea
   rápido?

2. Busca el encaje directo en el catálogo. Si lo hay, recomiéndalo.

3. Si no hay encaje directo, NO digas que no tienes nada. Busca por
   cercanía dentro del catálogo: mismo autor, mismo país, misma época,
   tono parecido, un tema que se roce. Ofrécelo explicando el puente:
   "Novela negra como tal no es, pero si te interesa ese ambiente turbio
   este te va a enganchar."

4. Si sigues sin encontrar nada que encaje de verdad, haz una segunda
   pregunta que abra otra puerta: qué te gustó del último que leíste, si
   prefieres algo más ligero, si te importa el país o la época.

5. Solo después de haber intentado de verdad, dilo. Y nunca como un
   punto final: "Ahora mismo no lo tenemos, pero pásate por la librería o
   escríbenos y te lo pedimos, suele estar en dos o tres días."

REGLA DURA SOBRE EL "NO":

Nunca abras una respuesta diciendo que no tienes algo. El "no" solo puede
aparecer después de haber ofrecido alternativas reales del catálogo o
haber repreguntado. Si tu primera frase empieza por "no tenemos", "no
disponemos" o "lamentablemente", estás contestando mal: vuelve a mirar el
catálogo y busca por cercanía.

LO DEMÁS:

- Dos o tres libros como máximo. Un librero no te suelta quince.
- De cada uno, por qué se lo recomiendas a esa persona en concreto. Una o
  dos líneas. Sin resumir la contraportada.
- Di siempre el precio.
- Cuando dos libros encajan parecido, elige el que lleva más tiempo sin
  venderse (viene marcado con "m":true). No lo menciones ni lo
  justifiques. Pero si ninguno encaja de verdad con lo que te han pedido,
  no lo empujes: recomendar mal se paga con que esa persona no vuelva.
- Nunca hables de cuánto stock hay, de qué no se vende, ni de números del
  negocio. Si te preguntan, di que de eso no sabes.
- Si preguntan algo que no va de libros, contesta corto y vuelve al tema.`;

function obtenerIp(req) {
  const xff = req.headers['x-forwarded-for'];
  if (xff) return xff.split(',')[0].trim();
  return req.socket?.remoteAddress || 'desconocida';
}

function limiteExcedido(clave, limite) {
  const ahora = Date.now();
  const previos = (intentos.get(clave) || []).filter((t) => ahora - t < VENTANA_MS);
  if (previos.length >= limite) {
    intentos.set(clave, previos);
    return true;
  }
  previos.push(ahora);
  intentos.set(clave, previos);
  return false;
}

function normalizar(s) {
  return (s || '')
    .toString()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '');
}

function coincide(item, palabras) {
  const campo = normalizar(`${item.t} ${item.a} ${item.e}`);
  return palabras.some((p) => campo.includes(p));
}

const TOPE_COINCIDENCIAS = 80;
const TOPE_MAS_VENDIDOS = 40;
const TOPE_STOCK_MUERTO = 60;
const TOPE_RESTO = 20;
const TOPE_POR_EDITORIAL = 8;

function claveItem(item) {
  return `${item.t}|${item.a}`;
}

function filtrarCatalogo(mensaje) {
  const palabras = normalizar(mensaje)
    .split(/[^a-z0-9ñ]+/)
    .filter((p) => p.length >= 3);

  let coincidencias = palabras.length ? catalogo.filter((item) => coincide(item, palabras)) : [];
  if (coincidencias.length > TOPE_COINCIDENCIAS) {
    coincidencias = [...coincidencias].sort((a, b) => b.u - a.u).slice(0, TOPE_COINCIDENCIAS);
  }

  // Muestra base: siempre presente, para que el modelo tenga con qué
  // trabajar cuando piden un género, un tema o un tono en vez de un título.
  const usados = new Set(coincidencias.map(claveItem));
  const porEditorial = new Map();

  const puedeAgregar = (item) =>
    !usados.has(claveItem(item)) && (porEditorial.get(item.e) || 0) < TOPE_POR_EDITORIAL;

  const agregar = (item, destino) => {
    destino.push(item);
    usados.add(claveItem(item));
    porEditorial.set(item.e, (porEditorial.get(item.e) || 0) + 1);
  };

  const masVendidos = [];
  for (const item of [...catalogo].sort((a, b) => b.v - a.v)) {
    if (masVendidos.length >= TOPE_MAS_VENDIDOS) break;
    if (puedeAgregar(item)) agregar(item, masVendidos);
  }

  const stockMuerto = [];
  for (const item of catalogo.filter((i) => i.m).sort((a, b) => b.u - a.u)) {
    if (stockMuerto.length >= TOPE_STOCK_MUERTO) break;
    if (puedeAgregar(item)) agregar(item, stockMuerto);
  }

  const resto = [];
  const disponibles = catalogo.filter(puedeAgregar);
  const paso = disponibles.length / TOPE_RESTO;
  for (let i = 0; i < TOPE_RESTO && disponibles.length; i++) {
    const item = disponibles[Math.min(disponibles.length - 1, Math.floor(i * paso))];
    if (puedeAgregar(item)) agregar(item, resto);
  }

  return [...coincidencias, ...masVendidos, ...stockMuerto, ...resto];
}

function armarMensajes(mensaje, historial, candidatos) {
  const mensajes = [];
  for (const turno of historial) {
    if (turno && typeof turno.usuario === 'string' && typeof turno.librero === 'string') {
      mensajes.push({ role: 'user', content: turno.usuario });
      mensajes.push({ role: 'assistant', content: turno.librero });
    }
  }
  mensajes.push({
    role: 'user',
    content: `${mensaje}\n\n<catalogo>\n${JSON.stringify(candidatos)}\n</catalogo>`,
  });
  return mensajes;
}

async function preguntarClaude(mensaje, historial, candidatos) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) throw new Error('Falta ANTHROPIC_API_KEY');

  const resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: MODELO,
      max_tokens: 700,
      system: SYSTEM_PROMPT,
      messages: armarMensajes(mensaje, historial, candidatos),
    }),
  });

  if (!resp.ok) {
    throw new Error(`Anthropic API respondió ${resp.status}`);
  }
  const datos = await resp.json();
  return datos.content[0].text;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Método no permitido' });
    return;
  }

  if (limiteExcedido(obtenerIp(req), LIMITE_MENSAJES_POR_HORA)) {
    res.status(429).json({ error: 'Demasiados mensajes. Probá de nuevo más tarde.' });
    return;
  }

  const { mensaje, historial } = req.body || {};

  if (typeof mensaje !== 'string' || !mensaje.trim() || mensaje.length > LIMITE_MENSAJE) {
    res.status(400).json({ error: 'Mensaje inválido' });
    return;
  }
  if (historial !== undefined && (!Array.isArray(historial) || historial.length > LIMITE_HISTORIAL)) {
    res.status(400).json({ error: 'Historial inválido' });
    return;
  }

  try {
    const candidatos = filtrarCatalogo(mensaje);
    const respuesta = await preguntarClaude(mensaje, historial || [], candidatos);
    res.status(200).json({ respuesta });
  } catch (err) {
    res.status(500).json({ error: 'No se pudo responder ahora.' });
  }
}
