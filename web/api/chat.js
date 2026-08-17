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

const SYSTEM_PROMPT = `Sos el librero de Librería Arenales, en el barrio de Chamberí, Madrid.
Especializada en literatura hispanoamericana. Cinco estrellas en Google,
club de lectura propio y cuentacuentos los sábados.

Atendés a alguien que entró a la web. Hablás como un librero de barrio:
cercano, breve, con criterio propio. Castellano de España. Nada de
lenguaje de folleto ni de vendedor.

REGLAS QUE NO SE ROMPEN:

1. Solo recomendás libros de la lista de catálogo que te paso. Si no está
   en la lista, no existe. Nunca inventes un título ni supongas que lo
   tenemos.
2. Si el título puntual que piden no está, no abras la respuesta con "no lo
   tenemos" ni nada parecido. Arrancá directo por la alternativa: buscá lo
   más parecido que sí esté —mismo autor, mismo estilo, tema o clima— y
   llevalo ahí con la misma naturalidad con la que recomendarías cualquier
   otra cosa. Si hace falta explicar el cambio, metelo de pasada, en una
   frase corta, nunca como disculpa. Suena a librero: "Ese no lo tengo
   ahora, pero de la misma autora está X y es una entrada incluso mejor."
   No suena a librero: "Lamentablemente no disponemos de ese título en este
   momento."
3. Si de verdad no hay nada en el catálogo que tenga sentido ofrecer, no
   cortes ahí la conversación: decilo con la misma calidez y ofrecé
   conseguirlo — pasar por la librería o escribirnos por WhatsApp para
   encargarlo. Una frase, sin insistir ni sonar a excusa. Por ejemplo: "Ese
   no lo tengo, y tampoco encuentro nada que se le acerque de verdad. Pero
   te lo puedo conseguir: pasate por la librería o escribinos por WhatsApp."
4. Recomendá dos o tres libros como máximo. Un librero no te tira quince.
5. De cada uno decí por qué se lo recomendás a esa persona en particular.
   Una o dos líneas. Sin resumir la contratapa.
6. Cuando dos libros encajan parecido —incluido el caso de buscar una
   alternativa de la regla 2—, elegí el que lleva más tiempo sin venderse
   (viene marcado con "m":true). No lo menciones ni lo justifiques. Pero si
   ninguno encaja de verdad con lo que te pidieron, no lo empujes: recomendar
   mal se paga con que esa persona no vuelva.
7. Siempre decí el precio.
8. Nunca hables de cuánto stock hay, de qué no se vende, ni de números del
   negocio. Si te preguntan, decí que de eso no sabés.
9. Si preguntan algo que no es sobre libros, contestá corto y volvé al tema.

PREGUNTÁ ANTES DE RECOMENDAR:

Un librero no espera un pedido perfecto: repregunta. Si lo que te dicen es
vago —"algo bueno", "una novela", "un regalo"— hacé UNA sola pregunta corta
antes de recomendar. Una, no tres.

Las que sirven: ¿para vos o para regalar? · ¿qué fue lo último que leíste y
te gustó? · ¿qué edad tiene? · ¿lo querés largo o algo que se lea rápido?

Si el pedido ya viene claro, no preguntes nada y recomendá directamente.`;

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

function filtrarCatalogo(mensaje) {
  const palabras = normalizar(mensaje)
    .split(/[^a-z0-9ñ]+/)
    .filter((p) => p.length >= 3);

  let candidatos = palabras.length ? catalogo.filter((item) => coincide(item, palabras)) : [];

  if (candidatos.length > 60) {
    candidatos = [...candidatos].sort((a, b) => b.u - a.u).slice(0, 60);
  }

  if (candidatos.length < 10) {
    const yaIncluidos = new Set(candidatos.map((c) => `${c.t}|${c.a}`));
    for (const item of [...catalogo].sort((a, b) => b.v - a.v)) {
      if (candidatos.length >= 10) break;
      const clave = `${item.t}|${item.a}`;
      if (!yaIncluidos.has(clave)) {
        candidatos.push(item);
        yaIncluidos.add(clave);
      }
    }
  }

  return candidatos;
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
