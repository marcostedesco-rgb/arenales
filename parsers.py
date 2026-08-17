"""
Librería Arenales — Lectores de datos
=====================================
Convierten los exports de Geslib (PDF hoy, CSV mañana) a un formato común.

Formato común de STOCK:  {ean, titulo, unidades, valor_eur, pvp}
Formato común de VENTAS: {fecha, ean, titulo, unidades, importe_eur}
"""

import re
import csv
import subprocess
from pathlib import Path


# ---------------------------------------------------------------- utilidades

def _num(s):
    """'1.234,56' -> 1234.56"""
    if not s:
        return 0.0
    s = str(s).replace("€", "").strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def _pdf_text(path, first=None, last=None):
    cmd = ["pdftotext", "-layout"]
    if first:
        cmd += ["-f", str(first)]
    if last:
        cmd += ["-l", str(last)]
    cmd += [str(path), "-"]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


# ------------------------------------------------------------------- STOCK

_PATRON_EAN = re.compile(r"^\s*(\d{12,13})\s+([\d.,]+)\s*€\s*(\d*)\s*(Si|No)?\s*(\S*)")


def _bloques_por_cabecera(paginas):
    """Agrupa las páginas en bloques según con qué cabecera arrancan."""
    bloques = []
    actual = None
    for i, p in enumerate(paginas):
        cab = next((l for l in p.split("\n") if l.strip()), "").strip()
        clave = cab.split()[0] if cab else ""
        if actual is None or clave != actual[0]:
            actual = (clave, [])
            bloques.append(actual)
        actual[1].append(i)
    return bloques


_PATRON_EDITORIAL = re.compile(
    r"^(.*?)\s{2,}(\d{1,4})\s{2,}(.+?)\s{2,}([\d.,]+)\s*€\s*$")


def _editoriales_de_pagina(texto_pagina):
    """Extrae (autor, código, editorial, pvp) de una página del bloque 2."""
    filas = []
    for linea in texto_pagina.split("\n"):
        m = _PATRON_EDITORIAL.match(linea)
        if m:
            autor, codigo, editorial, pvp = m.groups()
            filas.append({
                "autor": autor.strip(),
                "cod_editorial": codigo,
                "editorial": editorial.strip(),
                "pvp": _num(pvp),
            })
    return filas


def _alinear(izq, der, clave_izq, clave_der):
    """
    Empareja dos listas de la misma página que deberían tener igual longitud.

    Si coinciden, el emparejamiento es posicional. Si no (el PDF a veces pierde
    o duplica un renglón), alineamos por la secuencia de PVP: es el único valor
    que aparece en los dos bloques, así que sirve de ancla. Devuelve pares
    (i, j); las filas sin pareja quedan fuera.
    """
    if len(izq) == len(der):
        return list(enumerate(range(len(der))))

    import difflib
    a = [round(clave_izq(x), 2) for x in izq]
    b = [round(clave_der(x), 2) for x in der]
    pares = []
    for i, j, n in difflib.SequenceMatcher(None, a, b).get_matching_blocks():
        pares += [(i + k, j + k) for k in range(n)]
    return pares


def _titulos_de_pagina(texto_pagina):
    """Extrae los títulos de una página del bloque 1, uniendo continuaciones."""
    titulos = []
    for linea in texto_pagina.split("\n"):
        if not linea.strip() or linea.strip().startswith("Título"):
            continue
        m = re.match(r"^\s*S\s{2,}(.+?)\s*$", linea)
        if m:
            titulos.append(m.group(1).strip())
        elif titulos:
            titulos[-1] += " " + linea.strip()
    return titulos


def _filas_de_pagina(texto_pagina):
    """Extrae EAN / valor / unidades de una página del bloque 3."""
    lineas = texto_pagina.split("\n")
    filas = []
    for i, linea in enumerate(lineas):
        m = _PATRON_EAN.match(linea)
        if not m:
            continue
        ean, valor, unid, revisado, _ = m.groups()

        # cuando el título de la fila era largo, la cantidad baja de renglón
        if not unid:
            for j in range(i + 1, min(i + 4, len(lineas))):
                if _PATRON_EAN.match(lineas[j]):
                    break
                suelto = re.match(r"^\s+(\d+)\s*$", lineas[j])
                if suelto:
                    unid = suelto.group(1)
                    break

        unidades = int(unid) if unid else 0
        valor_eur = _num(valor)
        filas.append({
            "ean": ean,
            "titulo": "",
            "autor": "",
            "editorial": "",
            "cod_editorial": "",
            "unidades": unidades,
            "valor_eur": valor_eur,
            "pvp": round(valor_eur / unidades, 2) if unidades else valor_eur,
            "revisado": revisado == "Si",
        })
    return filas


def leer_stock_pdf(path):
    """
    El export de Geslib->Google Sheets sale en A4 vertical, lo que parte la
    planilla en 4 bloques de columnas consecutivos:
        bloque 1: Título
        bloque 2: Autor / Editorial / Nombre Editorial / PVP
        bloque 3: EAN / Stock eur / Stk. Total / Revisado / Stock
        bloque 4: Nuevo stock / Comentario

    El bloque 3 es el que tiene la clave única (EAN) y las magnitudes que
    importan. Para recuperar el título lo cruzamos con el bloque 1 *página por
    página*: si una página tiene la misma cantidad de filas en ambos bloques,
    el cruce es seguro. Si no coincide, dejamos el título vacío en esa página
    en vez de arriesgar un cruce equivocado.
    """
    paginas = _pdf_text(path).split("\f")
    bloques = _bloques_por_cabecera(paginas)

    pags_titulo = next((p for c, p in bloques if c.startswith("Título")), [])
    pags_autor = next((p for c, p in bloques if c.startswith("Autor")), [])
    pags_ean = next((p for c, p in bloques if c.startswith("EAN")), [])
    if not pags_ean:
        raise ValueError("No se encontró el bloque EAN en el PDF de stock")

    filas = []
    sin_titulo = sin_editorial = 0
    for n, idx_ean in enumerate(pags_ean):
        pag = _filas_de_pagina(paginas[idx_ean])

        # --- título (bloque 1): solo cruce posicional, no hay ancla común
        titulos = (_titulos_de_pagina(paginas[pags_titulo[n]])
                   if n < len(pags_titulo) else [])
        if len(titulos) == len(pag):
            for fila, titulo in zip(pag, titulos):
                fila["titulo"] = titulo
        else:
            sin_titulo += len(pag)

        # --- editorial (bloque 2): el PVP aparece en los dos bloques y sirve
        #     de ancla, así que podemos alinear incluso si la página desfasa
        eds = (_editoriales_de_pagina(paginas[pags_autor[n]])
               if n < len(pags_autor) else [])
        emparejados = set()
        for j, i in _alinear(eds, pag, lambda e: e["pvp"], lambda f: f["pvp"]):
            if j < len(eds) and i < len(pag):
                pag[i]["autor"] = eds[j]["autor"]
                pag[i]["editorial"] = eds[j]["editorial"]
                pag[i]["cod_editorial"] = eds[j]["cod_editorial"]
                emparejados.add(i)
        sin_editorial += len(pag) - len(emparejados)

        filas.extend(pag)

    avisar = __import__("sys").stderr
    if sin_titulo:
        print(f"[aviso] {sin_titulo} filas ({sin_titulo / len(filas) * 100:.1f}%) "
              f"sin título por desalineación del PDF.", file=avisar)
    if sin_editorial:
        print(f"[aviso] {sin_editorial} filas ({sin_editorial / len(filas) * 100:.1f}%) "
              f"sin editorial.", file=avisar)
    return filas


def leer_stock_csv(path):
    """
    Lector del export CSV de Geslib. Tolera variantes de nombres de columna
    porque cada instalación de Geslib rotula distinto.
    """
    alias = {
        "ean": ["ean", "isbn", "codigo", "código", "cod. barras"],
        "titulo": ["titulo", "título", "descripcion", "descripción", "nombre"],
        "autor": ["autor", "author"],
        "editorial": ["editorial", "sello", "publisher"],
        "unidades": ["stk. total", "stk total", "stock", "unidades", "cantidad",
                     "existencias"],
        "valor_eur": ["stock eur", "stock €", "valor", "importe", "valor stock"],
        "pvp": ["pvp", "precio", "p.v.p."],
    }

    with open(path, encoding="utf-8-sig", newline="") as fh:
        muestra = fh.read(4096)
        fh.seek(0)
        try:
            dialecto = csv.Sniffer().sniff(muestra, delimiters=";,\t")
        except csv.Error:
            dialecto = csv.excel
        lector = csv.DictReader(fh, dialect=dialecto)
        columnas = {c.strip().lower(): c for c in (lector.fieldnames or [])}

        def buscar(campo):
            for opcion in alias[campo]:
                for col_norm, col_real in columnas.items():
                    if col_norm == opcion or col_norm.startswith(opcion):
                        return col_real
            return None

        mapa = {k: buscar(k) for k in alias}
        if not mapa["ean"]:
            raise ValueError(f"El CSV no tiene columna de EAN/ISBN. Vi: {lector.fieldnames}")

        filas = []
        for reg in lector:
            ean = re.sub(r"\D", "", str(reg.get(mapa["ean"], "")))
            if len(ean) < 12:
                continue
            unidades = int(_num(reg.get(mapa["unidades"], 0))) if mapa["unidades"] else 0
            valor = _num(reg.get(mapa["valor_eur"], 0)) if mapa["valor_eur"] else 0.0
            pvp = _num(reg.get(mapa["pvp"], 0)) if mapa["pvp"] else 0.0
            if not valor and pvp:
                valor = pvp * unidades
            filas.append({
                "ean": ean,
                "titulo": (reg.get(mapa["titulo"]) or "").strip() if mapa["titulo"] else "",
                "autor": (reg.get(mapa["autor"]) or "").strip() if mapa["autor"] else "",
                "editorial": (reg.get(mapa["editorial"]) or "").strip() if mapa["editorial"] else "",
                "cod_editorial": "",
                "unidades": unidades,
                "valor_eur": round(valor, 2),
                "pvp": pvp or (round(valor / unidades, 2) if unidades else 0.0),
                "revisado": False,
            })
        return filas


def leer_stock(path):
    path = Path(path)
    return leer_stock_csv(path) if path.suffix.lower() == ".csv" else leer_stock_pdf(path)


# ------------------------------------------------------------------ VENTAS

def leer_ventas_pdf(path):
    """Informe 'Ventas diarias' de Geslib."""
    lineas = _pdf_text(path).split("\n")
    re_isbn = re.compile(r"(97[89][-\d]{10,17})")
    re_fecha = re.compile(r"^\s*(\d{2}/\d{2}/\d{4})")
    re_importe = re.compile(r"([\d.]*\d,\d{2})")

    ventas = []
    fecha = None
    for linea in lineas:
        f = re_fecha.match(linea)
        if f:
            fecha = f.group(1)
        m = re_isbn.search(linea)
        if not m or not fecha:
            continue

        ean = m.group(1).replace("-", "")
        resto = linea[m.end():]
        importes = re_importe.findall(resto)
        if not importes:
            continue

        precio = _num(importes[0])
        importe = _num(importes[1]) if len(importes) > 1 else precio

        # el título del libro y la cantidad se pegan cuando el título es largo;
        # deducimos la cantidad del cociente importe/precio, que es robusto.
        unidades = round(importe / precio) if precio else 1
        if unidades < 1 or unidades > 50:
            unidades = 1

        titulo = resto[:resto.find(importes[0])] if importes[0] in resto else ""
        titulo = re.sub(r"\s*\d+\s*$", "", titulo).strip()

        ventas.append({
            "fecha": fecha,
            "ean": ean,
            "titulo": titulo,
            "unidades": unidades,
            "importe_eur": importe,
        })
    return ventas


def leer_ventas_csv(path):
    alias = {
        "fecha": ["fecha", "date", "dia", "día"],
        "ean": ["ean", "isbn", "articulo", "artículo", "codigo", "código"],
        "titulo": ["descripcion", "descripción", "titulo", "título", "nombre"],
        "unidades": ["cnt.", "cnt", "cantidad", "unidades", "qty"],
        "importe_eur": ["importe", "total", "importe eur"],
    }
    with open(path, encoding="utf-8-sig", newline="") as fh:
        muestra = fh.read(4096)
        fh.seek(0)
        try:
            dialecto = csv.Sniffer().sniff(muestra, delimiters=";,\t")
        except csv.Error:
            dialecto = csv.excel
        lector = csv.DictReader(fh, dialect=dialecto)
        columnas = {c.strip().lower(): c for c in (lector.fieldnames or [])}

        def buscar(campo):
            for opcion in alias[campo]:
                for col_norm, col_real in columnas.items():
                    if col_norm == opcion or col_norm.startswith(opcion):
                        return col_real
            return None

        mapa = {k: buscar(k) for k in alias}
        ventas = []
        for reg in lector:
            ean = re.sub(r"\D", "", str(reg.get(mapa["ean"], ""))) if mapa["ean"] else ""
            if len(ean) < 12:
                continue
            ventas.append({
                "fecha": (reg.get(mapa["fecha"]) or "").strip() if mapa["fecha"] else "",
                "ean": ean,
                "titulo": (reg.get(mapa["titulo"]) or "").strip() if mapa["titulo"] else "",
                "unidades": int(_num(reg.get(mapa["unidades"], 1))) or 1,
                "importe_eur": _num(reg.get(mapa["importe_eur"], 0)),
            })
        return ventas


def leer_ventas(path):
    path = Path(path)
    return leer_ventas_csv(path) if path.suffix.lower() == ".csv" else leer_ventas_pdf(path)
