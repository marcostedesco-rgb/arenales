# Web de Arenales · reestructura en 4 secciones

Para Claude Code, en `~/arenales`. **Mostrame el plan antes de tocar archivos.**

Hoy `web/index.html` es una página corrida. Pasa a ser una página con cuatro
secciones y un menú fijo arriba.

**Lo que no se toca:** la paleta, las tipografías y el diseño que ya tiene la
página. Todo lo nuevo se construye con los mismos estilos que ya están
definidos. Si hace falta un color o un tamaño que no existe, avisame antes de
inventarlo.

**Lo que tampoco se toca:** `api/chat.js`, `api/panel.js`, `api/_datos/*` y
`panel.html`. Esta reestructura es solo de la cara pública.

---

## 0 · El menú

Barra fija arriba, que se queda visible al bajar. Cuatro enlaces a anclas:

`La librería` · `El espacio` · `Novedades` · `Hablá con el librero`

En móvil, los cuatro enlaces en una fila que puede desplazarse en horizontal.
Nada de menú hamburguesa: son cuatro, entran.

El enlace al chat va destacado —fondo del color de acento, el resto en texto
plano—. Es lo que diferencia esta web de cualquier otra librería y queda cuarto
en la página; el menú compensa esa distancia.

---

## 1 · La librería — `#libreria`

Es lo que ya hay, con una corrección: hoy los bloques **Visitanos**, **Horario**
y **Contacto** son encabezados sin contenido debajo. Quedaron vacíos.

Rellenalos con las constantes que ya están declaradas al principio del archivo.
Si alguna no existe todavía —los horarios, sobre todo— creala vacía con un
comentario `// COMPLETAR` y avisame cuáles faltan en tu resumen final.

El resto igual: encabezado, la línea de identidad, la galería de tres fotos y el
pie con Instagram, WhatsApp y Google Maps.

---

## 2 · El espacio — `#espacio`

Sección nueva. El objetivo es que alguien que busca dónde grabar, presentar un
libro o dar un taller entienda en diez segundos que este lugar sirve, y sepa
cómo preguntar.

El orden está pensado para eso: **primero la prueba de que ya se usa**, después
cómo es, y al final los datos.

### 2.0 · Los archivos

Copiar a `web/img/espacio/`:

| Archivo | Qué es |
|---|---|
| `espacio-recorrido.mp4` | Recorrido de 46 s, vertical, sin sonido, 4,9 MB |
| `recorrido-poster.jpg` | Imagen fija del video |
| `sala-eventos.jpg` | La sala del fondo — es la que importa |
| `pasillo.jpg` | El pasillo de ladrillo visto |
| `estanterias.jpg` | Las estanterías llenas |
| `rincon-infantil.jpg` | El rincón infantil con la alfombra |
| `fachada.jpg` | La fachada desde la calle |

### 2.1 · Encabezado y prueba

Título: **El espacio**. Debajo, un párrafo corto: una sala al fondo de la
librería, con pared de ladrillo visto, luz natural e insonorización de local
—entre estanterías de libros, que es lo que ningún estudio te da—.

Inmediatamente después, **el bloque que hace el trabajo**: en esta sala se graba
*Pensar Cuba*, la serie de entrevistas de **elTOQUE** con Julio A. Fernández
Estrada. Una línea que lo diga y el reproductor de la lista:

```
https://www.youtube.com/playlist?list=PLI19GhFs5U5CKGqHDhS8EMyinFrt6Lhjs
```

**Cómo embeberlo — importa.** No pongas el `<iframe>` de YouTube directo: carga
alrededor de un megabyte de JavaScript y rastreadores en cuanto abre la página,
aunque nadie le dé play. Usá el patrón de *fachada*: mostrás la miniatura de
YouTube con un botón de reproducir encima, y el `<iframe>` real se inserta
recién al hacer clic. Son unas quince líneas de JavaScript, sin dependencias.

La miniatura se trae de `https://i.ytimg.com/vi/ID_DEL_VIDEO/hqdefault.jpg`.

> **Las dos capturas del canal no las subas.** Son fotogramas de un video de
> elTOQUE: publicarlos en la web comercial de la librería es usar material de
> otro. Embebiendo el video estás enlazando a su canal, que es correcto y además
> les suma visitas. Si querés una imagen fija de una grabación, lo que
> corresponde es pedirles una foto y acreditarla.

### 2.2 · El recorrido en video

`espacio-recorrido.mp4`, con estos atributos: `controls`, `playsinline`,
`preload="metadata"` y `poster="/img/espacio/recorrido-poster.jpg"`.

**Sin autoplay y sin loop.** Son 4,9 MB: que los baje quien decidió mirarlo.
`preload="metadata"` hace que la página solo pida la cabecera del archivo hasta
que le dan play.

Es vertical. En escritorio va a la izquierda con un ancho máximo de 340 px, y la
ficha de datos (2.3) a la derecha. En móvil, uno debajo del otro.

### 2.3 · La ficha

Tarjetas cortas, un dato por tarjeta:

- **Capacidad** — `// COMPLETAR` personas sentadas
- **Superficie** — `// COMPLETAR` m²
- **Equipamiento** — sillas, mesa baja, wifi, iluminación de riel dirigible
- **Luz natural** — ventana al patio interior
- **Bueno para** — grabación de pódcast y entrevistas, presentaciones de libro,
  clubes de lectura, talleres, reuniones pequeñas
- **Horarios** — fuera del horario comercial y los días que la librería cierra

Marcá con `// COMPLETAR` los dos datos que no tenemos y avisame en el resumen.

### 2.4 · La galería

Las cinco fotos en cuadrícula: tres columnas en escritorio, una en móvil. Al
hacer clic se amplían sobre fondo oscuro; se cierra con Escape o clicando fuera.
Sin librerías externas.

`sala-eventos.jpg` va primera y ocupa el doble de ancho que las demás. Es la que
vende; el resto es contexto.

Los nombres de archivo y los pies de foto, en un array de constantes al
principio del archivo. Que agregar una foto sea agregar una línea.

### 2.5 · Cómo consultar

Sin formulario: necesitaría una función nueva en Vercel, un servicio de envío y
mantenimiento. Dos botones con el texto ya cargado consiguen lo mismo y no se
rompen nunca.

- **WhatsApp** — `https://wa.me/34679785293?text=` + el mensaje codificado
  *"Hola, quería consultar por el espacio de la librería para un evento."*
- **Correo** — `mailto:contacto@arenaleslibreria.com` con asunto *"Consulta por
  el espacio"* y un cuerpo con cuatro líneas a completar: fecha tentativa, tipo
  de evento, cuánta gente, horario.

**El precio no va.** Va por consulta, que mientras no haya tarifa fija te deja
negociar según el evento y evita que el primer contacto sea un número que
espanta.

### 2.6 · Para compartir

Esta sección se va a mandar por WhatsApp y por correo a productoras y editoriales,
así que tiene que tener su propio enlace decente: `arenaleslibreria.com/#espacio`
con etiquetas Open Graph propias no se puede, porque las etiquetas son de toda la
página.

Si querés que el link compartido muestre la sala y no la portada de la librería,
hay que hacer `espacio.html` aparte. Decime y lo agrego; con una sola página,
el enlace compartido va a mostrar siempre la imagen de la librería.

---

## 3 · Novedades — `#novedades`

Acá va el newsletter. Para septiembre usamos la versión ya corregida, en una
sola página continua. **En octubre esto cambia** — ver 3.4.

### 3.1 · Los archivos

Copiar a `web/newsletter/`:

- `2026-09.png` — el newsletter entero, 1624 × 6682 px
- `2026-09.pdf` — el mismo, en una sola página, para descargar

### 3.2 · Mostrarlo

**Se muestra el PNG, no el PDF.** Una imagen se adapta al ancho del teléfono
sola; un PDF embebido abre un visor que en móvil obliga a hacer zoom y a veces
directamente se baja el archivo en lugar de mostrarlo.

```html
<img src="/newsletter/2026-09.png" alt="Newsletter de septiembre 2026"
     loading="lazy">
```

Con `width: 100%; max-width: 640px; height: auto;` y centrado. Al hacer clic,
se amplía igual que las fotos del espacio.

**Arriba:** una línea con el mes que se está viendo, y un selector con los
números anteriores. Con uno solo, el selector no se muestra. La lista va en un
array de constantes:

```js
const NEWSLETTERS = [
  { id: "2026-09", titulo: "Septiembre 2026" },
];
```

**Abajo, dos botones:** *Descargar en PDF* (a `/newsletter/2026-09.pdf`) y
*Suscribirme*, que lleva al formulario de alta de la plataforma de correo.

`loading="lazy"` no es opcional: la imagen pesa 3 MB y no tiene que frenar la
carga de la página.

### 3.3 · Antes de publicar

Optimizá el PNG, que 3 MB es mucho para una web:

```bash
brew install pngquant
pngquant --quality 65-85 --force --output 2026-09.png 2026-09.png
```

Tiene que bajar a menos de 1 MB. Miralo después al 100% para confirmar que el
texto sigue nítido; si se degradó, subí el rango a `80-95`.

### 3.4 · Octubre: pasamos al HTML

Esta versión en imagen resuelve septiembre, pero tiene tres límites: pesa,
Google no puede leer el texto, y el calendario de eventos no se puede copiar ni
clicar.

Cuando salga el número de octubre, buscá en el correo el enlace **"Ver en el
navegador"**, copiá esa URL y guardala. Con eso servimos el HTML real:

```bash
curl -sL "LA_URL" -o ~/arenales/web/newsletter/2026-10.html
```

y se muestra en un `<iframe>` del mismo origen, al que se le ajusta la altura
al contenido por JavaScript para que no tenga barra interna. Idéntico al correo,
liviano, y con el texto indexable.

Dejá la sección preparada para las dos cosas: si la entrada del array tiene
`archivo`, se muestra el iframe; si no, la imagen. Así octubre es agregar una
línea.

---

## 4 · Hablá con el librero — `#chat`

El chat que ya existe, movido a su propia sección con un título y una línea que
explique qué es: *"Un librero que atiende a cualquier hora y solo recomienda
libros que están hoy en la estantería."*

**Además, un botón flotante** abajo a la derecha, visible en toda la página, que
baja hasta acá. Redondo, con el icono de conversación, del color de acento.
Cuando la sección del chat está en pantalla, se oculta.

Motivo: el chat pasó de ser lo primero que se ve a ser lo último. Sin algo que
lo traiga, lo va a usar bastante menos gente.

---

## Al terminar

- [ ] Las cuatro secciones se ven bien en móvil, sin desplazamiento horizontal
- [ ] El menú fijo no tapa el título de la sección al saltar a ella
- [ ] El iframe del newsletter se ve entero, sin barra interna, y las imágenes
      cargan
- [ ] El chat sigue funcionando igual que antes
- [ ] Los botones de WhatsApp y correo abren con el texto ya escrito
- [ ] Ampliar una foto y cerrarla con Escape funciona
- [ ] `curl -s -o /dev/null -w "%{http_code}" https://www.arenaleslibreria.com/api/_datos/catalogo.js`
      sigue dando **404**

Y decime en el resumen qué constantes quedaron con `// COMPLETAR`.
