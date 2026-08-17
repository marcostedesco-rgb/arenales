"""
Librería Arenales — Adjuntos del mail en base64
================================================
Lee los CSV de output/listas/ y los imprime como JSON {segmento: base64} por
stdout. Existe para que n8n arme los adjuntos del mail sin depender de nodos
de lectura de archivos ni de combinar ítems: un solo Code node con este
stdout ya puede construir el binario directo.
"""

import base64
import json
import sys
from pathlib import Path


def generar(carpeta="output/listas"):
    salida = {}
    for ruta in sorted(Path(carpeta).glob("*.csv")):
        clave = ruta.name.split("_")[0]
        salida[clave] = base64.b64encode(ruta.read_bytes()).decode("ascii")
    return salida


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "output/listas"
    print(json.dumps(generar(carpeta)))
