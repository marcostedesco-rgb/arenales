// Librería Arenales — Panel de rotación, con clave
// Devuelve el informe liviano al entrar (sin listas completas) y, si piden
// una lista puntual, esa lista completa y nada más. La clave nunca se
// compara con una comparación que corte en la primera diferencia.

import crypto from 'node:crypto';
import analisis from './_datos/analisis.js';

const LIMITE_INTENTOS_POR_HORA = 10;
const VENTANA_MS = 60 * 60 * 1000;
const SEGMENTOS_VALIDOS = new Set(['liquidar', 'devolver', 'reponer', 'destacar']);

const intentos = new Map(); // ip -> [timestamps en la última hora]

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

function clavesIguales(a, b) {
  // Se hashea antes de comparar para que dos strings de largo distinto no
  // corten la comparación antes de tiempo y filtren información por el
  // tiempo de respuesta.
  const ha = crypto.createHash('sha256').update(String(a)).digest();
  const hb = crypto.createHash('sha256').update(String(b)).digest();
  return crypto.timingSafeEqual(ha, hb);
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Método no permitido' });
    return;
  }

  if (limiteExcedido(obtenerIp(req), LIMITE_INTENTOS_POR_HORA)) {
    res.status(429).json({ error: 'Demasiados intentos. Probá de nuevo en una hora.' });
    return;
  }

  const { clave, lista } = req.body || {};
  const esperada = process.env.PANEL_PASSWORD || '';

  if (typeof clave !== 'string' || !clavesIguales(clave, esperada)) {
    res.status(401).json({ error: 'No autorizado' });
    return;
  }

  if (lista !== undefined) {
    if (typeof lista !== 'string' || !SEGMENTOS_VALIDOS.has(lista)) {
      res.status(400).json({ error: 'Lista inválida' });
      return;
    }
    res.status(200).json({ lista: analisis.listas[lista] });
    return;
  }

  res.status(200).json({
    generado: analisis.generado,
    panorama: analisis.panorama,
    segmentos: analisis.segmentos,
    liquidar: analisis.liquidar.slice(0, 10),
    devolver: analisis.devolver.slice(0, 10),
    reponer: analisis.reponer.slice(0, 10),
    destacar: analisis.destacar.slice(0, 10),
  });
}
