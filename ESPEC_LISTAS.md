# Listas de trabajo para ejecutar

Para Claude Code. Leé `CLAUDE.md` primero.

**Mostrame el plan antes de tocar archivos.**

---

## El problema

El informe dice *"liquidar 613 títulos"* y *"devolver 1.658"*, pero solo nombra
unos pocos como ejemplo. Quien atiende el mostrador no puede ejecutar eso: para
ir a la estantería necesita la lista completa, con el EAN y el precio.

Y hoy el dato ni siquiera existe: `_resumir()` en `analisis.py` guarda solo los
20 primeros de cada segmento.

---

## 1 · `analisis.py` — guardar las listas completas

Además de los `top` que ya devuelve, agregar una clave `listas` con **todas** las
fichas de los cuatro segmentos accionables:

```
listas: {
  liquidar: [...],   // completo, ordenado por valor_eur descendente
  devolver: [...],   // completo, ordenado por valor_eur descendente
  reponer:  [...],   // completo, ordenado por facturado_periodo descendente
  destacar: [...]    // completo, ordenado por facturado_periodo descendente
}
```

Cada ficha lleva además de lo que ya tiene: `autor` y `editorial`, que hoy se
pierden al construir la ficha aunque el parser los trae.

**Dos campos calculados nuevos:**

- En `liquidar`: `pvp_liquidacion` = `pvp × (1 − descuento_liquidacion)`,
  redondeado a dos decimales. Es el precio que va en la etiqueta.
- En `reponer`: `sugerido_pedir` = `max(1, ceil(ritmo_mensual × meses_reposicion)
  − unidades_stock)`. Agregar `meses_reposicion: 3` a `CONFIG`.

`informe.py` **no cambia**: sigue mandándole a Claude solo los `top`. Las listas
completas no van al prompt.

---

## 2 · `listas.py` (nuevo) — generar los CSV

Script que lee `output/analisis.json` y escribe en `output/listas/`:

| Archivo | Columnas |
|---|---|
| `liquidar_AAAA-MM.csv` | EAN · Título · Autor · Editorial · Ejemplares · PVP · Precio liquidación · Valor total · Hecho |
| `devolver_AAAA-MM.csv` | EAN · Título · Autor · Editorial · Ejemplares · PVP · Valor total · Hecho |
| `reponer_AAAA-MM.csv` | EAN · Título · Autor · Editorial · Vendidos · Stock actual · Facturado · Pedir · Hecho |
| `destacar_AAAA-MM.csv` | EAN · Título · Autor · Editorial · Vendidos · Stock actual · Facturado · Hecho |

Detalles que importan porque esto se abre en Excel en España:

- Separador **punto y coma**, codificación **UTF-8 con BOM**. Sin el BOM, Excel
  rompe los acentos.
- Los importes con **coma decimal**: `19,90`.
- El **EAN como texto**, no como número: Excel le come el cero inicial y lo pasa
  a notación científica. Prefijarlo con un apóstrofo o escribirlo entre comillas.
- La columna **Hecho** va vacía: es para que la tilden a mano.
- `devolver` y `liquidar` **ordenados por editorial y después por valor**, porque
  la devolución se gestiona con un distribuidor por vez.

---

## 3 · Adjuntarlas al mail

En `n8n_workflow.json`, después de `Componer el informe`, leer los cuatro CSV y
adjuntarlos al mail.

El nodo `Enviar por mail` soporta adjuntos desde propiedades binarias: hay que
cargar los archivos como binarios y listarlos en `attachments`.

En el cuerpo del mail, al final de la sección **📦 Devolver y liquidar**, agregar
una línea:

> *Las listas completas van adjuntas: 613 títulos para liquidar y 1.658 para
> devolver, con EAN y precio, listas para imprimir.*

Con los números tomados del análisis, no escritos a mano.

---

## 4 · Descarga desde el panel

En `web/`, que `/api/panel` devuelva también las listas completas, y que
`panel.html` muestre por cada segmento un botón **Descargar CSV** que arme el
archivo en el navegador a partir de esos datos.

Mismas reglas de formato que el punto 2: punto y coma, BOM, coma decimal, EAN
como texto.

**No agregar endpoints nuevos ni servir archivos**: las listas viajan por el
mismo `/api/panel` que ya pide clave. Son datos del negocio y no pueden quedar
accesibles sin autenticar.

`catalogo.py` tiene que copiar el `analisis.json` actualizado a
`web/api/_datos/analisis.js` como ya hace.

---

## Probar

```bash
python3 analisis.py data/stock.csv data/ventas.csv > output/analisis.json
python3 listas.py
ls -la output/listas/
```

- Los cuatro CSV existen.
- `liquidar` tiene **613 filas** más el encabezado; `devolver`, **1.658**;
  `reponer`, **39**.
- Abrir `liquidar` en Excel o Numbers: los acentos se ven bien, el EAN se ve
  completo como `9788466677929` y no como `9,78847E+12`, y la columna de precio
  de liquidación es el PVP menos el descuento configurado.
- El mail llega con los cuatro adjuntos.
- El panel muestra los botones de descarga y el CSV que bajan es idéntico al del
  mail.
