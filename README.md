# Agente de rotación — Librería Arenales

Analiza cada mes el stock contra el histórico de ventas y produce un
informe con qué liquidar, qué devolver, qué reponer y qué poner en el
mostrador.

## El problema

Librería Arenales (Chamberí, Madrid) tiene **€64.266 en estanterías** y factura
**€2.129 al mes**. Eso son **30 meses de rotación** cuando el estándar del
sector son 6. El **85% de los títulos no vendió ni una sola vez** en 13 meses:
**€53.221 de capital inmovilizado**.

Al mismo tiempo, 39 títulos que sí venden están agotados o casi. Los dos
errores conviven: dinero parado en lo que no rota y rotura de stock en lo que
rota.

## Cómo está construido

```
CSV de Geslib ──► analisis.py ──► segmentos ──► Claude ──► informe .md
   stock+ventas    (aritmética)     (JSON)     (criterio)    (acciones)
```

**La decisión de diseño que sostiene todo:** la IA no cuenta. Los 2.780
títulos los cruza Python, que siempre da el mismo resultado y se puede
auditar. Claude recibe los segmentos ya calculados y hace lo que un modelo
hace bien: priorizar, detectar patrones y explicarle a una persona qué tiene
que hacer este mes.

Pedirle a un modelo que sume 2.780 filas es la forma más rápida de tener un
informe que suena bien y está mal.

## Archivos

| Archivo | Qué hace |
|---|---|
| `parsers.py` | Lee los exports de Geslib. Acepta CSV o PDF. |
| `analisis.py` | Cruza stock y ventas, clasifica en segmentos. |
| `informe.py` | Arma el prompt y llama a Claude. |
| `n8n_workflow.json` | El flujo mensual completo, listo para importar. |
| `output/informe_semanal.md` | Ejemplo de salida con datos reales. |

## Segmentos

| Segmento | Criterio | Acción |
|---|---|---|
| `LIQUIDAR` | 0 ventas en el período, ≥2 ejemplares | Mesa de descuento |
| `DEVOLVER` | 0 ventas en el período, 1 ejemplar | Devolución al distribuidor |
| `VIGILAR` | 1 venta, ≥2 ejemplares | Revisar el mes que viene |
| `REPONER` | ≥3 ventas, menos de 1,5 meses de cobertura | Pedido urgente |
| `DESTACAR` | ≥3 ventas, con stock | Mostrador |
| `MANTENER` | El resto | Sin acción |

Los umbrales están en `CONFIG`, arriba de `analisis.py`.

## Uso

```bash
# análisis solo (no necesita API key)
python3 analisis.py data/stock.csv data/ventas.csv > output/analisis.json

# informe completo
export ANTHROPIC_API_KEY="sk-ant-..."
python3 informe.py output/analisis.json > output/informe.md

# ver el prompt sin gastar tokens
python3 informe.py output/analisis.json --prompt
```

## Montarlo en n8n

1. Abrir n8n en `http://localhost:5678` (Chrome o Firefox — en Safari el
   login local falla por las cookies seguras).
2. **Workflows → Import from File** → `n8n_workflow.json`.
3. **Settings → Variables**: crear `ARENALES_DIR` con la ruta de esta carpeta.
4. La API key va como variable de entorno al arrancar n8n:
   ```bash
   ANTHROPIC_API_KEY="sk-ant-..." npx n8n
   ```
5. Dejar los CSV en `data/` como `stock.csv` y `ventas.csv`.
6. **Execute Workflow** para probarlo; después activarlo para que corra el
   día 1 de cada mes a las 8.

## Sobre los datos

El motor lee CSV y PDF. El CSV es el camino bueno: el export a PDF de Geslib
sale en A4 vertical y parte la planilla en cuatro bloques de columnas, lo que
obliga a reconstruir las filas cruzando páginas. Se hace, pero un 4,7% de las
filas queda sin título porque esas páginas desalinean.

El cruce título↔EAN reconstruido desde el PDF se validó contra los títulos del
informe de ventas, que es una fuente independiente: **355 de 355 coincidencias
(100%)**.

Aun así, con el CSV esto desaparece y además permite conectar el flujo directo
al sistema.

## Pendiente

- [ ] Export automático desde Geslib (hoy es manual)
- [ ] Distinguir depósito de compra firme: cambia si un título se devuelve o se
      liquida
- [ ] Márgenes por editorial, para priorizar por beneficio y no por PVP
- [ ] Envío del informe por email o WhatsApp
