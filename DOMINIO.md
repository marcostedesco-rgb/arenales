# Publicar en el dominio de la librería

Dos partes: primero el contenido que le falta a la página, después el DNS.

---

# PARTE A · Contenido de la página

Para Claude Code, en `~/arenales`. **Mostrame el plan antes de tocar archivos.**

Al quedar en el dominio principal, `index.html` deja de ser solo el chat y pasa
a ser el sitio de la librería. Alguien que llega desde Google Maps espera saber
dónde está y cuándo abre.

Agregar a `index.html`, manteniendo la estética y la paleta que ya tiene:

**Encabezado** — nombre de la librería y una línea de identidad:
*Librería independiente en Chamberí, especializada en literatura
hispanoamericana.*

**El chat como protagonista**, justo debajo. Es lo que la diferencia de
cualquier otra web de librería: sigue siendo el centro de la página, no un
añadido al pie.

**Bloque de información práctica**, después del chat:

- Dirección y una línea de *cómo llegar*
- Horarios, marcando los días que cierra
- Teléfono y correo
- Enlaces a Instagram y a la ficha de Google Maps
- Mención de lo que ya existe: club de lectura y cuentacuentos de los sábados

Dejar esos datos en **constantes al principio del archivo**, agrupadas y
comentadas, para poder cambiarlas sin buscar entre el HTML.

**Nada de enlaces al panel.** Sigue siendo privado y quien lo necesita conoce la
dirección.

**Etiquetas para compartir:** agregar `<title>`, `description`, y las etiquetas
Open Graph (`og:title`, `og:description`, `og:url`). Son las que hacen que,
cuando pegues el link en WhatsApp o Instagram, aparezca con nombre y descripción
en lugar de una URL pelada.

---

# PARTE B · El DNS

**Regla que no se rompe: no se tocan los nameservers.**

El correo de la librería funciona con registros **MX** apuntando a Google.
Nosotros vamos a agregar registros **A** y **CNAME**, que son de otro tipo y no
se pisan entre sí. El correo sigue igual.

Si en algún momento Vercel te ofrece *cambiar los nameservers a Vercel*,
**decliná**. Esa es la única vía por la que se rompería el correo.

---

## B.1 · Averiguar quién administra el DNS — 5 min

```bash
dig +short NS TUDOMINIO.com
```

Lo que devuelve te dice dónde entrar:

| Si aparece | Entrás en |
|---|---|
| `squarespacedns.com` | Squarespace Domains — los dominios de Google pasaron ahí en 2023 |
| `googledomains.com` | Squarespace igual, con la cuenta de Google |
| `domaincontrol.com` | GoDaddy |
| `registrar-servers.com` | Namecheap |
| `cloudflare.com` | Cloudflare |

Si no reconocés ninguno, entrá a **admin.google.com → Dominios** y ahí figura el
registrador.

---

## B.2 · Agregar el dominio en Vercel — 10 min

1. **vercel.com/dashboard** → proyecto `arenales` → **Settings → Domains**.
2. Escribí tu dominio sin `www` y dale **Add**.
3. Cuando pregunte cómo configurarlo, elegí la opción de **agregar registros
   DNS**, no la de cambiar nameservers.
4. Repetí con `www.tudominio.com`.

Vercel te muestra los registros exactos que hay que crear. Suelen ser:

| Tipo | Nombre | Valor |
|---|---|---|
| A | `@` | `76.76.21.21` |
| CNAME | `www` | `cname.vercel-dns.com` |

**Usá los valores que te muestre Vercel, no estos.** Los pongo para que
reconozcas la forma.

---

## B.3 · Crear los registros — 20 min

Entrá al panel del registrador que encontraste en B.1, a la zona DNS de tu
dominio.

**Antes de agregar nada, sacá una foto o copiá la lista completa de registros
que hay hoy.** Si algo sale mal, poder volver atrás vale oro.

Agregá los dos registros que te dio Vercel.

**Lo que NO se toca:**

- Los registros **MX** — son el correo.
- Los **TXT** que empiezan con `v=spf1`, los de `_dmarc` y los de
  `google._domainkey` — son la autenticación del correo. Si los borrás, tus
  mails empiezan a caer en spam.
- Cualquier **TXT** de verificación de Google.

Si ya existe un registro **A** para `@`, reemplazalo por el de Vercel. Como el
dominio hoy solo tiene correo, lo más probable es que no haya ninguno.

---

## B.4 · Esperar y verificar — de 10 min a unas horas

En Vercel, la pantalla de Domains pasa de **Invalid Configuration** a
**Valid Configuration** sola. Podés apretar **Refresh**.

Desde la terminal:

```bash
dig +short TUDOMINIO.com
dig +short www.TUDOMINIO.com
```

Tienen que devolver la IP y el destino de Vercel.

Y comprobá que el correo sigue en pie:

```bash
dig +short MX TUDOMINIO.com
```

**Tienen que seguir apareciendo los servidores de Google.** Si están, el correo
no se tocó.

El certificado HTTPS lo emite Vercel solo, unos minutos después de que el DNS
resuelva. No hay que hacer nada.

---

## B.5 · Últimos ajustes — 15 min

- En Vercel, **Settings → Domains**, marcá el dominio sin `www` como
  **Primary** y dejá que `www` redirija hacia él. O al revés, pero elegí uno:
  que la misma página responda en dos direcciones distintas confunde a Google.
- Repetí las verificaciones de seguridad contra la dirección nueva:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://TUDOMINIO.com/api/_datos/catalogo.js
curl -s -o /dev/null -w "%{http_code}\n" https://TUDOMINIO.com/api/_datos/analisis.js
```

Los dos tienen que dar **404**.

- Actualizá el enlace en **Google Maps** y en **Instagram**, y regenerá el QR
  con la dirección nueva.
- Mandate un correo a vos mismo desde la cuenta de la librería para confirmar
  que sigue funcionando.

---

## Si algo sale mal

El correo no debería verse afectado, pero si dejara de llegar: volvé al panel de
DNS, compará con la foto que sacaste en B.3 y restaurá los MX. La propagación
tarda lo mismo para volver que para ir.

Y avisame con la lista de registros como quedó.
