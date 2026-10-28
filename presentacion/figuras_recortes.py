"""Ejemplos reales para la sección «De la figura al recorte» de la presentación.

Todo sale de archivos del repositorio:
- entrega/ejemplos_presentacion/ (Héctor): 10 figuras originales con sus cajas dibujadas (2 por destino), recortes_por_clase.jpg y creditos.csv
  (artículo, DOI y licencia de cada imagen). Se muestran SIEMPRE con su crédito.
- modelos/flujo_figuras/figuras_vision.csv, segmentacion/cajas/paneles.csv e indice_recortes.csv: conteos y cajas.
- Para la demostración «figura original → cajas → recortes» se usa una figura compuesta que sí está en producto/imagenes/ (fuera de Git):
  los recortes se generan aplicando las cajas normalizadas a la figura original.
Lo llama construir_datos.py.
"""
import csv
import random
import shutil
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent
FV = RAIZ / "modelos" / "flujo_figuras"
HECTOR = RAIZ / "entrega" / "ejemplos_presentacion"
SEMILLA = 24
COLOR = {"micro": (46, 158, 91), "espectro": (31, 120, 209), "otro": (224, 138, 0)}
DESTINOS = [
    ("simple", "Simple", "Un solo panel. Si es una micrografía de partículas, entra tal cual."),
    ("pareja", "Pareja", "Dos paneles, por ejemplo una micrografía y su espectro. Se separan en dos recortes."),
    ("compuesta", "Compuesta", "Tres o más paneles (micrografías, espectros, fotos, gráficos). Se separan con una caja por panel."),
    ("superpuesto", "Superpuesto", "Varias curvas espectrales superpuestas en los mismos ejes. No sirve para entrenar."),
    ("excluir", "Excluir", "No es una micrografía ni un espectro útil (esquemas, tablas, fotos…). No se usa."),
]
NOMBRE_CLASE = {"inorganico": "Inorgánico", "lipidico": "Lipídico", "nanomaterial": "Nanomaterial", "polimerico": "Polimérico"}


def leer(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fuente(tam: int):
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:
        return ImageFont.load_default()


def reducir(im: Image.Image, ancho: int) -> Image.Image:
    if im.width <= ancho:
        return im.copy()
    return im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)


def dibujar_cajas(im: Image.Image, cajas: list[dict]) -> Image.Image:
    out = im.copy()
    d = ImageDraw.Draw(out)
    grosor = max(2, round(out.width / 260))
    f = fuente(max(12, round(out.width / 45)))
    for c in cajas:
        x0, y0, x1, y1 = (float(c[k]) for k in ("x0", "y0", "x1", "y1"))
        caja = [x0 * out.width, y0 * out.height, x1 * out.width, y1 * out.height]
        col = COLOR.get(c["tipo"], COLOR["otro"])
        hija = bool(c["padre"])
        d.rectangle(caja, outline=col, width=max(1, grosor - 1) if hija else grosor)
        etiqueta = f"{c['panel']}" + ("·inset" if hija else "")
        tw = d.textlength(etiqueta, font=f)
        d.rectangle([caja[0], caja[1], caja[0] + tw + 8, caja[1] + f.size + 4], fill=col)
        d.text((caja[0] + 4, caja[1] + 1), etiqueta, fill=(255, 255, 255), font=f)
    return out


def recortar(im: Image.Image, c: dict) -> Image.Image:
    x0, y0, x1, y1 = (float(c[k]) for k in ("x0", "y0", "x1", "y1"))
    return im.crop((round(x0 * im.width), round(y0 * im.height), round(x1 * im.width), round(y1 * im.height)))


def cuadrado(im: Image.Image, lado: int) -> Image.Image:
    im = im.copy()
    im.thumbnail((lado, lado), Image.LANCZOS)
    lienzo = Image.new("RGB", (lado, lado), (255, 255, 255))
    lienzo.paste(im, ((lado - im.width) // 2, (lado - im.height) // 2))
    return lienzo


def credito_csv(fila: dict) -> dict:
    return {"titulo": fila["titulo"].replace("*", "").strip(), "doi": fila["doi"], "licencia": fila["licencia"].upper()}


def credito_articulo(arts: dict, pmcid: str) -> dict:
    a = arts[pmcid]
    return {"titulo": a["title"].replace("<i>", "").replace("</i>", "").strip(), "anio": a["year"], "doi": a["doi_link"], "licencia": a["license_epmc"].upper()}


def construir() -> dict:
    carpeta = SALIDA / "assets" / "recortes"
    if carpeta.exists():
        for p in carpeta.glob("*.jpg"):
            p.unlink()
    carpeta.mkdir(parents=True, exist_ok=True)
    arts = {r["pmcid"]: r for r in leer(RAIZ / "curation" / "ext_articulos.csv")}
    fv = leer(FV / "figuras_vision.csv")
    cajas = leer(FV / "segmentacion" / "cajas" / "paneles.csv")
    n = len(fv)
    cuenta = Counter(r["destino_vision"] for r in fv)
    estados = {d: Counter(r["estado"] for r in fv if r["destino_vision"] == d) for d, _, _ in DESTINOS}

    # 1) ejemplos de Héctor (figuras con cajas dibujadas) con su crédito de creditos.csv
    creditos = leer(HECTOR / "creditos.csv")
    destinos = []
    for d, nombre, frase in DESTINOS:
        ejemplos = []
        for r in (c for c in creditos if c["destino"] == d):
            shutil.copyfile(HECTOR / r["archivo"], carpeta / f"h_{r['archivo']}")
            ejemplos.append({"fig_id": r["fig_id"], "n_paneles": int(r["paneles"]), "cajas": f"assets/recortes/h_{r['archivo']}", "original": None,
                             "credito": credito_csv(r)})
        destinos.append({"id": d, "nombre": nombre, "frase": frase, "n": cuenta[d], "pct": round(100 * cuenta[d] / n, 1),
                         "aceptada_auto": estados[d]["aceptada_auto"], "aceptada_arbitrada": estados[d]["aceptada_arbitrada"],
                         "cola_revision": estados[d]["cola_revision"], "ejemplos": ejemplos})

    # 2) muestra sin retoques de Héctor: recortes_por_clase.jpg + créditos por clase
    shutil.copyfile(HECTOR / "recortes_por_clase.jpg", carpeta / "h_recortes_por_clase.jpg")
    muestra = {"imagen": "assets/recortes/h_recortes_por_clase.jpg",
               "creditos": [{"clase": NOMBRE_CLASE[c["destino"].split(":")[1]], "credito": credito_csv(c)} for c in creditos if c["destino"].startswith("recorte:")]}

    # 3) demostración de tres pasos con una figura compuesta que está en este equipo
    por_fig: dict[str, list[dict]] = {}
    for c in cajas:
        por_fig.setdefault(c["fig_id"], []).append(c)
    rng = random.Random(SEMILLA)
    cand = [r for r in fv if r["destino_vision"] == "compuesta" and r["estado"] != "cola_revision" and r["pmcid"] in arts and (RAIZ / r["imagen"]).exists()
            and 4 <= sum(1 for c in por_fig.get(r["fig_id"], []) if not c["padre"]) <= 8
            and all(c["tipo"] == "micro" for c in por_fig.get(r["fig_id"], []) if not c["padre"])]
    rng.shuffle(cand)
    demo = None
    for r in cand:
        im = Image.open(RAIZ / r["imagen"]).convert("RGB")
        if im.width < 400:
            continue
        cs = por_fig[r["fig_id"]]
        reducir(im, 1100).save(carpeta / "demo_original.jpg", quality=85)
        dibujar_cajas(reducir(im, 1100), cs).save(carpeta / "demo_cajas.jpg", quality=85)
        recs = []
        for i, c in enumerate(sorted((c for c in cs if not c["padre"]), key=lambda c: int(c["panel"]))):
            nombre_r = f"demo_recorte{i + 1}.jpg"
            cuadrado(recortar(im, c), 260).save(carpeta / nombre_r, quality=88)
            recs.append({"img": f"assets/recortes/{nombre_r}", "tipo": c["tipo"], "panel": c["panel"]})
        demo = {"fig_id": r["fig_id"], "n_paneles": len(recs), "n_cajas": len(cs), "original": "assets/recortes/demo_original.jpg",
                "cajas": "assets/recortes/demo_cajas.jpg", "recortes": recs, "credito": credito_articulo(arts, r["pmcid"])}
        break

    idx = leer(FV / "segmentacion" / "cajas" / "indice_recortes.csv")
    tipos = Counter(r["tipo"] for r in cajas)
    elegibles = [r for r in idx if r["elegible_morfologia"] == "True" and r["clase"]]
    pan = [int(r["paneles"]) for r in fv if r["paneles"].isdigit()]
    return {
        "n_figuras": n, "figuras_con_paneles": len({c["fig_id"] for c in cajas}),
        "paneles": {"n": len(pan), "media": round(sum(pan) / len(pan), 2), "pct1": round(100 * sum(1 for p in pan if p == 1) / len(pan), 1),
                    "pct2": round(100 * sum(1 for p in pan if p == 2) / len(pan), 1), "pct3": round(100 * sum(1 for p in pan if p >= 3) / len(pan), 1)},
        "destinos": destinos, "compuesta_demo": demo, "muestra": muestra,
        "recortes": {"total": len(cajas), "micro": tipos["micro"], "espectro": tipos["espectro"], "otro": tipos["otro"],
                     "elegibles_con_clase": len(elegibles), "articulos_elegibles": len({r["pmcid"] for r in elegibles})},
        "acuerdo": {"coinciden_pie_imagen": round(100 * sum(1 for r in fv if r["acuerdo_con_pie"] == "True") / n, 1),
                    "cola": sum(1 for r in fv if r["estado"] == "cola_revision"),
                    "arbitradas": sum(1 for r in fv if r["estado"] == "aceptada_arbitrada")},
        "fuentes": "modelos/flujo_figuras/figuras_vision.csv, PROGRESO.md, segmentacion/cajas/paneles.csv e indice_recortes.csv, segmentacion/INSTRUCCIONES_CAJAS.md, entrega/ejemplos_presentacion/",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(construir(), ensure_ascii=False, indent=1)[:2000])
