# Contexto del proyecto — Agente de rotación, Librería Arenales

Leé esto antes de tocar nada.

## Qué es

Un agente mensual que cruza el inventario de una librería contra su histórico
de ventas y dice qué liquidar, qué devolver, qué reponer y qué poner en el
mostrador.

Es el proyecto final del curso **CoderCup IA de Coderhouse**. Se entrega el
**domingo 23 de agosto de 2026**. El criterio del jurado es explícito: *"No gana
el proyecto más técnico. Gana el que mejor resuelve un problema real."*

Entregables: el proyecto andando (link, acceso o demo) y un video de **máximo 2
minutos** explicando qué problema resuelve, cómo se hizo y cómo se usa.

## El problema real

Librería Arenales, Chamberí (Madrid). Negocio familiar del usuario.

- Factura **€2.123/mes** y cuesta **~€6.000/mes** sostenerla
- Los socios llevan **€60.076** aportados para cubrir el hueco
- **€63.552** en estanterías, de los cuales **€52.568 (83%)** no vendió nada en
  13 meses
- Rotación: **29,9 meses**. El estándar del sector son 6.

El hallazgo que ordena todo: **los dos errores conviven**. Hay capital muerto en
lo que no rota y rotura de stock en lo que sí rota. De los diez títulos más
vendidos del año, cinco tienen cero o un solo ejemplar.

Existe un plan de reactivación previo con tres ejes. Este agente ataca el
**Eje 01 (liberar caja del stock)**, cuya meta era €8.000–12.000. La medición
real da **€34.007** de caja recuperable.

## La decisión de arquitectura que no hay que romper

```
CSV de Geslib ──► analisis.py ──► segmentos ──► Claude ──► informe .md
   stock+ventas    (aritmética)     (JSON)     (criterio)    (acciones)
```

**La IA no cuenta.** Los 2.676 títulos los cruza Python: mismo resultado
siempre, auditable. Claude recibe los segmentos ya calculados y hace lo que un
modelo hace bien — priorizar, ver patrones, explicar qué tiene que hacer este mes.

Pedirle a un LLM que sume 2.676 filas da un informe que suena bien y está mal.
Esto es también el argumento fuerte del video: **separar el cálculo de la
decisión.** Si alguna propuesta mueve aritmética hacia el prompt, es un
retroceso.

## Archivos

| Archivo | Qué hace |
|---|---|
| `parsers.py` | Lee los exports de Geslib. CSV o PDF. |
| `analisis.py` | Cruza stock y ventas, clasifica en segmentos. `CONFIG` arriba. |
| `informe.py` | Arma el prompt y llama a la API de Anthropic. |
| `n8n_workflow.json` | El flujo mensual, listo para importar. |
| `deck/generar.js` | Genera el anexo en PPTX para los socios (pptxgenjs). |
| `output/informe_semanal.md` | Ejemplo de salida con datos reales. |

## Cosas que ya se resolvieron — no volver sobre ellas

**El PDF de stock viene partido en cuatro bloques de columnas.** Geslib exporta
a Google Sheets y de ahí a PDF A4 vertical, lo que parte la planilla:
Título / Autor-Editorial-PVP / EAN-Stock / Nuevo stock. Cada bloque son 63
páginas consecutivas. `leer_stock_pdf()` los recompone cruzando página por
página.

**El cruce está verificado, no asumido.** El título reconstruido se validó
contra los títulos del informe de ventas (fuente independiente): 355 de 355.
La editorial se alinea usando el PVP como ancla, porque aparece en los dos
bloques: 2.746 de 2.746 con PVP coincidente. Si tocás los parsers, volvé a
correr esas verificaciones.

**El libro usado queda fuera.** Se cataloga con la editorial `LAURA TEDESCO`
(104 títulos, €713,69). No se devuelve al distribuidor ni se repone, así que
ensucia la rotación y las decisiones de compra. Está en
`CONFIG["editoriales_excluidas"]`.

**El CSV es el camino bueno.** El lector de PDF existe porque hoy es lo único
que hay, pero deja un 4,7% de filas sin título. Ambos caminos dan resultados
idénticos en las 15 métricas del panorama.

## Qué falta

1. **Export automático desde Geslib.** Hoy es manual. El usuario iba a ver en
   estos días si se puede conectar desde su Mac al software o dejar los CSV en
   una carpeta vigilada. Es el punto abierto más importante.
2. **Distinguir depósito de compra firme.** Cambia si un título se devuelve o se
   liquida. El dato existe en Geslib pero no está en el export actual.
3. **Márgenes por editorial**, para priorizar por beneficio y no por PVP.
4. **Envío del informe** por email o WhatsApp.
5. **Grabar el video de 2 minutos.**

## Entorno del usuario

- MacBook Air. Node recién instalado desde nodejs.org.
- n8n corre con `npx n8n` en `http://localhost:5678`.
  **Abrirlo en Chrome o Firefox, no en Safari** — el login local falla por
  cookies seguras.
- La API key va como variable de entorno al arrancar n8n:
  `ANTHROPIC_API_KEY="sk-ant-..." npx n8n`

## Cómo hablarle al usuario

Castellano rioplatense, directo. Es analítico y revisa los números: ya detectó
dos cosas mal en material entregado. Si un dato no está verificado, decilo en
vez de suavizarlo.
