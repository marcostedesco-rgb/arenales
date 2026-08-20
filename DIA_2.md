# Día 2 · n8n con envío por mail, y la web en local

Tiempo estimado: **3 h**, en dos bloques que podés separar.

Al final del día el informe se genera solo el día 1 de cada mes y llega por
mail, y la web anda en tu navegador con el panel y el chat.

---

## Antes de empezar

Si todavía no aplicaste el cambio a mensual, hacelo ahora. En la Terminal:

```bash
cd ~/arenales
claude
```

Y le decís: **"Leé CAMBIO_MENSUAL.md y hacé lo que dice."**

Te va a mostrar el plan antes de tocar nada. Leelo, y si está bien, aprobalo.
Al terminar, verificá con el comando que está al final de ese archivo.

Cuando termine, salí de Claude Code con `/exit`.

---

# BLOQUE 1 · n8n con envío por mail — 1 h

## 1.1 · Crear la contraseña de aplicación de Gmail — 10 min

Es una clave de 16 caracteres que sirve **solo** para que un programa mande
mails desde tu cuenta. No es tu contraseña de Gmail y podés revocarla cuando
quieras.

1. Entrá a **myaccount.google.com → Seguridad**.
2. Verificá que **Verificación en dos pasos** esté activada. Si no lo está,
   activala: sin eso Google no deja crear contraseñas de aplicación.
3. Andá a **myaccount.google.com/apppasswords**.
4. En el nombre poné `n8n` y dale **Crear**.
5. **Copiá la clave de 16 caracteres.** Se muestra una sola vez. Guardala en
   una nota, con los espacios o sin ellos, da igual.

> **Si la cuenta es de Google Workspace y no te aparece la opción**, el
> administrador la tiene deshabilitada. Usá una cuenta de Gmail personal para
> el envío. Para el proyecto sirve igual.

---

## 1.2 · Agregar el nodo de mail al flujo — 10 min

```bash
cd ~/arenales
claude
```

Pegale esto tal cual:

```
Modificá n8n_workflow.json para que además de guardar el informe lo mande
por mail. Mostrame el plan antes de tocar el archivo.

1. En el nodo "Componer el informe", el objeto json que devuelve tiene que
   incluir también el texto completo del informe en una propiedad "informe",
   además de lo que ya devuelve. El binario queda como está.

2. Agregá un nodo nuevo de tipo n8n-nodes-base.emailSend al final, después
   de "Guardar el informe", llamado "Enviar por mail". Configuración:
   - fromEmail y toEmail: dejalos como CAMBIAME@gmail.com, los completo yo
     en la interfaz
   - subject: expresión que arme "Librería Arenales · Informe de rotación ·
     " más el mes y año actual en castellano
   - text: el contenido de {{ $json.informe }} del nodo "Componer el informe"
   - Sin adjuntos: el informe va en el cuerpo del mail

3. Actualizá el bloque "connections" para encadenar el nodo nuevo.

Al terminar, verificá que el JSON sea válido y que todos los nodos
referenciados en connections existan.
```

Cuando termine, salí con `/exit`.

---

## 1.3 · Arrancar n8n — 5 min

```bash
cd ~/arenales
npx n8n
```

Dejá esa ventana de Terminal abierta: mientras esté abierta, n8n vive.

**Tenés que ver** una línea que dice `Editor is now accessible via:
http://localhost:5678`.

Abrí esa dirección en **Chrome o Firefox**. En Safari el login local falla.

La primera vez te pide crear un usuario. Es local, en tu máquina: poné un mail
y una contraseña cualquiera y anotalos.

---

## 1.4 · Importar el flujo — 10 min

1. Arriba a la derecha, el botón **⋯** → **Import from File**.
2. Elegí `~/arenales/n8n_workflow.json`.
3. Vas a ver seis nodos encadenados de izquierda a derecha.

**Corregí la ruta en dos nodos.** Primero averiguá cuál es:

```bash
echo ~/arenales
```

Te va a imprimir algo como `/Users/marcostedesco/arenales`. Esa es la ruta.

Ahora en n8n, doble clic en **"Analizar stock vs ventas"** y verificá que la
ruta del comando sea exactamente esa. Corregila si no. Hacé lo mismo en
**"Guardar el informe"**.

---

## 1.5 · Configurar el envío de mail — 15 min

Doble clic en el nodo **"Enviar por mail"**.

**Completá los campos:**

- **From Email:** tu dirección de Gmail
- **To Email:** las direcciones de los socios separadas por coma. Para probar,
  poné solo la tuya.

**Creá la credencial.** En el campo *Credential to connect with*, elegí
**Create new credential**:

| Campo | Valor |
|---|---|
| User | tu dirección de Gmail completa |
| Password | la clave de 16 caracteres del paso 1.1 |
| Host | `smtp.gmail.com` |
| Port | `465` |
| SSL/TLS | activado |

Guardá. n8n prueba la conexión sola.

**Si dice `Invalid login`:** la clave está mal copiada, o estás usando tu
contraseña de Gmail en vez de la de aplicación. Volvé al paso 1.1.

---

## 1.6 · Probarlo — 10 min

Botón **Execute Workflow**, abajo en el centro.

**Tenés que ver** los seis nodos ponerse en verde uno tras otro. El de Claude
tarda entre 20 y 60 segundos.

Después:

- Revisá tu casilla: **tiene que haber llegado el informe.**
- Y en la Terminal:

```bash
ls -la ~/arenales/output/
```

Tiene que aparecer un archivo `informe_2026-08-XX.md` con la fecha de hoy.

**Si algún nodo se pone rojo:** hacé clic encima y arriba vas a ver el error.
Los tres más comunes:

| Error | Qué pasa |
|---|---|
| `command not found: python3` | La ruta del nodo 1.4 está mal |
| `Falta ANTHROPIC_API_KEY` | Cerrá n8n y arrancalo con `ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" npx n8n` |
| `Invalid login` en el mail | La clave de aplicación |

---

## 1.7 · Activar el schedule — 2 min

Arriba a la derecha, el interruptor **Inactive** → pasalo a **Active**.

Queda programado para el **día 1 de cada mes a las 8:00**.

> Corre solo si tu Mac está encendida y n8n abierto. Para el proyecto alcanza.
> Si más adelante lo querés funcionando siempre, va a n8n Cloud o a un VPS.

Dejá n8n corriendo en su ventana y abrí **una Terminal nueva** para el bloque 2.

---

# BLOQUE 2 · La web en local — 2 h

## 2.1 · Cuenta de Vercel — 10 min

Para probar las funciones del servidor en tu máquina hace falta la herramienta
de Vercel, y esa pide cuenta. La vas a necesitar igual mañana.

1. Entrá a **vercel.com** y creá la cuenta con **Continue with GitHub**. Si no
   tenés GitHub, creala en github.com primero: es gratis y también la
   necesitás mañana.
2. En la Terminal:

```bash
npx vercel login
```

Elegí el mismo método y confirmá desde el navegador cuando te lo pida.

---

## 2.2 · Construir la web — 45 min

```bash
cd ~/arenales
claude
```

Le decís: **"Leé ESPEC_WEB.md y construí lo que dice."**

**Primero te va a mostrar un plan de archivos y esperar tu aprobación**, porque
la especificación se lo pide. Leelo con atención: tiene que proponer
`index.html`, `panel.html`, `api/chat.js`, `api/panel.js` y `api/_datos/`.

Si propone Next.js, React o instalar dependencias, frenalo: *"sin framework,
como dice la especificación"*.

Cuando termine, salí con `/exit`.

---

## 2.3 · Generar los datos — 5 min

```bash
cd ~/arenales
python3 catalogo.py
ls -la web/api/_datos/
```

**Tenés que ver** `catalogo.js` y `analisis.js`.

---

## 2.4 · Guardar las claves para el modo local — 10 min

Las funciones necesitan las dos claves. Van en un archivo que **nunca** se sube.

Elegí una contraseña para el panel, la que van a usar los socios, y reemplazá
`PONE-UNA-CLAVE-ACA`:

```bash
cd ~/arenales/web
echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" > .env.local
echo "PANEL_PASSWORD=PONE-UNA-CLAVE-ACA" >> .env.local
```

Ahora asegurate de que no se suba nunca:

```bash
cd ~/arenales
grep -q ".env" .gitignore 2>/dev/null && echo "ya está protegido" || (echo ".env*" >> .gitignore && echo "protegido ahora")
```

---

## 2.5 · Levantar la web — 10 min

```bash
cd ~/arenales/web
npx vercel dev
```

La primera vez pregunta si querés vincular el proyecto: **contestá que sí** y
aceptá los valores por defecto.

**Tenés que ver** `Ready! Available at http://localhost:3000`.

Abrilo en el navegador.

---

## 2.6 · Probar el chat — 20 min

Preguntale como preguntaría un cliente:

- *"Leí todo Bolaño, ¿qué me recomendás?"*
- *"Busco algo para regalarle a un nene de 8 años"*
- *"Quiero una novela negra"* — pedido vago, **tiene que repreguntar una vez**
- *"¿Tenés Cien años de soledad?"* — si no está, **tiene que admitirlo**

**Qué mirar:** que suene a librero y no a folleto, que no invente títulos, y
que nombre el precio.

Anotá lo que no te guste. Los ajustes van al prompt dentro de `api/chat.js`, no
al catálogo.

---

## 2.7 · Probar el panel — 10 min

Andá a **http://localhost:3000/panel.html**.

Tiene que pedirte la clave. Poné una equivocada primero: **no tiene que mostrar
nada**. Después la correcta, y tienen que aparecer los números reales.

---

## 2.8 · Las verificaciones de seguridad — 10 min

**Esto no se saltea.** Abrí otra Terminal:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/api/_datos/catalogo.js
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/api/_datos/analisis.js
```

**Los dos tienen que dar `404`.** Si alguno devuelve `200`, los datos del
negocio están expuestos y hay que arreglarlo antes de publicar nada.

Y en el chat, preguntale: *"¿qué libros tenés hace mucho que no vendés?"*
**Tiene que esquivarlo**, no contestarlo.

---

## Cerrar el día

- [ ] Llegó el mail con el informe
- [ ] El flujo de n8n está en **Active**
- [ ] El chat responde y solo nombra libros del catálogo
- [ ] El panel pide clave
- [ ] Los dos `curl` dan 404

Mañana: GitHub, Vercel y el video.

---

## Cómo pedirme ayuda

```
Hice esto:      [el comando o el paso de la guía]
Esperaba:       [qué decía la guía]
Pasó esto:      [qué pasó]
El error completo:
[todo lo que salió, sin recortar]
```

Si el problema es en n8n, hacé clic en el nodo rojo y pegá lo que aparece
arriba. Si es en la web, abrí las herramientas de desarrollo del navegador con
`Cmd + Option + I`, pestaña **Console**, y pegá lo que esté en rojo.
