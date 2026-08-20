"""
Librería Arenales — Datos para la web
======================================
Genera los dos módulos que consumen las funciones de /api: el catálogo para
el chat (solo lo necesario para recomendar) y una copia de output/analisis.json
para el panel. Ninguno de los dos se sirve como archivo estático: viven en
web/api/_datos/, que Vercel no expone como ruta.
"""

import json
import sys
from pathlib import Path

import analisis


def _catalogo(ruta_stock, ruta_ventas):
    datos = analisis.cargar_datos(ruta_stock, ruta_ventas)
    por_ean = datos["por_ean"]

    catalogo = []
    for art in datos["stock"]:
        if art["unidades"] <= 0:
            continue
        v = por_ean.get(art["ean"])
        vendidas = v["unidades"] if v else 0
        catalogo.append({
            "t": art["titulo"],
            "a": art.get("autor", ""),
            "e": art.get("editorial", ""),
            "p": art["pvp"],
            "u": art["unidades"],
            "v": vendidas,
            "m": vendidas == 0,
        })
    return catalogo


def generar(ruta_stock="data/stock.xls", ruta_ventas="data/ventas.xls",
            ruta_analisis="output/analisis.json", carpeta_salida="web/api/_datos"):
    salida = Path(carpeta_salida)
    salida.mkdir(parents=True, exist_ok=True)

    catalogo = _catalogo(ruta_stock, ruta_ventas)
    (salida / "catalogo.js").write_text(
        "module.exports = " + json.dumps(catalogo, ensure_ascii=False) + ";\n",
        encoding="utf-8")

    analisis_json = json.load(open(ruta_analisis, encoding="utf-8"))
    (salida / "analisis.js").write_text(
        "module.exports = " + json.dumps(analisis_json, ensure_ascii=False) + ";\n",
        encoding="utf-8")

    return len(catalogo)


if __name__ == "__main__":
    n = generar()
    print(f"catalogo.js: {n} títulos con stock. analisis.js: copiado.", file=sys.stderr)
