# Día 1 · El agente funcionando en tu Mac

Tiempo estimado: **1 h 30** si Geslib coopera. Todo se hace en la Terminal y el
navegador. No hace falta escribir código.

**Al final del día tenés un informe de rotación escrito por Claude con los datos
de tu librería.** Con eso solo ya hay proyecto entregable.

> Abrí la Terminal: `Cmd + Espacio`, escribí `terminal`, Enter.
> Cada bloque de código se copia y se pega entero, y se aprieta Enter.

---

## Paso 1 · Verificar Python — 5 min

```bash
python3 --version
```

**Tenés que ver:** `Python 3.9.x` o un número mayor.

**Si dice `command not found`:** macOS te abre una ventana ofreciendo instalar
las *herramientas de línea de comandos*. Dale **Instalar**, esperá a que
termine (tarda unos minutos) y volvé a correr el comando.

---

## Paso 2 · Dejar el proyecto en su lugar — 5 min

Descomprimí `arenales_agente.zip` haciéndole doble clic. Te crea una carpeta
`arenales`. Movela a tu carpeta personal, la que tiene tu nombre de usuario.

Después, movés a esa misma carpeta los tres archivos sueltos que te mandé:
`PLAN_3_DIAS.md`, `ESPEC_WEB.md` y este mismo, `DIA_1.md`.

Verificá:

```bash
cd ~/arenales && ls
```

**Tenés que ver, entre otros:** `analisis.py`, `parsers.py`, `informe.py`,
`catalogo.py` no todavía, `data`, `output`, `CLAUDE.md`.

**Si dice `no such file or directory`:** la carpeta quedó en otro lado. Buscala
en Finder, arrastrala sobre el ícono de la Terminal después de escribir `cd ` —
con el espacio — y eso pega la ruta correcta sola.

---

## Paso 3 · Crear la API key — 15 min

La suscripción Pro de Claude **no** sirve para esto. La API es una cuenta de
consumo aparte.

1. Entrá a **console.anthropic.com** y logueate con tu cuenta.
2. **Settings → API keys → Create Key.** Ponele de nombre `arenales`.
3. **Copiala completa ahora**, empieza con `sk-ant-`. No se vuelve a mostrar.
   Pegala en una nota mientras tanto.
4. Andá a **Billing → Add credits** y cargá **US$5**. Alcanza de sobra: cada
   informe cuesta centavos.

> **La key es como la llave de tu casa. No me la pegues acá ni en ningún chat,
> y no la escribas dentro de ningún archivo del proyecto.**

---

## Paso 4 · Guardar la key en tu Mac — 5 min

Reemplazá `sk-ant-TU-CLAVE-ACA` por la tuya, con las comillas:

```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-TU-CLAVE-ACA"' >> ~/.zshrc
source ~/.zshrc
```

Comprobá que quedó:

```bash
echo $ANTHROPIC_API_KEY
```

**Tenés que ver** tu clave impresa. Si sale vacío, repetí el primer comando
mirando bien que las comillas estén completas.

---

## Paso 5 · Exportar de Geslib — 30 min

**Es el único paso que puede trabarse, porque depende de un sistema que no
controlamos. Si se complica, saltá al Plan B y seguí. No pierdas el día acá.**

Necesitás dos informes:

**Informe de stock** — con estas columnas:
EAN o ISBN · Título · Autor · Editorial · Stk. Total · Stock eur · PVP

**Informe de ventas diarias** — con estas columnas:
Fecha · Artículo (el EAN) · Descripción · Cnt. · Importe

En cada uno buscá el botón de **exportar** y elegí **CSV** o **Excel**. En
ventas, poné el período más largo que te deje: cuanto más historial, mejor
detecta lo que no rota.

Guardalos en `~/arenales/data/` con estos nombres exactos:
**`stock.csv`** y **`ventas.csv`**.

Verificá que llegaron:

```bash
ls -la ~/arenales/data/
```

### Plan B — si Geslib solo exporta PDF

No pasa nada, el lector de PDF ya está hecho y probado. Guardalos como
`stock.pdf` y `ventas.pdf` y en los pasos siguientes cambiás `.csv` por `.pdf`
en los comandos. Perdés el título del 4,7% de los libros, nada más.

### Plan C — si hoy no sale nada de Geslib

Seguí con los archivos que ya están en `data/`. Son tus datos reales, los que me
pasaste, ya convertidos. **Seguí el día completo con esos** y actualizás cuando
consigas el export.

---

## Paso 6 · Correr el análisis — 2 min

```bash
cd ~/arenales
python3 analisis.py data/stock.csv data/ventas.csv > output/analisis.json
```

Puede tardar unos segundos. Es normal que aparezcan líneas que empiezan con
`[aviso]` — son informativas, no son errores.

Mirá el resultado:

```bash
python3 -c "import json;d=json.load(open('output/analisis.json'));[print(f'{k:32} {v}') for k,v in d['panorama'].items()]"
```

**Si usaste los archivos que ya venían** (Plan C), tenés que ver exactamente
esto:

```
titulos                          2676
unidades                         3745
valor_stock_eur                  63552.39
rotacion_meses                   29.9
pct_titulos_sin_venta            84.9
capital_inmovilizado_eur         52567.79
caja_recuperable_estimada_eur    34006.99
```

**Si exportaste de Geslib**, los números van a ser parecidos pero no idénticos,
porque el stock es de otra fecha. Lo que tiene que dar es del mismo orden: unos
2.500 a 3.000 títulos y entre €55.000 y €70.000.

**Si ves ceros, o `titulos: 0`:** el archivo se leyó pero no reconoció las
columnas. Andá al final de esta guía, a *Cómo pedirme ayuda*.

---

## Paso 7 · Generar el informe con Claude — 5 min

Antes de gastar un centavo, mirá el prompt exacto que se va a mandar:

```bash
python3 informe.py output/analisis.json --prompt | head -30
```

Ahora sí, el informe:

```bash
python3 informe.py output/analisis.json > output/informe.md
```

Tarda entre 20 y 60 segundos. **Este es el momento de la verdad del proyecto.**

Abrilo:

```bash
open -a TextEdit output/informe.md
```

**Leelo como librero, no como programador.** La pregunta de la Clase 2:
*¿esto le ahorra tiempo o le crea trabajo?* Si las acciones que propone las
podrías ejecutar el lunes, el agente funciona.

### Si da error

**`RuntimeError: Falta ANTHROPIC_API_KEY`** → volvé al paso 4.

**Error que menciona `model` o `not_found_error`** → el nombre del modelo
cambió. Abrí `informe.py`, buscá la línea que empieza con `MODELO =` cerca del
principio, y cambiá el nombre por uno de los que veas listados en
console.anthropic.com. Es una sola palabra.

**`credit balance is too low`** → volvé a Billing y cargá el crédito.

---

## Paso 8 · Ajustar los umbrales — 20 min

Abrí `analisis.py`:

```bash
open -a TextEdit analisis.py
```

Arriba de todo está el bloque `CONFIG`. Estos son los que te conviene revisar:

| Parámetro | Qué significa | Está en |
|---|---|---|
| `umbral_rotacion` | Ventas al año para considerar que un libro rota | 3 |
| `cobertura_critica` | Meses de stock por debajo de los cuales urge reponer | 1.5 |
| `descuento_liquidacion` | Descuento que asumimos en la mesa de saldos | 0.30 |
| `tasa_devolucion` | Porcentaje del PVP que reconoce el distribuidor | 0.60 |

**Los dos últimos son los que más te conviene ajustar**, porque determinan la
cifra de caja recuperable y hoy son supuestos míos. Si sabés qué te reconoce
Trevenque en una devolución, poné ese número.

Cambiás, guardás, y volvés a correr el paso 6. Es instantáneo y no cuesta nada:
solo el paso 7 consume API.

---

## Cerrar el día

```bash
cd ~/arenales && ls output/
```

**Tenés que ver `analisis.json` e `informe.md`.** Con esos dos archivos el
agente está funcionando y tenés proyecto.

Mañana: n8n para que corra solo, y la web.

---

## Cómo pedirme ayuda

Para que te resuelva en un mensaje y no en cuatro, mandame las cuatro cosas del
formato de la Clase 4:

```
Hice esto:      [el comando que corriste]
Esperaba:       [qué decía la guía que tenía que pasar]
Pasó esto:      [qué pasó en realidad]
El error completo:
[pegás TODO lo que salió en la terminal, sin recortar nada]
```

Lo que menos sirve es "no funciona": no veo tu pantalla y termino adivinando
tres veces. Pegá el error entero, incluidas las partes que parecen basura.

**Si el problema es que no reconoce las columnas del CSV**, además mandame la
primera línea del archivo, que es la de los encabezados:

```bash
head -1 data/stock.csv
head -1 data/ventas.csv
```

Eso no tiene datos de nadie, solo los nombres de las columnas, y con eso ajusto
el lector en dos minutos.
