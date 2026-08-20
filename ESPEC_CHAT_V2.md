# Ajustes al chat librero

Para Claude Code, en `~/arenales`. **Mostrame el plan antes de tocar archivos.**

Tres cambios: la selección de candidatos, el prompt y la dirección.

---

## 1 · Dar más material al modelo — `web/api/chat.js`

**El problema.** Hoy los candidatos salen de buscar las palabras del mensaje
dentro de título, autor y editorial. Eso funciona cuando piden un título o un
autor concreto, y falla siempre que piden un **género, un tema o un tono**:
nadie escribe "novela negra" en la portada de una novela negra.

El resultado es que el modelo recibe seis títulos irrelevantes y contesta que no
hay nada. Y tiene razón con lo que le dimos.

**El arreglo.** Que los candidatos sean siempre dos cosas juntas:

**a) Las coincidencias por palabra clave**, como hoy, hasta 80.

**b) Una muestra base de 120 títulos**, siempre, aunque haya coincidencias.
Armada así:

- 40 de los más vendidos del período (`v` más alto)
- 60 de stock muerto (`m: true`), los de mayor stock primero — es lo que
  queremos mover
- 20 repartidos por el resto del catálogo

Sin repetir títulos entre los tres grupos ni con las coincidencias.

Total: unos 200 títulos por consulta, alrededor de 6.000 tokens. Es asequible y
le da al modelo material real para trabajar.

**Variedad de sellos:** al armar la muestra, evitar que más de 8 títulos vengan
de la misma editorial. Si no, se llena de Alianza y Tusquets, que son las que
más volumen tienen.

---

## 2 · El prompt — reemplazo completo

Reemplazar el `system` de `api/chat.js` por este texto.

```
Eres el librero de Librería Arenales, en el barrio de Chamberí, Madrid.
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
- Si preguntan algo que no va de libros, contesta corto y vuelve al tema.
```

---

## 3 · La dirección — `web/index.html`

Donde dice:

> A media cuadra del Parque del Tercer Depósito, cerca del metro Canal.

Tiene que decir:

> A media cuadra del Parque del Canal de Isabel II, cerca del metro Canal.

La calle y el código postal quedan igual.

---

## Probar

En local, `npx vercel dev`, y estas cuatro consultas:

| Preguntar | Qué tiene que pasar |
|---|---|
| *"Quiero una novela negra"* | Recomienda algo del catálogo por cercanía, o repregunta. **No** puede abrir con un "no tenemos". |
| *"¿Tienes Cien años de soledad?"* | Si no está, ofrece alternativas primero y recién después menciona el encargo. |
| *"Busco poesía japonesa contemporánea"* | Caso extremo. Puede terminar en "no lo tenemos", pero solo después de repreguntar u ofrecer algo. |
| *"Algo para regalar"* | Una sola pregunta antes de recomendar. |

**Y la comprobación que no se salta:** ninguno de los títulos que nombre puede
ser inventado. Buscá dos o tres de los que recomiende dentro de
`api/_datos/catalogo.js` y confirmá que existen.

Si empieza a nombrar libros que no están en el catálogo, el cambio salió mal:
avisame antes de publicar.
