# Informe por mail con formato

Para Claude Code. Leé `CLAUDE.md` primero.

**Mostrame el plan antes de tocar archivos.**

Dos cosas: un arreglo en el lector de CSV y el formato del mail.

---

## 1 · Arreglo en `parsers.py` — hacelo primero

`leer_stock_csv()` devuelve diccionarios **sin** las claves `autor`,
`editorial` ni `cod_editorial`. El lector de PDF sí las devuelve.

La consecuencia es grave y silenciosa: `analisis.py` filtra el libro usado
buscando `CONFIG["editoriales_excluidas"]` dentro de `a.get("editorial", "")`,
que en el camino CSV siempre está vacío. **La exclusión no se aplica y nadie se
entera**, porque el informe sale igual, solo que con 104 títulos de más.

Arreglar:

- Que `leer_stock_csv()` devuelva siempre las tres claves, vacías si la columna
  no está en el archivo.
- Que reconozca las columnas `Autor` y `Editorial` cuando existan, con la misma
  lógica tolerante de alias que ya usa para las otras.
- Que `analisis.py` **avise por stderr** si hay editoriales configuradas para
  excluir y ninguna fila trae editorial. Algo como:
  `[aviso] Se pidió excluir LAURA TEDESCO pero el archivo no trae columna de
  editorial: no se excluyó nada.`

Ese aviso es lo que evita que el error vuelva a pasar desapercibido.

**Verificar** con el `data/stock.csv` nuevo, que ya trae Editorial:

```bash
python3 analisis.py data/stock.csv data/ventas.csv > output/analisis.json
python3 -c "import json;d=json.load(open('output/analisis.json'));print(d['panorama']['titulos'], d['excluido'])"
```

Tiene que imprimir `2676` y el bloque de excluido con `'titulos': 104`.

---

## 2 · El mail con formato

Hoy el cuerpo es texto plano y se lee como un bloque. Convertirlo en HTML.

El markdown que produce Claude **no cambia**: el archivo `.md` que se guarda en
`output/` sigue igual. El HTML se arma solo para el mail, en el nodo
`Componer el informe` de `n8n_workflow.json`.

### Restricciones de correo, no son opcionales

- **Maquetar con `<table>`**, nunca con flexbox ni grid: Outlook no los soporta.
- **Estilos en línea** en cada etiqueta. Nada de hojas externas ni `<style>`.
- **Sin imágenes ni tipografías externas**: la mayoría de los clientes las
  bloquean. Los iconos son **emoji**, que se ven en todos lados.
- Ancho máximo **600 px**, centrado, y que se lea bien en un teléfono.
- Tipografía: `-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.

### Paleta

| Uso | Color |
|---|---|
| Verde corporativo | `#004226` |
| Verde sobre fondo oscuro | `#0A5534` |
| Fondo de la página | `#FBFAF8` |
| Tarjeta positiva | `#E3EEE8` |
| Tarjeta de alerta | `#F8E9E8` |
| Beige de acento | `#E2D4CB` |
| Texto | `#2A2A2A` |
| Texto secundario | `#6B6B6B` |

### Estructura

**Cabecera** — fondo `#004226`, texto blanco.
Título *Librería Arenales*, debajo *Informe de rotación* y el mes en curso.
Y en letra chica, en `#8FB3A0`: *Ventas del {periodo_desde} al {periodo_hasta}*.

**Banda de KPIs** — cuatro tarjetas en una tabla de **2 columnas × 2 filas**,
para que en el teléfono se lean bien. Cada una: el número grande (26 px, negrita,
`#004226`) y debajo la etiqueta chica (11 px, `#6B6B6B`).

| Tarjeta | Número | Etiqueta | Fondo |
|---|---|---|---|
| 1 | `valor_stock_eur` | en estanterías | `#E3EEE8` |
| 2 | `pct_titulos_sin_venta` % | sin vender en {meses} meses | `#F8E9E8` |
| 3 | `rotacion_meses` | meses de rotación · objetivo {rotacion_objetivo} | `#F8E9E8` |
| 4 | `caja_recuperable_estimada_eur` | caja recuperable estimada | `#E3EEE8` |

Los importes en euros, formato español: `€63.552`.

**Cuerpo** — el markdown de Claude convertido a HTML.

**Pie** — fondo `#FBFAF8`, texto `#6B6B6B` de 11 px: *Generado
automáticamente el {fecha}. Próximo informe: el día 1 del mes que viene.*

### Cómo convertir el markdown

Escribir una función chica, sin librerías externas. Tiene que cubrir lo que el
informe realmente usa:

**`## Título` → cabecera de sección.** Fondo `#004226`, texto blanco, 16 px
negrita, con 12 px de relleno y esquinas redondeadas, y un emoji delante según
el título:

| Sección | Emoji |
|---|---|
| Lo que hay que hacer este mes | 🎯 |
| Devolver y liquidar | 📦 |
| Reponer con urgencia | ⚠️ |
| Para el mostrador | ⭐ |
| Lo que aprendimos | 💡 |
| cualquier otra | 📄 |

**`**negrita**` → `<strong>` en `#004226`.** Es lo que resalta los títulos de
los libros y las acciones, así que tiene que destacarse de verdad.

**`*cursiva*` → `<em>`.**

**Tablas** → `<table>` con encabezado de fondo `#004226` y texto blanco, filas
alternadas en blanco y `#F4F2EE`, bordes finos `#E8E6E2`, 13 px.

**Listas numeradas y con viñetas** → `<ol>` y `<ul>` con espacio entre ítems.

**Párrafos** → `<p>` con `line-height: 1.6` y 12 px de separación.

**`---`** → no dibujar una línea: ya separan las cabeceras de sección. Ignorarlo.

Los bloques que arrancan con `**N.` dentro de "Lo que hay que hacer este mes"
son las tres acciones principales. Envolverlos en una tarjeta de fondo
`#FBFAF8` con borde izquierdo grueso de 3 px en `#004226`, para que se lean como
tres bloques y no como un párrafo largo.

### En el nodo de mail

El nodo `Enviar por mail` tiene que mandar **HTML**, no texto plano. En n8n eso
es poner `emailFormat` en `html` y usar el campo `html` en lugar de `text`.

Incluir igual una versión en texto plano como alternativa, para los clientes que
no muestran HTML.

---

## Probar

1. Ejecutar el workflow en n8n y ver que llegue el mail.
2. Abrirlo en el teléfono: tiene que leerse sin zoom y sin desplazamiento
   lateral.
3. Comprobar que los cuatro KPI muestran los números nuevos: **2.676 títulos** y
   **€63.552**, no los viejos.
4. Confirmar que `output/informe_*.md` sigue siendo markdown limpio, sin HTML.
