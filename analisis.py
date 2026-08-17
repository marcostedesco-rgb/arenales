"""
Librería Arenales — Motor de análisis de rotación
=================================================
Cruza el stock actual contra el histórico de ventas y clasifica cada título
en un segmento accionable.

Regla de diseño: acá NO interviene la IA. Todos los números salen de
aritmética verificable. La IA se usa después, para decidir e interpretar,
nunca para contar.
"""

import math
from collections import defaultdict
from datetime import datetime

import parsers


# ------------------------------------------------------------------ ajustes

CONFIG = {
    "meses_historico": None,      # None = detectarla de los datos; si tiene un valor, ese manda
    "umbral_muerto": 0,           # ventas para considerar un título muerto
    "umbral_lento": 1,            # ventas para considerarlo lento
    "umbral_rotacion": 3,         # ventas para considerarlo de rotación
    "cobertura_critica": 1.5,     # meses de stock por debajo de los cuales urge reponer
    "cobertura_sana": 6,          # estándar del sector
    "meses_reposicion": 3,        # cuántos meses de ritmo cubre un pedido de reposición
    "descuento_liquidacion": 0.05,
    "tasa_devolucion": 0.60,      # % del PVP que suele reconocer el depósito

    # Editoriales que no son fondo de librería y quedan fuera del análisis.
    # "Laura Tedesco" es la etiqueta con la que se cataloga el libro usado:
    # no se devuelve al distribuidor ni se repone, así que mezclarlo con el
    # fondo nuevo ensucia la rotación y las decisiones de compra.
    "editoriales_excluidas": ["LAURA TEDESCO"],
}


def _mes(fecha):
    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(fecha, formato)
        except (ValueError, TypeError):
            continue
    return None


# ------------------------------------------------------------------ análisis

def cargar_datos(ruta_stock, ruta_ventas, config=None):
    """
    Lee stock y ventas, aplica la exclusión de editoriales y agrega las ventas
    por EAN. Es el cruce que necesita cualquier consumidor de estos datos
    (el análisis de rotación, pero también el catálogo de la web): separado
    acá para que la exclusión no se reimplemente en dos lugares.
    """
    cfg = {**CONFIG, **(config or {})}

    stock = parsers.leer_stock(ruta_stock)
    ventas = parsers.leer_ventas(ruta_ventas)

    # --- exclusión del libro usado
    excluidas = [e.upper() for e in cfg["editoriales_excluidas"]]
    if excluidas and not any(a.get("editorial") for a in stock):
        import sys
        print(f"[aviso] Se pidió excluir {', '.join(cfg['editoriales_excluidas'])} "
              f"pero el archivo no trae columna de editorial: no se excluyó nada.",
              file=sys.stderr)
    if excluidas:
        fuera = {a["ean"] for a in stock
                 if any(e in a.get("editorial", "").upper() for e in excluidas)}
        excluido = {
            "editoriales": cfg["editoriales_excluidas"],
            "titulos": len(fuera),
            "unidades": sum(a["unidades"] for a in stock if a["ean"] in fuera),
            "valor_eur": round(sum(a["valor_eur"] for a in stock if a["ean"] in fuera), 2),
            "ventas_eur": round(sum(v["importe_eur"] for v in ventas
                                    if v["ean"] in fuera), 2),
        }
        stock = [a for a in stock if a["ean"] not in fuera]
        ventas = [v for v in ventas if v["ean"] not in fuera]
    else:
        excluido = None

    # --- agregación de ventas por título
    por_ean = defaultdict(lambda: {"unidades": 0, "importe": 0.0,
                                   "titulo": "", "fechas": []})
    for v in ventas:
        reg = por_ean[v["ean"]]
        reg["unidades"] += v["unidades"]
        reg["importe"] += v["importe_eur"]
        if v["titulo"] and len(v["titulo"]) > len(reg["titulo"]):
            reg["titulo"] = v["titulo"]
        f = _mes(v["fecha"])
        if f:
            reg["fechas"].append(f)

    fechas_todas = [f for r in por_ean.values() for f in r["fechas"]]
    periodo_desde_dt = min(fechas_todas) if fechas_todas else None
    periodo_hasta_dt = max(fechas_todas) if fechas_todas else None

    if cfg["meses_historico"] is not None:
        meses = cfg["meses_historico"]
    elif periodo_desde_dt and periodo_hasta_dt:
        meses = max(1, (periodo_hasta_dt.year - periodo_desde_dt.year) * 12
                    + (periodo_hasta_dt.month - periodo_desde_dt.month) + 1)
    else:
        meses = 1

    return {
        "cfg": cfg,
        "stock": stock,
        "por_ean": por_ean,
        "meses": meses,
        "periodo_desde_dt": periodo_desde_dt,
        "periodo_hasta_dt": periodo_hasta_dt,
        "excluido": excluido,
    }


def analizar(ruta_stock, ruta_ventas, config=None):
    datos = cargar_datos(ruta_stock, ruta_ventas, config)
    cfg = datos["cfg"]
    stock = datos["stock"]
    por_ean = datos["por_ean"]
    meses = datos["meses"]
    periodo_desde_dt = datos["periodo_desde_dt"]
    periodo_hasta_dt = datos["periodo_hasta_dt"]
    excluido = datos["excluido"]
    hoy = periodo_hasta_dt

    # --- clasificación título por título
    fichas = []
    for art in stock:
        ean = art["ean"]
        v = por_ean.get(ean)
        vendidas = v["unidades"] if v else 0
        facturado = v["importe"] if v else 0.0
        ritmo = vendidas / meses                       # unidades por mes
        cobertura = art["unidades"] / ritmo if ritmo else float("inf")

        ultima = max(v["fechas"]) if v and v["fechas"] else None
        dias_sin_vender = (hoy - ultima).days if (ultima and hoy) else None

        if vendidas <= cfg["umbral_muerto"]:
            segmento = "LIQUIDAR" if art["unidades"] >= 2 else "DEVOLVER"
        elif vendidas <= cfg["umbral_lento"] and art["unidades"] >= 2:
            segmento = "VIGILAR"
        elif vendidas >= cfg["umbral_rotacion"] and cobertura <= cfg["cobertura_critica"]:
            segmento = "REPONER"
        elif vendidas >= cfg["umbral_rotacion"]:
            segmento = "DESTACAR"
        else:
            segmento = "MANTENER"

        fichas.append({
            "ean": ean,
            "titulo": art["titulo"] or (v["titulo"] if v else ""),
            "autor": art.get("autor", ""),
            "editorial": art.get("editorial", ""),
            "unidades_stock": art["unidades"],
            "valor_eur": round(art["valor_eur"], 2),
            "pvp": art["pvp"],
            "vendidas_periodo": vendidas,
            "facturado_periodo": round(facturado, 2),
            "ritmo_mensual": round(ritmo, 2),
            "cobertura_meses": (round(cobertura, 1) if cobertura != float("inf") else None),
            "dias_sin_vender": dias_sin_vender,
            "segmento": segmento,
        })

    # --- títulos que vendieron pero ya no figuran en stock (rotura)
    en_stock = {a["ean"] for a in stock}
    roturas = []
    for ean, v in por_ean.items():
        if ean in en_stock or v["unidades"] < cfg["umbral_rotacion"]:
            continue
        roturas.append({
            "ean": ean,
            "titulo": v["titulo"],
            "autor": "",
            "editorial": "",
            "unidades_stock": 0,
            "valor_eur": 0.0,
            "pvp": round(v["importe"] / v["unidades"], 2) if v["unidades"] else 0.0,
            "vendidas_periodo": v["unidades"],
            "facturado_periodo": round(v["importe"], 2),
            "ritmo_mensual": round(v["unidades"] / meses, 2),
            "cobertura_meses": 0.0,
            "dias_sin_vender": (hoy - max(v["fechas"])).days if v["fechas"] and hoy else None,
            "segmento": "REPONER",
        })
    fichas.extend(roturas)

    # la facturación del período se mide sobre TODAS las ventas, incluidas las
    # de títulos que ya no están en el stock; si no, la rotación sale inflada.
    facturacion_total = sum(v["importe"] for v in por_ean.values())
    unidades_vendidas = sum(v["unidades"] for v in por_ean.values())

    resultado = _resumir(fichas, cfg, meses, facturacion_total, unidades_vendidas,
                         len(por_ean), periodo_desde_dt, periodo_hasta_dt)
    resultado["excluido"] = excluido
    return resultado


def _resumir(fichas, cfg, meses, facturacion, unidades_vendidas, titulos_vendidos,
             periodo_desde_dt=None, periodo_hasta_dt=None):
    por_segmento = defaultdict(list)
    for f in fichas:
        por_segmento[f["segmento"]].append(f)

    valor_total = sum(f["valor_eur"] for f in fichas)
    unidades_total = sum(f["unidades_stock"] for f in fichas)
    facturacion_mensual = facturacion / meses if meses else 0

    muerto = por_segmento["LIQUIDAR"] + por_segmento["DEVOLVER"]
    valor_muerto = sum(f["valor_eur"] for f in muerto)

    caja_liquidacion = sum(f["valor_eur"] for f in por_segmento["LIQUIDAR"]) * (
        1 - cfg["descuento_liquidacion"])
    caja_devolucion = sum(f["valor_eur"] for f in por_segmento["DEVOLVER"]) * cfg["tasa_devolucion"]

    def top(segmento, clave, n=20):
        return sorted(por_segmento[segmento], key=lambda f: -f[clave])[:n]

    def con_pvp_liquidacion(f):
        return {**f, "pvp_liquidacion": round(f["pvp"] * (1 - cfg["descuento_liquidacion"]), 2)}

    def con_sugerido_pedir(f):
        pedir = math.ceil(f["ritmo_mensual"] * cfg["meses_reposicion"]) - f["unidades_stock"]
        return {**f, "sugerido_pedir": max(1, pedir)}

    listas = {
        "liquidar": sorted((con_pvp_liquidacion(f) for f in por_segmento["LIQUIDAR"]),
                           key=lambda f: -f["valor_eur"]),
        "devolver": sorted(por_segmento["DEVOLVER"], key=lambda f: -f["valor_eur"]),
        "reponer": sorted((con_sugerido_pedir(f) for f in por_segmento["REPONER"]),
                          key=lambda f: -f["facturado_periodo"]),
        "destacar": sorted(por_segmento["DESTACAR"], key=lambda f: -f["facturado_periodo"]),
    }

    return {
        "generado": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "panorama": {
            "titulos": len(fichas),
            "unidades": unidades_total,
            "valor_stock_eur": round(valor_total, 2),
            "facturacion_periodo_eur": round(facturacion, 2),
            "facturacion_mensual_eur": round(facturacion_mensual, 2),
            "unidades_vendidas_periodo": unidades_vendidas,
            "titulos_vendidos_periodo": titulos_vendidos,
            "periodo_desde": periodo_desde_dt.strftime("%d/%m/%Y") if periodo_desde_dt else None,
            "periodo_hasta": periodo_hasta_dt.strftime("%d/%m/%Y") if periodo_hasta_dt else None,
            "meses_analizados": meses,
            "rotacion_meses": round(valor_total / facturacion_mensual, 1) if facturacion_mensual else None,
            "rotacion_objetivo": cfg["cobertura_sana"],
            "titulos_sin_venta": len(muerto),
            "pct_titulos_sin_venta": round(len(muerto) / len(fichas) * 100, 1) if fichas else 0,
            "capital_inmovilizado_eur": round(valor_muerto, 2),
            "pct_capital_inmovilizado": round(valor_muerto / valor_total * 100, 1) if valor_total else 0,
            "caja_recuperable_estimada_eur": round(caja_liquidacion + caja_devolucion, 2),
        },
        "segmentos": {
            nombre: {
                "titulos": len(filas),
                "unidades": sum(f["unidades_stock"] for f in filas),
                "valor_eur": round(sum(f["valor_eur"] for f in filas), 2),
            }
            for nombre, filas in sorted(por_segmento.items())
        },
        "liquidar": top("LIQUIDAR", "valor_eur"),
        "devolver": top("DEVOLVER", "valor_eur"),
        "reponer": top("REPONER", "facturado_periodo"),
        "destacar": top("DESTACAR", "facturado_periodo"),
        "vigilar": top("VIGILAR", "valor_eur", 10),
        "listas": listas,
    }


if __name__ == "__main__":
    import json
    import sys

    stock = sys.argv[1] if len(sys.argv) > 1 else "data/stock.pdf"
    ventas = sys.argv[2] if len(sys.argv) > 2 else "data/ventas.pdf"
    resultado = analizar(stock, ventas)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
