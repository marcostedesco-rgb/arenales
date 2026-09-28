# Rediseño de la web de Arenales

Para Claude Code, en `~/arenales`. **Mostrame el plan antes de tocar archivos.**

Hay una maqueta aprobada. Este documento dice cómo llevarla a la web real.

---

## 0 · Lo que NO se toca

- `web/api/chat.js`, `web/api/panel.js`, `web/api/_datos/*` — la lógica y los datos
  quedan exactamente como están.
- `web/panel.html` — el panel privado no cambia y **no se enlaza desde ninguna
  parte**. Quien lo necesita conoce la dirección.
- Las variables de entorno de Vercel.

Esto es un cambio de la cara pública y nada más. Si algo te obliga a tocar
`api/`, parás y me avisás.

---

## 1 · Los archivos de la maqueta

Descomprimir `maqueta-arenales.zip` y copiar así:

| Del zip | A |
|---|---|
| `maqueta.html` | `web/index.html` |
| `chat.html` | `web/chat.html` |
| `newsletter.html` | `web/newsletter.html` |
| `img/espacio/*` | `web/img/espacio/` |

**Al copiar `maqueta.html` a `index.html`, reemplazar todos los `maqueta.html`
de los enlaces por `index.html`.** Están en la marca del encabezado, en el menú
y en los "Volver a la librería" de las otras dos páginas. Son unos ocho.

Y borrar de la maqueta la barra de aviso: el `<div class="aviso">` y su regla
CSS, en las tres páginas. Era para revisarla, no va en producción.

---

## 2 · El diseño es el de la maqueta, tal cual

**No rediseñes nada.** El bloque `:root` con las variables de color, la
tipografía Montserrat, los tamaños, los filetes y el espaciado se copian como
están. Si algo no entra o se rompe en algún ancho, avisame antes de cambiar un
valor.

Dos cosas que importan y que es fácil romper sin querer:

**Los colores salen de dos variables, no de valores sueltos.** `--marca` es el
color del texto de los títulos y `--solido` el fondo de los botones y la cinta.
En claro las dos son el verde del cartel; en oscuro las dos son blanco. Si
agregás un elemento nuevo, usá esas variables, nunca un color escrito a mano.

**Las tres páginas comparten el mismo bloque de estilos.** Hoy está repetido en
cada archivo. Dejalo repetido — son tres archivos, no vale la pena montar un CSS
externo y una petición más. Pero si cambiás una variable, cambiala en las tres.

---

## 3 · El chat se muda a su propia página

Hoy el chat vive dentro de `index.html`. Pasa a `chat.html`.

**En `index.html`:** sacar el bloque del chat, su JavaScript y sus estilos. En su
lugar queda el botón flotante que ya viene en la maqueta, que enlaza a
`chat.html`. Ese botón va también en `newsletter.html`, con el mismo marcado.

**En `chat.html`:** la maqueta trae una conversación de ejemplo escrita a mano
dentro de `<div class="hilo">`. **Borrala entera** y conectá ahí el JavaScript
que hoy está en `index.html`, respetando las clases de la maqueta:

- Mensaje del librero → `<div class="msg de-el">`
- Mensaje del visitante → `<div class="msg de-vos">`
- El campo y el botón ya están, con las clases `.campo` y sus hijos.

El primer mensaje del librero —el saludo— sí se queda, como estado inicial.

**Las cuatro preguntas sugeridas** (`.chip`) tienen que funcionar: al hacer clic,
escriben su texto en el campo y envían, igual que si lo hubiera tecleado la
persona.

**El endpoint no cambia:** sigue siendo el mismo `fetch` a `/api/chat` que ya
funciona. No toques el formato del cuerpo ni la respuesta.

Cuando el hilo crece, que baje solo al último mensaje. Y mientras espera la
respuesta, algún indicador — un `.msg.de-el` con tres puntos alcanza.

---

## 4 · Los textos y datos, en constantes

Al principio de `index.html`, un bloque de constantes comentado, agrupado y con
los que faltan marcados. Que cambiar un horario no sea buscar entre el HTML.

```js
const LIBRERIA = {
  direccion:  "C. de Vallehermoso, 110",
  barrio:     "Barrio de Chamberí, Madrid · metro Canal",
  maps:       "https://maps.google.com/?q=...",   // COMPLETAR con el enlace real de la ficha
  telefono:   "679 78 52 93",
  whatsapp:   "34679785293",
  correo:     "contacto@arenaleslibreria.com",
  instagram:  "https://www.instagram.com/arenales.libreria/",
  horario:    { dias: "De martes a sábado", manana: "10:00 – 14:00", tarde: "17:00 – 21:00" },
};

const CINTA = [
  "Cuentacuentos los sábados a las 12",
  "Club de lectura con el Teatro de la Abadía",
  "Presentaciones y grabaciones en la sala del fondo",
  "3×2 en libros de segunda mano",
];

const ESPACIO = {
  capacidad:    "20 personas sentadas",
  superficie:   "40 m²",
  equipamiento: "Sillas, mesa baja, wifi, luz de riel",
  luz:          "Ventana al patio interior",
  bueno:        "Presentaciones, pódcast, talleres, clubes",
  horarios:     "Fuera del horario comercial",
  playlist:     "https://www.youtube.com/playlist?list=PLI19GhFs5U5CKGqHDhS8EMyinFrt6Lhjs",
};

const BOLETINES = [
  { id: "2026-09", titulo: "Septiembre 2026",
    imagen: "img/espacio/newsletter-completo.jpg",
    portada: "img/espacio/newsletter-portada.jpg",
    pdf: "newsletter/2026-09.pdf" },
];

const ALTA_BOLETIN = "";  // COMPLETAR: URL del formulario de alta de la plataforma de correo
```

`CINTA` se repite dos veces seguidas dentro del `<div>` que se desplaza — así el
bucle no deja un hueco al volver a empezar. Está hecho así en la maqueta.

`BOLETINES` lo usan las dos páginas: `index.html` muestra el primero del array
como portada, y `newsletter.html` arma el selector con todos y muestra el que se
elija. Con uno solo, el selector se oculta.

**Decime en el resumen final qué constantes quedaron vacías.**

---

## 5 · Dos cosas que faltan

**La foto de la sala.** La sección del espacio se apoya solo en el video. Dejá
previsto `img/espacio/sala.jpg` y, si el archivo no existe, que esa parte no se
muestre en vez de romperse con una imagen rota.

**El formulario de alta.** Mientras `ALTA_BOLETIN` esté vacío, el botón
*Suscribirme* tiene que abrir un `mailto:` a la dirección de la librería con el
asunto *"Quiero suscribirme al boletín"*. Nunca un botón que no hace nada.

---

## 6 · Etiquetas para compartir

En las tres páginas, `<title>`, `description` y Open Graph propios — distintos en
cada una, que es la mitad de la gracia de tenerlas separadas:

| Página | title | og:image |
|---|---|---|
| `index.html` | Librería Arenales · Chamberí, Madrid | `img/espacio/fachada.jpg` |
| `chat.html` | Habla con el librero · Librería Arenales | `img/espacio/narrativa.jpg` |
| `newsletter.html` | El boletín · Librería Arenales | `img/espacio/newsletter-portada.jpg` |

`og:url` absoluto, con `https://www.arenaleslibreria.com/...`.

Así el enlace del espacio que se manda a una productora muestra la librería, y
el del boletín muestra la portada del mes.

---

## 7 · Peso

La página trae fotos grandes y un video. Antes de publicar:

- Todas las `<img>` menos la primera, con `loading="lazy"`.
- El video se queda con `preload="metadata"` y sin `autoplay`. Son 4,9 MB.
- `img/espacio/newsletter-completo.jpg` solo lo carga `newsletter.html`.

Decime cuánto pesa la portada de `index.html` con todo cargado. Si pasa de
2,5 MB, volvemos sobre las fotos.

---

## 8 · Probar

`npx vercel dev`, y en este orden:

**Que no se rompió nada de lo que ya andaba**

- [ ] El chat responde en `/chat.html` igual que antes, y solo nombra libros del
      catálogo
- [ ] Preguntarle *"¿qué libros tenéis hace mucho que no vendéis?"* — lo esquiva
- [ ] `/panel.html` sigue pidiendo clave y muestra los mismos números
- [ ] Los CSV del panel se descargan

**Lo nuevo**

- [ ] El botón flotante aparece en las tres páginas y lleva al chat
- [ ] Las cuatro preguntas sugeridas escriben y envían
- [ ] La portada del boletín abre `newsletter.html` y se ve entero
- [ ] Los enlaces de Maps abren la ficha correcta
- [ ] Los botones del espacio abren WhatsApp y el correo con el texto cargado

**Los dos anchos**

- [ ] A 375 px no hay desplazamiento horizontal en ninguna página
- [ ] La galería pasa a dos columnas y las fotos quedan cuadradas
- [ ] El botón flotante no tapa nada importante

**Seguridad, que no se saltea**

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://www.arenaleslibreria.com/api/_datos/catalogo.js
curl -s -o /dev/null -w "%{http_code}\n" https://www.arenaleslibreria.com/api/_datos/analisis.js
```

Los dos tienen que dar **404** después de publicar.

---

## 9 · Publicar

Commit en la terminal y **Push desde GitHub Desktop**, como siempre. Vercel
publica solo. Después, repetir los dos `curl` contra el dominio real.

No hace falta tocar nada en Vercel: son tres archivos estáticos más y una
carpeta de imágenes. El *Root Directory* sigue siendo `web`.
