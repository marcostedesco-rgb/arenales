"""
Librería Arenales — Lectores de datos
=====================================
Convierten los exports de Geslib (PDF, CSV o el XLS de "Valoración de
centro" / "Ventas diarias" que Geslib genera directo) a un formato común.

Formato común de STOCK:  {ean, titulo, unidades, valor_eur, pvp}
Formato común de VENTAS: {fecha, ean, titulo, unidades, importe_eur}
"""

import re
import csv
import subprocess
import unicodedata
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


def _plano(s):
    """'Descripción' -> 'descripcion' — para comparar encabezados sin acentos."""
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return s.strip().lower()


def _celda(fila, indice):
    return fila[indice] if 0 <= indice < len(fila) else ""


def _es_ean(valor):
    """Devuelve el EAN limpio de guiones, o None si no tiene pinta de EAN/ISBN."""
    digitos = re.sub(r"\D", "", str(valor or ""))
    return digitos if len(digitos) >= 12 else None


def _fila_encabezado(fila, etiquetas_necesarias):
    presentes = {_plano(v) for v in fila if v not in (None, "")}
    return etiquetas_necesarias <= presentes


def _mapa_encabezado(fila, etiquetas):
    mapa = {}
    for i, valor in enumerate(fila):
        v = _plano(valor)
        if v in etiquetas:
            mapa[v] = i
    return mapa


def _hoja_xls(path):
    """Primera hoja de un .xls/.xlsx como lista de filas.

    Los exports de Geslib salen del "Reports" de un ERP viejo y no siempre
    respetan el formato BIFF al pie de la letra (algunos traen un EXTERNSHEET
    mal armado que hace que xlrd los rechace). calamine los lee igual.
    """
    from python_calamine import CalamineWorkbook
    return CalamineWorkbook.from_path(str(path)).get_sheet_by_index(0).to_python()


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


_ETIQUETAS_STOCK = {"articulo", "descripcion", "autor", "stock", "pvp"}


def leer_stock_xls(path):
    """
    Lector del XLS "Inventario: Valoración de centro" que exporta Geslib
    directo (sin pasar por Google Sheets ni PDF).

    El reporte agrupa los títulos por "Familia" (= editorial), repitiendo el
    encabezado de columnas en cada grupo y cerrando cada uno con una fila de
    subtotal. Todas esas filas de encabezado, subtotal, "Página X de Y" y
    "Total" traen la columna Artículo vacía, así que basta con quedarse con
    las filas cuyo primer valor tiene forma de EAN — no hace falta llevar un
    estado de "dónde estoy dentro del bloque".

    Ojo con la columna PVP: acá no es el precio unitario, es el valor total
    de ese título en stock (unidades × pvp) — igual que "Stock eur" en el PDF
    viejo. El precio unitario sale de dividir por las unidades.
    """
    filas = _hoja_xls(path)

    idx = {}
    editorial_actual = ""
    resultado = []

    for fila in filas:
        if not idx and _fila_encabezado(fila, _ETIQUETAS_STOCK):
            idx = _mapa_encabezado(fila, _ETIQUETAS_STOCK)
            continue

        if len(fila) > 2 and _plano(_celda(fila, 1)) == "familia" and _celda(fila, 2):
            editorial_actual = re.sub(r"^\(\d+\)\s*-\s*", "", str(fila[2]).strip())
            continue

        if not idx:
            continue

        ean = _es_ean(_celda(fila, idx.get("articulo", -1)))
        if not ean:
            continue

        unidades = int(_celda(fila, idx.get("stock", -1)) or 0)
        valor_eur = float(_celda(fila, idx.get("pvp", -1)) or 0)
        pvp = round(valor_eur / unidades, 2) if unidades else 0.0

        resultado.append({
            "ean": ean,
            "titulo": str(_celda(fila, idx.get("descripcion", -1)) or "").strip(),
            "autor": str(_celda(fila, idx.get("autor", -1)) or "").strip(),
            "editorial": editorial_actual,
            "cod_editorial": "",
            "unidades": unidades,
            "valor_eur": round(valor_eur, 2),
            "pvp": pvp,
            "revisado": False,
        })

    return resultado


def leer_stock(path):
    path = Path(path)
    sufijo = path.suffix.lower()
    if sufijo == ".csv":
        return leer_stock_csv(path)
    if sufijo in (".xls", ".xlsx"):
        return leer_stock_xls(path)
    return leer_stock_pdf(path)


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


_ETIQUETAS_VENTAS = {"fecha", "articulo", "descripcion", "cnt.", "importe"}


def leer_ventas_xls(path):
    """
    Lector del XLS "Ventas: Ventas diarias" que exporta Geslib directo.
    Una fila por línea de venta, sin agrupar — más simple que el de stock.

    Las líneas de descuento tipo "3X2 LIBROS USADOS" traen '***' en vez de
    EAN y cantidad negativa: no son ventas de un título real, quedan fuera
    igual que en el lector de CSV.
    """
    filas = _hoja_xls(path)

    idx = {}
    ventas = []

    for fila in filas:
        if not idx and _fila_encabezado(fila, _ETIQUETAS_VENTAS):
            idx = _mapa_encabezado(fila, _ETIQUETAS_VENTAS)
            continue

        if not idx:
            continue

        ean = _es_ean(_celda(fila, idx.get("articulo", -1)))
        if not ean:
            continue

        fecha_valor = _celda(fila, idx.get("fecha", -1))
        fecha = (fecha_valor.strftime("%d/%m/%Y") if hasattr(fecha_valor, "strftime")
                 else str(fecha_valor))
        cantidad = _celda(fila, idx.get("cnt.", -1))
        unidades = int(cantidad) if str(cantidad).strip() not in ("", "None") else 1

        ventas.append({
            "fecha": fecha,
            "ean": ean,
            "titulo": str(_celda(fila, idx.get("descripcion", -1)) or "").strip(),
            "unidades": unidades,
            "importe_eur": round(float(_celda(fila, idx.get("importe", -1)) or 0), 2),
        })

    return ventas


def leer_ventas(path):
    path = Path(path)
    sufijo = path.suffix.lower()
    if sufijo == ".csv":
        return leer_ventas_csv(path)
    if sufijo in (".xls", ".xlsx"):
        return leer_ventas_xls(path)
    return leer_ventas_pdf(path)
