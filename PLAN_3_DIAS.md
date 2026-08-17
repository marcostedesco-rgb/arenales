# Plan de ejecución — 3 días

Proyecto final CoderCup IA · Librería Arenales · Entrega: domingo 23/8

---

## La arquitectura, en un dibujo

```
GESLIB
  │  exportás 2 CSV (stock y ventas)
  ▼
CARPETA data/  en tu Mac
  │
  ▼
n8n (local, lunes 8:00)
  │  1. corre analisis.py  → cruza stock vs ventas, 6 segmentos
  │  2. llama a Claude     → redacta el informe de acciones
  │  3. guarda los archivos en output/
  ▼
GIT COMMIT + PUSH
  │
  ▼
VERCEL  publica solo
  │
  ├──► PANEL WEB   lee el JSON y muestra el informe
  └──► CHAT        endpoint con la API key, responde sobre el catálogo real
```

**Por qué así:** el análisis pesado corre una vez por semana en tu máquina, donde
ya está probado. La web solo muestra. El único servicio que corre en internet es
el chat, que es una función chica. Menos piezas, menos cosas que se rompen.

---

# DÍA 1 · El agente funcionando en tu Mac

**Objetivo del día:** corrés un comando y sale un informe escrito por Claude con
los datos reales de la librería.

### 1.1 · Verificar Python — *Terminal* — 5 min

```bash
python3 --version
```

Si dice `command not found`, macOS te va a ofrecer instalar las Command Line
Tools. Aceptá y esperá. Necesitás 3.9 o superior.

### 1.2 · Dejar el proyecto en su lugar — *Finder / Terminal* — 5 min

Descomprimí `arenales_agente.zip` en tu carpeta personal, de modo que quede
`~/arenales`. Esa ruta la vamos a usar en todos lados.

```bash
cd ~/arenales && ls
```

Tenés que ver `analisis.py`, `parsers.py`, `informe.py`, `data/`, `output/`.

### 1.3 · Conseguir la API key — *console.anthropic.com* — 10 min

1. Entrá a **console.anthropic.com** con tu cuenta.
2. **Settings → API keys → Create Key**. Copiala completa; no se vuelve a mostrar.
3. **Billing → Add credits.** Con US$5 te sobra: cada informe semanal cuesta
   centavos y el chat, según uso, unos pocos dólares al mes.

> Ojo: la suscripción Pro de Claude **no** incluye acceso a la API. Son cuentas
> de consumo separadas.

Guardala en la terminal:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Para que quede fija en todas las terminales:

```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
source ~/.zshrc
```

### 1.4 · Exportar los archivos de Geslib — *Geslib* — 30 min

**Este es el paso que puede fallar. Reservale tiempo.**

Necesitás dos informes:

| Informe | Columnas que tienen que venir |
|---|---|
| **Stock** | EAN/ISBN · Título · Autor · Editorial · Stk. Total · Stock eur · PVP |
| **Ventas diarias** | Fecha · Artículo (EAN) · Descripción · Cnt. · Importe |

En cada informe buscá el botón de **exportar** y elegí **CSV** o **Excel**.
Guardalos en `~/arenales/data/` como `stock.csv` y `ventas.csv`.

Para ventas, poné el período más largo que te deje: cuanto más historial, mejor
detecta lo que no rota.

**Si Geslib solo exporta PDF:** no pasa nada. El lector de PDF ya está hecho y
probado. Guardalos como `stock.pdf` y `ventas.pdf` y usá esos nombres en los
comandos. Perdés el 4,7% de los títulos, nada más.

**Si hoy no podés sacar nada:** seguí con los CSV que ya están en `data/`. Son
los datos reales convertidos desde los PDF que me pasaste. No frenes el día por
esto.

### 1.5 · Correr el análisis — *Terminal* — 2 min

```bash
cd ~/arenales
python3 analisis.py data/stock.csv data/ventas.csv > output/analisis.json
```

Abrí `output/analisis.json` y mirá el bloque `panorama`. Si los números se
parecen a los que ya vimos (~2.676 títulos, ~€63.500, rotación ~30 meses), el
archivo se leyó bien.

### 1.6 · Generar el informe con Claude — *Terminal* — 3 min

```bash
python3 informe.py output/analisis.json > output/informe.md
```

Abrilo. **Este es el momento de la verdad del proyecto:** si el informe te
resulta útil y accionable, el agente funciona.

Antes de gastar tokens podés ver el prompt exacto que se le manda:

```bash
python3 informe.py output/analisis.json --prompt
```

### 1.7 · Ajustar los umbrales — *cualquier editor* — 20 min

Abrí `analisis.py` y mirá el bloque `CONFIG` al principio. Ahí están
`umbral_muerto`, `umbral_rotacion`, `cobertura_critica`,
`descuento_liquidacion` y `tasa_devolucion`.

Cambiá lo que no te cierre según tu criterio de librero y volvé a correr. Es
instantáneo y no cuesta nada.

**Al terminar el día 1 tenés:** el agente andando con datos reales y un informe
que podés mostrar. Con esto solo, ya tenés proyecto entregable.

---

# DÍA 2 · n8n y la web en local

**Objetivo del día:** el flujo semanal automatizado y la página andando en tu
navegador.

### 2.1 · Arrancar n8n con la key — *Terminal* — 5 min

```bash
cd ~/arenales
ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" npx n8n
```

Abrí **http://localhost:5678** en **Chrome o Firefox**. En Safari falla el login
por las cookies seguras.

### 2.2 · Importar el flujo — *n8n* — 10 min

1. **Workflows → Import from File** → elegí `n8n_workflow.json`.
2. Abrí el nodo **"Analizar stock vs ventas"** y verificá que la ruta diga
   `/Users/<tu-usuario>/arenales`. Corregila si tu usuario es otro.
3. Hacé lo mismo en el nodo **"Guardar el informe"**.

> El flujo trae la ruta escrita directamente, sin variables de n8n. Las
> Variables son una función de los planes pagos y no queremos depender de eso.

### 2.3 · Probarlo — *n8n* — 10 min

Apretá **Execute Workflow**. Mirá que los cinco nodos se pongan en verde y que
aparezca un archivo nuevo en `output/`.

Si algo falla, **Executions** te muestra en qué nodo se rompió y con qué error.

### 2.4 · Activar el schedule — *n8n* — 2 min

Poné el interruptor **Active** arriba a la derecha. Queda programado para los
lunes a las 8:00.

Tené presente: corre solo si tu Mac está prendida y n8n abierto. Para el
proyecto alcanza. Si más adelante lo querés 24/7, va a un VPS o a n8n Cloud.

### 2.5 · Levantar la web — *Terminal* — 20 min

Yo te entrego la carpeta `web/` con el panel y el chat ya armados.

```bash
cd ~/arenales/web
npm install
npm run dev
```

Abrí **http://localhost:3000**. Vas a ver el panel con los datos de tu
`analisis.json`.

### 2.6 · Probar el chat — *navegador* — 30 min

Preguntale cosas reales, como preguntaría un cliente:

- "Leí todo Bolaño, ¿qué me recomendás?"
- "Busco algo para regalarle a un nene de 8 años"
- "¿Tenés poesía latinoamericana?"

**Qué mirar:** que solo recomiende libros que están en el stock, que diga
honestamente cuando no tiene algo, y que suene a librero y no a folleto.

Lo que no te guste, me lo pasás y ajusto el prompt.

**Al terminar el día 2 tenés:** el flujo automatizado y la web andando en local.

---

# DÍA 3 · Publicar y grabar

**Objetivo del día:** una dirección que abre cualquiera, y el video grabado.

### 3.1 · Subir a GitHub — *GitHub Desktop o Terminal* — 30 min

Creá el repositorio en github.com. **Ponelo privado.**

> **Por qué privado:** el repositorio incluye el historial de ventas y el
> inventario valorizado de un negocio familiar. En la clase el ejemplo era
> público porque era una app de juguete. Vercel publica igual desde un
> repositorio privado en el plan gratuito.

Con GitHub Desktop es más simple: **Add Local Repository** → elegí `~/arenales`
→ **Publish repository** → tildá *Keep this code private*.

Por terminal:

```bash
cd ~/arenales
git init
git add .
git commit -m "primer commit: agente de rotación de Librería Arenales"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/arenales.git
git push -u origin main
```

**Antes de subir, verificá que la API key no esté en ningún archivo:**

```bash
grep -r "sk-ant" . --exclude-dir=node_modules --exclude-dir=.git
```

Si eso devuelve algo, sacalo antes de hacer el commit.

### 3.2 · Publicar en Vercel — *vercel.com* — 30 min

1. Entrá a **vercel.com** y creá cuenta con GitHub.
2. **Add New → Project → Import Git Repository** → elegí `arenales`.
3. En **Root Directory** poné `web`.
4. En **Environment Variables** agregá:
   `ANTHROPIC_API_KEY` = tu clave.
5. **Deploy.**

A los dos minutos tenés una dirección tipo `arenales.vercel.app`, con HTTPS
puesto por Vercel.

### 3.3 · Probar desde el celular — 15 min

Abrí la dirección en el teléfono, con datos móviles y no por WiFi, para
comprobar que sale de verdad a internet. Usá el chat desde ahí.

### 3.4 · Probar el circuito completo — 15 min

Cambiá algo chico en el informe, hacé commit y push, y mirá cómo Vercel publica
solo. **Este momento es el que conviene grabar para el video:** es el circuito
de la Clase 5 funcionando de punta a punta.

### 3.5 · El dominio *(opcional)* — 30 min

Si querés `libreriaarenales.com` o similar: se compra en Namecheap o Cloudflare,
se pega en Vercel en la pantalla de dominios del proyecto, y copiás los dos o
tres datos que Vercel te indique en el registrador. Tarda de minutos a horas en
propagarse.

No es necesario para entregar. La dirección de Vercel sirve igual.

### 3.6 · Grabar el video — *QuickTime + celular* — 2 h

Máximo 2 minutos. Estructura sugerida:

| Tiempo | Qué |
|---|---|
| 0:00–0:25 | El problema, con números reales de la librería |
| 0:25–0:50 | El informe semanal: qué liquidar, devolver y reponer |
| 0:50–1:20 | El chat, usado desde el celular como lo usaría un cliente |
| 1:20–1:40 | Cómo está hecho: Python cuenta, Claude decide, n8n orquesta, Vercel publica |
| 1:40–2:00 | El impacto: €34.007 de caja recuperable contra €8–12.000 estimados |

Grabá la pantalla con QuickTime (**Archivo → Nueva grabación de pantalla**) y el
celular con otro teléfono o con el modo espejo.

### 3.7 · Entregar — 10 min

Formulario oficial con el link de Vercel y el del video. Opcional: publicarlo
con **#CoderCup** y mención a **@coderhouse**.

---

## Qué puede fallar y qué hacemos

| Riesgo | Plan B |
|---|---|
| Geslib no exporta CSV | Usar los PDF; el lector ya está hecho y probado |
| No sale ningún export de Geslib | Usar los CSV que ya están en `data/` |
| n8n se complica | Correr los dos comandos de Python a mano. El agente funciona igual |
| El chat responde cualquier cosa | Ajustamos el prompt; el catálogo no se toca |
| Vercel no compila | Se publica igual la versión anterior. Vercel avisa qué se rompió |
| Se acaba el tiempo | Con el día 1 hecho ya hay proyecto entregable |

---

## Reparto de tareas

**Yo:** la carpeta `web/` completa (panel y chat), el catálogo consultable, el
prompt del librero, el endpoint con sus límites de uso, y el flujo de n8n
corregido.

**Vos:** el export de Geslib, la API key, correr y probar, GitHub, Vercel y el
video.

**Claude Code en tu Mac:** para cuando algo falle y haya que ver por qué.

---

## Antes de arrancar, tené a mano

- [ ] Acceso a Geslib con permiso de exportar
- [ ] Cuenta en console.anthropic.com con US$5 de crédito
- [ ] Cuenta de GitHub
- [ ] Cuenta de Vercel *(se crea con la de GitHub)*
- [ ] Chrome o Firefox instalado *(n8n no anda en Safari)*
