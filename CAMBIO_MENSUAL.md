# Cambio: de informe semanal a mensual

Para Claude Code. Leé `CLAUDE.md` primero.

**Mostrame el plan antes de tocar archivos.** Son cambios chicos en cuatro
archivos, sin lógica nueva salvo el punto 1.

---

## Qué NO cambia

La ventana de análisis sigue siendo el histórico completo de ventas que traiga
el archivo. Lo que cambia es cada cuánto se corre el informe, no cuánto mira.

---

## 1 · `analisis.py` — detectar el período de los datos

Hoy `CONFIG["meses_historico"]` está fijo en 13. Eso es frágil: si el próximo
export trae 12 meses o 18, el ritmo mensual y la rotación salen mal sin que
nadie se entere.

**Calcularlo de los datos:** la primera y la última fecha de venta del archivo,
la diferencia en meses, mínimo 1. Si `CONFIG["meses_historico"]` tiene un valor
distinto de `None`, ese manda; dejalo en `None` por defecto.

Agregar al bloque `panorama`:

- `periodo_desde` y `periodo_hasta` en formato `dd/mm/aaaa`
- `meses_analizados` con el valor calculado

---

## 2 · `analisis.py` — renombrar dos campos

`vendidas_13m` → `vendidas_periodo`
`facturado_13m` → `facturado_periodo`

Tienen el número de meses metido en el nombre y eso deja de ser cierto en cuanto
cambie el export. Cambiarlos ahora, antes de que la web los use.

**Buscar en todo el proyecto** y actualizar cada uso: aparecen también en
`informe.py`. Verificar con `grep -rn "13m" .` que no quede ninguno.

---

## 3 · `informe.py` — pasar a mensual

En el texto de `ROL` y de `INSTRUCCIONES`:

| Dice | Tiene que decir |
|---|---|
| "el informe semanal" | "el informe mensual" |
| "## Lo que hay que hacer esta semana" | "## Lo que hay que hacer este mes" |
| "para poner a la vista esta semana" | "para poner a la vista este mes" |
| "ejecutarse esta semana" | "ejecutarse este mes" |
| "El análisis de rotación de esta semana" | "El análisis de rotación de este mes" |

En `_compactar`, actualizar las claves renombradas del punto 2.

**Agregar al prompt el período analizado**, para que el informe pueda decir
sobre qué datos está mirando. Algo como: *"Los datos de ventas van del
{periodo_desde} al {periodo_hasta}."* Va dentro del bloque `<analisis>`.

---

## 4 · `n8n_workflow.json` — schedule mensual

- Nombre del workflow: `Arenales — Informe de rotación mensual`
- Nombre del nodo trigger: `Día 1 de cada mes, 08:00`
- En `rule.interval`: `field` pasa de `"weeks"` a `"months"`, sacar
  `triggerAtDay`, agregar `triggerAtDayOfMonth: 1`. Mantener `triggerAtHour: 8`
  y `triggerAtMinute: 0`.

En el nodo `Componer el informe`, el pie que dice *"próxima ejecución: lunes"*
tiene que decir el día 1 del mes siguiente.

---

## 5 · `CLAUDE.md` y `README.md`

Reemplazar las menciones a "semanal", "semana" y "los lunes" por la cadencia
mensual. En `CLAUDE.md`, la frase *"qué tiene que hacer el lunes a la mañana"*
pasa a *"qué tiene que hacer este mes"*.

---

## Verificar

```bash
grep -rn "semanal\|semana\|lunes\|13m" . --include="*.py" --include="*.json" --include="*.md" --exclude-dir=.git
```

Solo deberían quedar menciones en `PLAN_3_DIAS.md`, `DIA_1.md` y este archivo,
que son guías de trabajo y no parte del producto.

Después:

```bash
python3 analisis.py data/stock.csv data/ventas.csv > output/analisis.json
python3 -c "import json;d=json.load(open('output/analisis.json'));p=d['panorama'];print(p['periodo_desde'],'→',p['periodo_hasta'],'|',p['meses_analizados'],'meses')"
```

**Tiene que imprimir** `03/06/2025 → 26/06/2026 | 13 meses` con los datos
actuales. Si da 13, la detección automática funciona y coincide con el valor
que estaba fijo antes.

Confirmar que el resto del panorama no se movió: `valor_stock_eur` sigue en
63552.39 y `rotacion_meses` en 29.9.
