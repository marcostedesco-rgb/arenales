# Especificación de la web — Librería Arenales

Para Claude Code. Leé también `CLAUDE.md` antes de empezar.

**Antes de escribir código, mostrame el plan de archivos y esperá que lo apruebe.**

---

## Qué hay que construir

Dos cosas con **públicos distintos que no se mezclan**:

| Página | Para quién | Acceso |
|---|---|---|
| **Chat librero** | Clientes de la librería | Público |
| **Panel de rotación** | Socios y quien atiende | Con clave |

**Sin framework.** Nada de Next.js, React ni build step. HTML, CSS y JavaScript
plano. Vercel sirve los estáticos y dos funciones en `/api`.

---

## Regla de seguridad, antes que nada

**Ningún dato del negocio puede quedar como archivo servible.**

El informe tiene el valor del inventario, el capital inmovilizado y qué no se
vende. El catálogo tiene el stock por título y la marca de cuáles están
parados. Si eso queda como `.json` en el proyecto, se descarga entrando a la
URL directa, aunque ninguna página lo enlace.

Por eso los datos se generan como **módulos JavaScript dentro de
`api/_datos/`**. Vercel no expone como ruta nada que empiece con `_`, y esos
archivos solo los pueden leer las funciones del servidor. El navegador nunca
recibe el catálogo ni el informe: recibe la respuesta del chat, o los datos del
panel si presentó la clave.

---

## Estructura

```
web/
  index.html                chat público
  panel.html                panel, pide clave
  api/
    chat.js                 responde al chat
    panel.js                verifica la clave y devuelve el informe
    _datos/
      catalogo.js           generado — nunca servido
      analisis.js           generado — nunca servido
```

---

## 1 · `catalogo.py` (nuevo, en la raíz del proyecto)

Reutiliza `parsers.py` y la exclusión de editoriales de `analisis.py`.
Genera los dos módulos.

**`web/api/_datos/catalogo.js`** — un objeto por título con stock > 0:

```js
module.exports = [
  {"t":"título","a":"autor","e":"editorial","p":19.9,"u":3,"v":12,"m":false}
]
```

`p` = PVP · `u` = unidades en stock · `v` = vendidas en el período ·
`m` = true si no vendió nada. Claves cortas a propósito: va entero al prompt.

**`web/api/_datos/analisis.js`** — `module.exports = ` con el contenido de
`output/analisis.json`.

Ese archivo ahora incluye una clave `listas` con las fichas **completas** de los
segmentos accionables, no solo las primeras veinte. Son unas 2.700 filas, así
que el módulo pesa cerca de un megabyte. No es problema para la función, que lo
carga una sola vez, pero sí importa para lo que se le manda al navegador: ver el
punto 4.

---

## 2 · `index.html` — el chat, público

Caja de mensajes y campo de texto. Al enviar hace `POST /api/chat` con
`{mensaje, historial}`.

Tres preguntas de ejemplo como botones, para probar sin escribir:
*"Leí todo Bolaño, ¿qué me recomendás?"* · *"Algo para un nene de 8 años"* ·
*"¿Tenés poesía latinoamericana?"*

Arriba, presentación breve de la librería. **Ningún enlace al panel**: quien lo
necesita conoce la dirección.

---

## 3 · `panel.html` — el informe, con clave

Al abrir pide la clave. La manda a `POST /api/panel`; si es correcta recibe los
datos y los dibuja. Guardar la clave en `sessionStorage` para no pedirla en cada
recarga.

Muestra:

- **Encabezado** con el período analizado: *Ventas del {periodo_desde} al
  {periodo_hasta}*, y la fecha en que se generó el análisis.
- **Fila de KPIs:** valor del stock, % de títulos sin venta, capital
  inmovilizado, rotación en meses, caja recuperable estimada.
- **Los seis segmentos** con títulos, ejemplares y valor.
- **Cuatro listas de acción:** Reponer (por `facturado_periodo`), Liquidar (por
  `valor_eur`), Devolver (por `valor_eur`) y Destacar (por `facturado_periodo`).
  **Los primeros 10 de cada una**, y debajo un botón **Descargar CSV** que trae
  la lista completa.

Los campos de cada ficha son `vendidas_periodo` y `facturado_periodo`. No
existen `vendidas_13m` ni `facturado_13m`: se renombraron.

**El botón de descarga** pide la lista completa a `/api/panel` y arma el CSV en
el navegador, con las mismas reglas que los adjuntos del mail: separador punto y
coma, UTF-8 con BOM, coma decimal y el EAN como texto.

---

## 4 · `api/panel.js`

```js
export default async function handler(req, res) { ... }
```

Solo `POST`. Compara el campo `clave` contra `process.env.PANEL_PASSWORD`.

- Correcta → devuelve los datos, **sin las listas completas**: `panorama`,
  `segmentos` y los primeros 10 de cada segmento. Es lo que se dibuja al entrar
  y tiene que ser liviano.
- Si además viene un campo `lista` con el nombre de un segmento
  (`liquidar`, `devolver`, `reponer` o `destacar`), devuelve **esa** lista
  completa desde `analisis.listas` y nada más. Es lo que pide el botón de
  descarga.
- Incorrecta → 401, sin decir por qué.
- Máximo 10 intentos por IP por hora. Después, 429.

Mandar el megabyte entero al entrar haría que el panel tarde en abrir en el
teléfono, que es donde lo van a mirar. Por eso las listas van solo cuando se
piden.

La comparación tiene que recorrer siempre la cadena completa, sin cortar en la
primera diferencia, para no filtrar información por el tiempo de respuesta.

---

## 5 · `api/chat.js`

1. Solo `POST`. Otro método, 405.
2. Valida: mensaje de hasta 500 caracteres, historial de hasta 10 turnos.
3. Carga `_datos/catalogo.js`.
4. **Filtra candidatos** con las palabras del mensaje contra título, autor y
   editorial. Más de 60 coincidencias, se queda con las 60 de mayor stock.
   Menos de 10, agrega los más vendidos para dar contexto.
5. Llama a la API de Anthropic con el system prompt de abajo.
6. Devuelve `{respuesta}` y **nada más**: ni el catálogo, ni los candidatos, ni
   la marca de stock muerto.

**Límites:** 15 mensajes por IP por hora, en memoria. `max_tokens: 700`. La key
sale de `process.env.ANTHROPIC_API_KEY` y nunca llega al cliente.

### System prompt

```
Sos el librero de Librería Arenales, en el barrio de Chamberí, Madrid.
Especializada en literatura hispanoamericana. Cinco estrellas en Google,
club de lectura propio y cuentacuentos los sábados.

Atendés a alguien que entró a la web. Hablás como un librero de barrio:
cercano, breve, con criterio propio. Castellano de España. Nada de
lenguaje de folleto ni de vendedor.

REGLAS QUE NO SE ROMPEN:

1. Solo recomendás libros de la lista de catálogo que te paso. Si no está
   en la lista, no existe. Nunca inventes un título ni supongas que lo
   tenemos.
2. Si no tenemos lo que buscan, decilo de frente y ofrecé lo más parecido
   que sí esté. "No lo tenemos, pero si te gustó X mirá Y."
3. Recomendá dos o tres libros como máximo. Un librero no te tira quince.
4. De cada uno decí por qué se lo recomendás a esa persona en particular.
   Una o dos líneas. Sin resumir la contratapa.
5. Cuando dos libros encajan parecido, elegí el que lleva más tiempo sin
   venderse (viene marcado con "m":true). No lo menciones ni lo justifiques.
   Pero si ninguno encaja de verdad con lo que te pidieron, no lo empujes:
   recomendar mal se paga con que esa persona no vuelva.
6. Siempre decí el precio.
7. Nunca hables de cuánto stock hay, de qué no se vende, ni de números del
   negocio. Si te preguntan, decí que de eso no sabés.
8. Si preguntan algo que no es sobre libros, contestá corto y volvé al tema.

PREGUNTÁ ANTES DE RECOMENDAR:

Un librero no espera un pedido perfecto: repregunta. Si lo que te dicen es
vago —"algo bueno", "una novela", "un regalo"— hacé UNA sola pregunta corta
antes de recomendar. Una, no tres.

Las que sirven: ¿para vos o para regalar? · ¿qué fue lo último que leíste y
te gustó? · ¿qué edad tiene? · ¿lo querés largo o algo que se lea rápido?

Si el pedido ya viene claro, no preguntes nada y recomendá directamente.
```

El catálogo filtrado va en el mensaje de usuario dentro de `<catalogo>`, en
JSON compacto. Modelo: `claude-sonnet-4-6`.

---

## 6 · Estética

Identidad de la librería, la misma de la presentación a los socios:

| Uso | Color |
|---|---|
| Verde corporativo | `#004226` |
| Verde sobre fondo oscuro | `#0A5534` |
| Fondo claro | `#FBFAF8` |
| Tarjeta positiva | `#E3EEE8` |
| Tarjeta de alerta | `#F8E9E8` |
| Beige de acento | `#E2D4CB` |

Tipografía del sistema. Tarjetas redondeadas, sombra suave. **Tiene que verse
bien en el celular**: es donde lo van a abrir el cliente y el jurado.

---

## 7 · Cómo probar

```bash
cd ~/arenales
python3 catalogo.py
cd web && npx vercel dev
```

Funcional:

- El chat responde y **solo nombra libros que están en el catálogo**.
- Pedirle algo que seguro no está: tiene que admitirlo, no inventar.
- Pedido vago: tiene que repreguntar una vez.
- El panel pide clave y muestra los números reales: **2.676 títulos** y
  **€63.552**. Si ves 2.780, está leyendo un análisis viejo.
- El encabezado muestra el período: *03/06/2025 al 26/06/2026*.
- Los cuatro botones de descarga traen el CSV completo. El de Liquidar tiene
  **613 filas**; el de Devolver, **1.658**.
- El CSV descargado abre bien en Excel: acentos correctos y el EAN completo,
  no en notación científica.
- Todo se lee bien en pantalla angosta.

**De separación de accesos, y esto no se salta:**

- `curl http://localhost:3000/api/_datos/catalogo.js` → tiene que dar 404.
- `curl http://localhost:3000/api/_datos/analisis.js` → tiene que dar 404.
- `POST /api/panel` con la clave equivocada → 401 y ningún dato.
- Preguntarle al chat *"¿cuánto stock tenés?"* o *"¿qué no se vende?"* →
  tiene que esquivarlo.
- Abrir el chat y mirar las herramientas de desarrollo: en ninguna respuesta
  del servidor puede aparecer el catálogo ni la marca `m`.

---

## Lo que NO hay que hacer

- Nada de base de datos vectorial ni embeddings. El catálogo entra en el prompt.
- Nada de framework ni de build step.
- Ningún archivo de datos fuera de `api/_datos/`.
- Ningún enlace al panel desde la página pública.
- La API key y la clave del panel nunca en un archivo que llegue al navegador.
- No commitear `.env` ni ninguna clave. Verificar con `grep -r "sk-ant" .` antes
  de subir.
