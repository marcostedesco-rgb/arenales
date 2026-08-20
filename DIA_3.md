# Día 3 · Publicar y grabar

Actualizado con lo que ya está hecho.

**Ya tenés:** la web andando en local con tu diseño, el contenido de la página
completo, y el dominio configurado en Vercel con los registros DNS creados.

**Falta:** cargar las claves, subir a GitHub, publicar, verificar y grabar.

Tiempo estimado: **3 h 30**. Dos bloques que podés separar.

---

# BLOQUE 1 · Publicar — 1 h 15

## 1.1 · Cargar las claves en Vercel — 10 min

**Va primero.** Si publicás sin esto, el chat y el panel salen al aire sin poder
funcionar.

**vercel.com/dashboard** → proyecto `arenales` → **Settings → Environment
Variables**. Agregá las dos, marcando los tres entornos (Production, Preview,
Development):

| Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | tu clave `sk-ant-...` |
| `PANEL_PASSWORD` | la clave del panel |

Si no te acordás de alguna:

```bash
cat ~/arenales/web/.env.local
```

## 1.2 · Verificar el Root Directory — 2 min

En **Settings → General → Root Directory** tiene que decir **`web`**.

Es la carpeta que se publica. El resto del repositorio —los datos, los
informes, las guías— queda fuera del servidor.

---

## 1.3 · Proteger lo que no se sube — 10 min

**Antes de crear el repositorio.** Si una clave entra al historial de git,
sacarla después no es editar un archivo: hay que reescribir el historial.

```bash
cd ~/arenales
cat > .gitignore << 'EOF'
.env
.env.*
.vercel
node_modules/
__pycache__/
*.pyc
.DS_Store
EOF
```

Verificá que no quede ninguna clave suelta:

```bash
grep -rn "sk-ant" . --exclude-dir=.git --exclude-dir=node_modules --exclude=.env.local
```

**No tiene que devolver nada.** Si aparece algo, sacalo antes de seguir.

---

## 1.4 · Crear el repositorio y subir — 25 min

En **github.com** → botón **+** arriba a la derecha → **New repository**:

- **Repository name:** `arenales`
- **Visibility:** **Private** ← no es opcional
- **No** tildes ninguna casilla de abajo (README, .gitignore, licencia)
- **Create repository**

> **Por qué privado:** el repositorio lleva el historial de ventas y el
> inventario valorizado de un negocio familiar. Vercel publica igual desde un
> repositorio privado con el plan gratuito.

Subilo, reemplazando `TU-USUARIO`:

```bash
cd ~/arenales
git init
git add .
git commit -m "Agente de rotación y chat librero de Librería Arenales"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/arenales.git
git push -u origin main
```

Si pide autenticación, GitHub ya no acepta la contraseña normal: te abre el
navegador para autorizar.

**Comprobá en github.com** que estén tus archivos y que **no** aparezcan
`.env.local` ni la carpeta `.vercel`.

---

## 1.5 · Conectar Vercel al repositorio — 10 min

En **Settings → Git → Connect Git Repository** → elegí `arenales`.

En cuanto se conecte, Vercel publica solo. Andá a **Deployments** y miralo
construir.

Al terminar, el aviso de *"no deployment"* del dominio desaparece y la dirección
queda activa. El certificado HTTPS lo emite Vercel solo, unos minutos después.

> **Si no encontrás la opción de Git:** en el dashboard, **Add New → Project →
> Import Git Repository → arenales**, con **Root Directory = `web`**. Te crea un
> proyecto nuevo; hay que volver a cargar las variables del paso 1.1 y mover el
> dominio, y después borrás el proyecto viejo.

---

## 1.6 · Verificar en producción — 15 min

**Esto no se saltea.** Reemplazá `TUDOMINIO.com`:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://TUDOMINIO.com/api/_datos/catalogo.js
curl -s -o /dev/null -w "%{http_code}\n" https://TUDOMINIO.com/api/_datos/analisis.js
```

**Los dos tienen que dar `404`.** Si alguno da `200`, cualquiera en internet
puede bajarse el inventario y las ventas. Frená y avisame.

Y comprobá que el correo sigue en pie:

```bash
dig +short MX TUDOMINIO.com
```

**Tienen que aparecer los servidores de Google.**

Después, en el navegador:

- El chat responde y solo nombra libros del catálogo.
- Preguntale *"¿qué libros tenés hace mucho que no vendés?"*: tiene que
  esquivarlo.
- `/panel.html` con clave equivocada no muestra nada; con la correcta muestra
  **2.676 títulos** y **€63.552**.
- Los botones de descarga bajan los CSV completos.

---

## 1.7 · Probar desde el celular — 10 min

Abrí el dominio en el teléfono **con datos móviles, no con el WiFi de casa**.
Así confirmás que sale de verdad a internet.

- El chat se usa cómodo con una mano y el teclado no tapa el campo de escritura.
- El panel se lee sin zoom.
- Un CSV descargado desde el teléfono se abre bien.

Mandate un correo desde la cuenta de la librería para confirmar que el correo
sigue funcionando.

---

## 1.8 · Probar el circuito completo — 10 min

Cambiá algo mínimo, por ejemplo un texto de `index.html`:

```bash
cd ~/arenales
git add .
git commit -m "ajuste de texto"
git push
```

Mirá en **Deployments** cómo se publica solo.

**Grabá la pantalla mientras hacés esto.** Es el circuito de la Clase 5
funcionando de punta a punta y sirve para el video.

---

## 1.9 · Que la gente llegue al chat — 20 min

Ahora que tenés el dominio propio, esto rinde el doble. Es gratis:

- **Google Maps:** en el perfil del negocio, campo de sitio web. Son 50 reseñas
  de cinco estrellas trayendo gente: que tengan a dónde ir.
- **Instagram:** el link en la biografía, con una frase corta:
  *"¿No sabés qué leer? Preguntale a nuestro librero, a cualquier hora."*
- **Un QR impreso** en el mostrador y en la vidriera. Se genera gratis en
  cualquier web de códigos QR. El de la vidriera es el que más rinde: cubre las
  quince horas semanales y los dos días que el local está cerrado.
- **WhatsApp:** mandalo al club de lectura.

---

# BLOQUE 2 · El video — 2 h 15

Máximo **2 minutos**. Se juzga *qué problema resuelve, cómo lo hiciste y cómo
se usa*.

## 2.1 · Grabar — 40 min

**Pantalla del Mac:** QuickTime → **Archivo → Nueva grabación de pantalla**.

**Pantalla del iPhone, sin filmarlo con otro teléfono:** conectá el iPhone al
Mac con cable, QuickTime → **Archivo → Nueva grabación de vídeo**, y en la
flecha junto al botón de grabar elegí tu iPhone como fuente. Graba la pantalla
limpia y en alta calidad. Es lo que más diferencia un video casero de uno bien
hecho.

**Tomas separadas:**

1. El mail del informe, bajando despacio por las secciones.
2. El panel: los KPI y una descarga de CSV.
3. El chat en el teléfono, con una consulta real de punta a punta.
4. El circuito de git a Vercel del paso 1.8.
5. La librería: fachada, estanterías, mesa de novedades. **Diez segundos de esto
   valen más que cualquier gráfico.**

## 2.2 · El guion — 30 min

Los números sacalos de **tu informe actual**.

**0:00 – 0:20 · El problema**

> Mi familia tiene una librería en Chamberí, Madrid. Tiene cinco estrellas en
> Google, club de lectura y clientes fieles. Y pierde plata todos los meses.
> Hay sesenta y tres mil euros en las estanterías, y el ochenta y cinco por
> ciento de los libros no vendió ni un ejemplar en trece meses.

*Sobre imágenes de la librería.*

**0:20 – 0:45 · El primer agente**

> Construí un agente que cruza el inventario contra las ventas y, una vez por
> mes, manda esto: qué liquidar, qué devolver al distribuidor, qué reponer
> urgente. Y adjunta las listas completas con el código de barras, para que
> quien atiende las imprima y las ejecute.

*Sobre el mail y el panel.*

**0:45 – 1:15 · El segundo agente**

> El mismo análisis alimenta un segundo agente: un librero que atiende en la
> web. Solo recomienda libros que están hoy en la estantería, y cuando dos
> encajan parecido, empuja el que lleva meses sin venderse. Atiende los
> domingos y a las tres de la mañana, que es cuando la librería está cerrada.

*Sobre el chat en el teléfono.*

**1:15 – 1:35 · Cómo está hecho**

> Acá hay una decisión que quiero contar: **la IA no cuenta, decide.** Los dos
> mil seiscientos títulos los cruza un programa, que da siempre el mismo
> resultado y se puede auditar. Claude recibe los números ya calculados y hace
> lo que un modelo hace bien: priorizar y explicar qué hacer el lunes. Pedirle
> que sume dos mil filas da un informe que suena bien y está mal.

**1:35 – 2:00 · El impacto**

> El plan de reactivación estimaba entre ocho y doce mil euros de caja
> recuperable. Medido de verdad, son más de treinta mil. Eso es la diferencia
> entre cerrar y no cerrar. Y el mes que viene el informe llega solo.

*Cierre sobre la fachada, con el dominio en pantalla.*

## 2.3 · Montar — 45 min

**iMovie** viene en todos los Mac. Arrastrás los clips, grabás la voz encima y
exportás en 1080p.

- **Cronometralo.** Dos minutos es el máximo y lo controlan.
- **Sin música**, o muy baja. La voz tiene que entenderse.
- **Sin intro ni títulos animados.** El problema arranca en el segundo cero.
- Si un plano se hace largo, cortalo. Mejor que sobre tiempo.

## 2.4 · Entregar — 20 min

1. Subí el video a **YouTube como no listado**, o a Drive con enlace público.
   Comprobá desde una ventana de incógnito que abre sin pedir permisos.
2. Completá el **formulario oficial** con el link del dominio y el del video.
3. Opcional, suma: publicarlo con **#CoderCup** y mención a **@coderhouse**.

---

## Cerrar

- [ ] Las dos variables cargadas en Vercel
- [ ] Repositorio privado, sin claves
- [ ] El dominio abre desde el celular con datos móviles
- [ ] Los dos `curl` dan 404 en producción
- [ ] Los MX de Google siguen ahí y el correo funciona
- [ ] El panel pide clave; el chat no filtra datos del negocio
- [ ] El link está en Google Maps y en Instagram
- [ ] El video dura menos de 2 minutos
- [ ] Formulario entregado

---

## Cómo pedirme ayuda

```
Hice esto:      [el paso de la guía]
Esperaba:       [qué decía]
Pasó esto:      [qué pasó]
El error completo:
[todo, sin recortar]
```

Si falla el despliegue, en Vercel entrá al deployment rojo, **Building** o
**View Function Logs**, y pegá lo que salga.

Para el guion, si querés que lo ajuste a cómo hablás vos, mandámelo como lo
dirías en voz alta y lo pulo.
