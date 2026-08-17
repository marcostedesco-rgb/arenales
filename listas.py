"""
Librería Arenales — Listas de trabajo para el mostrador
========================================================
Lee output/analisis.json y escribe los CSV que se pueden imprimir o tildar
a mano: liquidar, devolver, reponer, destacar. Formato pensado para abrirse
en Excel en España: separador punto y coma, BOM, coma decimal, EAN en texto.
"""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path


def _eur(n):
    return f"{n:.2f}".replace(".", ",")


def _ean_texto(ean):
    return f"'{ean}"


def _escribir(ruta, columnas, filas):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8-sig", newline="") as fh:
        escritor = csv.writer(fh, delimiter=";")
        escritor.writerow(columnas)
        escritor.writerows(filas)


def generar(ruta_analisis="output/analisis.json", carpeta_salida="output/listas"):
    datos = json.load(open(ruta_analisis, encoding="utf-8"))
    listas = datos["listas"]
    mes = datetime.now().strftime("%Y-%m")
    salida = Path(carpeta_salida)

    por_editorial_y_valor = lambda filas: sorted(
        filas, key=lambda f: (f.get("editorial") or "", -f["valor_eur"]))

    _escribir(
        salida / f"liquidar_{mes}.csv",
        ["EAN", "Título", "Autor", "Editorial", "Ejemplares", "PVP",
         "Precio liquidación", "Valor total", "Hecho"],
        [
            [_ean_texto(f["ean"]), f["titulo"], f["autor"], f["editorial"],
             f["unidades_stock"], _eur(f["pvp"]), _eur(f["pvp_liquidacion"]),
             _eur(f["valor_eur"]), ""]
            for f in por_editorial_y_valor(listas["liquidar"])
        ],
    )

    _escribir(
        salida / f"devolver_{mes}.csv",
        ["EAN", "Título", "Autor", "Editorial", "Ejemplares", "PVP", "Valor total", "Hecho"],
        [
            [_ean_texto(f["ean"]), f["titulo"], f["autor"], f["editorial"],
             f["unidades_stock"], _eur(f["pvp"]), _eur(f["valor_eur"]), ""]
            for f in por_editorial_y_valor(listas["devolver"])
        ],
    )

    _escribir(
        salida / f"reponer_{mes}.csv",
        ["EAN", "Título", "Autor", "Editorial", "Vendidos", "Stock actual",
         "Facturado", "Pedir", "Hecho"],
        [
            [_ean_texto(f["ean"]), f["titulo"], f["autor"], f["editorial"],
             f["vendidas_periodo"], f["unidades_stock"], _eur(f["facturado_periodo"]),
             f["sugerido_pedir"], ""]
            for f in listas["reponer"]
        ],
    )

    _escribir(
        salida / f"destacar_{mes}.csv",
        ["EAN", "Título", "Autor", "Editorial", "Vendidos", "Stock actual",
         "Facturado", "Hecho"],
        [
            [_ean_texto(f["ean"]), f["titulo"], f["autor"], f["editorial"],
             f["vendidas_periodo"], f["unidades_stock"], _eur(f["facturado_periodo"]), ""]
            for f in listas["destacar"]
        ],
    )

    return salida


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "output/analisis.json"
    carpeta = generar(ruta)
    print(f"Listas escritas en {carpeta}/", file=sys.stderr)
