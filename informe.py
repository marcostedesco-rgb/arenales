"""
Librería Arenales — Capa de decisión (Claude)
=============================================
Toma los segmentos que calculó `analisis.py` y le pide a Claude que redacte
las recomendaciones del mes con criterio de librero.

División de tareas deliberada:
  · analisis.py  -> cuenta, cruza y clasifica. Aritmética verificable.
  · informe.py   -> decide, prioriza y explica. Criterio comercial.

A la IA nunca se le pide que sume. Se le pide que resuelva qué hacer.
"""

import json
import os
import urllib.request

MODELO = "claude-sonnet-4-6"
API_URL = "https://api.anthropic.com/v1/messages"


ROL = """Sos el analista de compras de Librería Arenales, una librería \
independiente de Chamberí (Madrid) especializada en literatura \
hispanoamericana. Tiene 5 estrellas en Google, club de lectura propio y \
cuentacuentos los sábados.

La situación es crítica y la conocés: la librería factura mucho menos de lo \
que cuesta sostenerla y los socios vienen inyectando capital todos los meses \
para cubrir el hueco. El capital está atrapado en las estanterías. Tu trabajo \
es liberarlo sin romper la identidad de la librería.

Escribís para los socios y para quien atiende el mostrador. Hablás en \
castellano de España, directo, sin jerga de consultoría y sin adornos. \
Cada recomendación tuya tiene que poder ejecutarse este mes."""


INSTRUCCIONES = """Te paso el análisis de rotación de este mes. Los números \
ya están calculados y son correctos: no los recalcules ni los pongas en duda, \
usalos tal cual.

Tu tarea es escribir el informe mensual con esta estructura exacta:

## Lo que hay que hacer este mes
Tres acciones concretas, numeradas, en orden de impacto sobre la caja. Cada \
una con el título de los libros involucrados y el euro que mueve. Nada de \
"considerar" ni "evaluar": verbos de ejecución.

## Devolver y liquidar
Qué sacar de la estantería y por qué. Distinguí entre lo que conviene \
devolver al distribuidor y lo que conviene liquidar con descuento en tienda. \
Si ves un patrón temático o de sello en el stock muerto, decilo: eso corrige \
la política de compras hacia adelante.

## Reponer con urgencia
Títulos que venden y están agotados o casi. Cada día sin ellos es venta \
perdida. Ordenalos por lo que facturaron.

## Para el mostrador
Cinco títulos que tengan stock y rotación, para poner a la vista este mes. \
Una línea por título explicando por qué ese.

## Lo que aprendimos
Dos o tres observaciones sobre qué tipo de libro funciona y cuál no en esta \
librería. Esto alimenta las compras del mes que viene.

Reglas:
- Si un dato no está en el análisis, no lo inventes. Decí que falta.
- Nada de tablas de más de cuatro columnas.
- El informe entero, por debajo de 700 palabras."""


def _compactar(datos, tope=25):
    """Recorta el análisis a lo que la IA necesita ver, sin ruido."""
    def limpiar(filas):
        return [
            {
                "titulo": f["titulo"] or f"[sin título] {f['ean']}",
                "stock": f["unidades_stock"],
                "eur": f["valor_eur"],
                "vendidas": f["vendidas_periodo"],
                "facturado": f["facturado_periodo"],
                "cobertura_meses": f["cobertura_meses"],
            }
            for f in filas[:tope]
        ]

    return {
        "panorama": datos["panorama"],
        "segmentos": datos["segmentos"],
        "liquidar": limpiar(datos["liquidar"]),
        "devolver": limpiar(datos["devolver"]),
        "reponer": limpiar(datos["reponer"]),
        "destacar": limpiar(datos["destacar"]),
        "vigilar": limpiar(datos["vigilar"], ),
    }


def construir_prompt(datos):
    p = datos["panorama"]
    periodo = (
        f"Los datos de ventas van del {p['periodo_desde']} al {p['periodo_hasta']}.\n\n"
        if p.get("periodo_desde") and p.get("periodo_hasta") else ""
    )
    return (
        f"{INSTRUCCIONES}\n\n"
        f"<analisis>\n{periodo}"
        f"{json.dumps(_compactar(datos), ensure_ascii=False, indent=1)}\n</analisis>"
    )


def redactar(datos, api_key=None, modelo=MODELO):
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Falta ANTHROPIC_API_KEY")

    cuerpo = json.dumps({
        "model": modelo,
        "max_tokens": 2000,
        "system": ROL,
        "messages": [{"role": "user", "content": construir_prompt(datos)}],
    }).encode()

    pedido = urllib.request.Request(
        API_URL,
        data=cuerpo,
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(pedido, timeout=120) as r:
        respuesta = json.loads(r.read())
    return respuesta["content"][0]["text"]


if __name__ == "__main__":
    import sys

    datos = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "output/analisis.json",
                           encoding="utf-8"))
    if "--prompt" in sys.argv:
        print(construir_prompt(datos))
    else:
        print(redactar(datos))
