"""Genera producto/presentacion/datos.js y copia las imagenes que usa la presentacion.

Lee solo archivos congelados del repositorio (curation/v0.1, ext_*.csv, equipo/DECISIONES.md, figuras/, modelos/).
Uso (desde la raiz del repositorio):  python producto/presentacion/construir_datos.py
Despues la presentacion se abre con `python -m http.server 8000` desde producto/ -> http://localhost:8000/presentacion/
(tambien funciona abriendo index.html con doble clic: los datos van en datos.js, no se hace fetch).
"""
import csv
import json
from collections import Counter
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent
sys.path.insert(0, str(SALIDA))
import figuras_recortes  # noqa: E402  (ejemplos de «De la figura al recorte»)
CUR = RAIZ / "curation"
FIGS = RAIZ / "figuras" / "figuras_para_el_video"
IMAGENES = RAIZ / "producto" / "imagenes"

# Ejemplos reales de extraccion: (pmcid, muestra tal como esta en ext_descriptores.csv, figura que se muestra)
EJEMPLOS = [
    ("PMC8986208", "optimized Entacapone-NLCs", "IDRD_A_2058651_F0003_B.jpg"),
    ("PMC12775131", "Amp–AgNPs", "41598_2025_30539_Fig3_HTML.jpg"),
    ("PMC11945751", "Blank liposome (before freeze-drying)", "pharmaceuticals-18-00414-g001.jpg"),
    ("PMC11102914", "Empty HA-ThCs-NPs", "41598_2024_55900_Fig5_HTML.jpg"),
]

PIES_FIGURAS = {
    1: "Cobertura de la base: 1.824 artículos leídos, 1.707 con evidencia.",
    2: "Artículos por año de publicación y clase de portador.",
    3: "Artículos por tipo de portador.",
    4: "Micrografías por tipo de microscopía y clase.",
    5: "Espectros por técnica y clase.",
    6: "Distribución del tamaño de partícula (DLS) por clase.",
    7: "Pares tamaño – potencial zeta.",
    8: "Flujo de construcción de la base.",
    9: "Control de calidad asistido por IA: muestra de 20 artículos.",
    10: "Escalera de modelos de la ronda 1: tamaño (R²) y clase (F1 macro).",
}

NOMBRES_MODELO = {
    "tamano_dummy": "Media global", "tamano_media_clase": "Media por clase", "tamano_B_lineal": "Lineal",
    "tamano_B_ridge": "Ridge", "tamano_B_rf300": "Random Forest 300", "tamano_B_rf500": "Random Forest 500",
    "tamano_B_hgb": "Boosting", "clase4_mayoritaria": "Clase mayoritaria", "clase4_logistica": "Logística",
    "clase4_rf": "Random Forest", "clase4_hgb": "Boosting",
}


def leer_csv(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def limpiar_titulo(t: str) -> str:
    return re.sub(r"</?[a-zA-Z]+>", "", t).strip()


def ejemplos() -> list[dict]:
    arts = {r["pmcid"]: r for r in leer_csv(CUR / "ext_articulos.csv")}
    desc = leer_csv(CUR / "ext_descriptores.csv")
    pan = leer_csv(CUR / "ext_paneles.csv")
    carpeta = SALIDA / "assets" / "ejemplos"
    carpeta.mkdir(parents=True, exist_ok=True)
    out = []
    for pmcid, muestra, imagen in EJEMPLOS:
        fila = next(r for r in desc if r["pmcid"] == pmcid and r["sample"] == muestra)
        art = arts[pmcid]
        panel = next(r for r in pan if r["pmcid"] == pmcid and r["image_file"] == imagen)
        origen = IMAGENES / pmcid / imagen
        if not origen.exists():
            raise SystemExit(f"falta la imagen {origen}: ejecutar modelos/descargar_imagenes.py")
        destino = carpeta / f"{pmcid}.jpg"
        shutil.copyfile(origen, destino)
        out.append({
            "pmcid": pmcid, "titulo": limpiar_titulo(art["title"]), "anio": art["year"], "doi": art["doi_link"],
            "licencia": art["license_epmc"], "portador": art["carrier_type"], "nivel": art["tier"],
            "microscopia": panel["variant"], "figura": panel["fig"], "cita_panel": panel["quote"], "imagen": f"assets/ejemplos/{pmcid}.jpg", "imagen_original": imagen,
            "muestra": fila["sample"], "size_nm": fila["size_nm"], "pdi": fila["pdi"], "zeta_mV": fila["zeta_mV"],
            "medio": fila["medium"], "fuente": fila["source"], "cita": fila["quote"],
        })
    return out


GRUPOS = {
    "Datos": ["D1", "D2", "D3", "D4", "D5", "D7", "D8", "D19", "D20", "D21", "D22"],
    "Figuras": ["D6", "D25", "D26", "D27", "D28"],
    "Evaluación estadística": ["D9", "D11", "D12", "D13", "D29", "D30", "D31", "D32"],
    "Modelos": ["D10", "D14", "D15", "D16", "D17", "D18", "D23", "D24", "D33", "D34"],
}


def decisiones() -> dict:
    texto = (RAIZ / "equipo" / "DECISIONES.md").read_text(encoding="utf-8")
    secciones, actual, filas = [], None, []
    for linea in texto.splitlines():
        m = re.match(r"## ([A-E])\. (.+)", linea)
        if m:
            actual = f"{m.group(1)}. {m.group(2)}"
            secciones.append(actual)
            continue
        if linea.startswith("| D") and actual:
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            if len(celdas) == 5:
                n, dec, porque, evid, estado = celdas
            elif len(celdas) == 4:
                n, dec, porque, estado = celdas
                evid = ""
            else:
                continue
            grupo = next((g for g, ids in GRUPOS.items() if n in ids), None)
            if grupo is None:
                raise SystemExit(f"La decisión {n} no tiene grupo en GRUPOS de construir_datos.py")
            filas.append({"id": n, "seccion": actual, "grupo": grupo, "decision": dec, "porque": porque, "evidencia": evid, "estado": estado})
    sin_fila = [i for ids in GRUPOS.values() for i in ids if i not in {f["id"] for f in filas}]
    if sin_fila:
        raise SystemExit(f"GRUPOS lista decisiones que no están en DECISIONES.md: {sin_fila}")
    siguientes = re.findall(r"^\d+\. (.+)$", texto.split("## D.")[1].split("## E.")[0], flags=re.M)
    # El ajuste fino ya se hizo (D23) y el contacto con el CNCA no es un experimento: quedan los pendientes reales.
    pendientes = [s for s in siguientes if "ajuste fino" not in s.lower() and "CNCA" not in s]
    return {"grupos": list(GRUPOS), "filas": filas, "experimentos": pendientes}


def modelos() -> dict:
    filas = leer_csv(FIGS / "datos" / "figura_10.csv")
    tam, cla = [], []
    for r in filas:
        item = {"id": r["modelo"], "nombre": NOMBRES_MODELO[r["modelo"]], "valor": round(float(r["valor"]), 3),
                "lo": round(float(r["ic_inf"]), 3), "hi": round(float(r["ic_sup"]), 3),
                "base": r["modelo"] in ("tamano_dummy", "tamano_media_clase", "clase4_mayoritaria")}
        (tam if r["tarea"] == "Tamaño" else cla).append(item)
    n_tam = filas[0]
    return {
        "tamano": {"items": tam, "n_filas": int(n_tam["n_filas"]), "n_articulos": int(n_tam["n_articulos"]),
                   "fuente": "modelos/tabular/REPORTE_TABULAR.md · figura 10", "metrica": "R² de log10(tamaño)"},
        "clase": {"items": cla, "n_filas": int(filas[-1]["n_filas"]), "n_articulos": int(filas[-1]["n_articulos"]),
                  "fuente": "modelos/tabular/REPORTE_TABULAR.md · figura 10", "metrica": "F1 macro (4 clases)"},
        "imagen": imagen(),
    }


# ══════════════════════════════════════════════════════════════════════════════════════
# ÚNICO SITIO PARA CAMBIAR LAS CIFRAS DEL MODELO DE IMAGEN (presentación). Valor, IC 95 % inferior, superior.
# Fuentes (Héctor, 23 oct): modelos/comparacion/METRICAS_CON_IC.md (congelados) y METRICAS_AJUSTE_FINO_CON_IC.md
# (ajuste fino en GPU): 2.100 figuras, 1.641 artículos, 4 clases, 5 particiones por artículo, 1.000 remuestreos por
# artículo. Cifras EXPLORATORIAS. Si Héctor entrega cifras nuevas (sábado 24, 3 pm), cambiarlas aquí, volver a
# ejecutar este script y actualizar a mano video/GUION.md, video/GUION_EN.md, producto/web_contenido/modelos_y_limitaciones.md
# y la Figura 11 (lista en producto/presentacion/LEEME.md).
IMAGEN_N_FIGURAS, IMAGEN_N_ARTICULOS = 2100, 1641
IMAGEN_FUENTE = "modelos/comparacion/METRICAS_CON_IC.md y METRICAS_AJUSTE_FINO_CON_IC.md"
F1_MAYORITARIA = (0.156, 0.149, 0.162)
F1_IMAGEN = (0.442, 0.416, 0.467)          # vectores congelados, modelo del Atlas (SVM con probabilidades): cifra principal
F1_AJUSTE_FINO = (0.460, 0.437, 0.484)     # ajuste fino de ResNet50 y DINOv2 (promedio), 10 épocas, GPU
F1_MEDIDAS = (0.526, 0.500, 0.553)
F1_FUSION = (0.561, 0.535, 0.585)          # vectores congelados + medidas
F1_FUSION_TARDIA = (0.580, 0.554, 0.603)   # ajuste fino + medidas, peso fijo 50/50
DIF_FUSION_MEDIDAS = (0.035, 0.014, 0.056)         # fusión (congelados) − solo medidas, IC pareado
DIF_FUSION_TARDIA_MEDIDAS = (0.054, 0.032, 0.077)  # fusión tardía − solo medidas
DIF_AJUSTE_VS_CONGELADO = (0.018, -0.008, 0.045)   # ajuste fino − congelados: el intervalo incluye el cero
F1_VARIANTE = (0.475, 0.451, 0.499)        # SVM con otra regla de decisión: variante exploratoria, no titular
VECINO_MISMO_ARTICULO = "2,7 %"
# ══════════════════════════════════════════════════════════════════════════════════════


def miles(n) -> str:
    return f"{int(round(n)):,}".replace(",", ".")


def c2(v: float) -> str:
    return f"{v:.2f}".replace(".", ",")


def c3(v: float) -> str:
    return f"{v:.3f}".replace(".", ",").replace("-", "−")


def ic(t: tuple) -> str:
    return f"{c2(t[0])} [{c2(t[1])}–{c2(t[2])}]"


def dif(t: tuple) -> str:
    return f"{'+' if t[0] >= 0 else ''}{c3(t[0])} [{'+' if t[1] >= 0 else ''}{c3(t[1])}, {'+' if t[2] >= 0 else ''}{c3(t[2])}]"


def imagen() -> dict:
    def item(i, nombre, t, **extra):
        return {"id": i, "nombre": nombre, "valor": t[0], "lo": t[1], "hi": t[2], **extra}
    return {
        "items": [
            item("may", "Clase mayoritaria", F1_MAYORITARIA, base=True),
            item("atlas", "Imagen sola (vectores congelados)", F1_IMAGEN),
            item("ajuste", "Imagen sola (ajuste fino en GPU)", F1_AJUSTE_FINO),
            item("medidas", "Solo medidas (logística)", F1_MEDIDAS),
            item("fusion", "Fusión: congelados + medidas", F1_FUSION),
            item("fusion_tardia", "Fusión tardía: ajuste fino + medidas", F1_FUSION_TARDIA, destacado=True),
        ],
        "n_filas": IMAGEN_N_FIGURAS, "n_articulos": IMAGEN_N_ARTICULOS, "metrica": "F1 macro (4 clases) · línea base v0.1 (figura completa)", "fuente": IMAGEN_FUENTE,
        "titulo": f"Solo la imagen: F1 ≈ {c2(F1_IMAGEN[0])}. Con las medidas: ≈ {c2(F1_FUSION_TARDIA[0])}",
        "texto": (f"Vectores de ResNet50 y DINOv2 congelados, un clasificador sencillo encima y la <strong>figura completa</strong> "
                  f"(a menudo con varios paneles). <strong>La imagen sola es débil</strong>: F1 {ic(F1_IMAGEN)} frente a {c2(F1_MAYORITARIA[0])} de la línea base. "
                  f"Probamos también <strong>ajustar las redes completas en GPU</strong>: tampoco mejora de forma clara ({ic(F1_AJUSTE_FINO)}; diferencia "
                  f"{dif(DIF_AJUSTE_VS_CONGELADO)}, su intervalo incluye el cero) y DINOv2 sobreajusta. <strong>El límite está en las imágenes, no en la arquitectura.</strong> "
                  f"Combinar la imagen con las medidas ayuda un poco: con los vectores congelados sube de {c2(F1_MEDIDAS[0])} a {c2(F1_FUSION[0])}, "
                  f"y la fusión tardía con el ajuste fino llega a <strong>{ic(F1_FUSION_TARDIA)}</strong>, {dif(DIF_FUSION_TARDIA_MEDIDAS)} sobre las medidas solas (intervalo sin el cero). "
                  f"El vecino más cercano de una imagen es del mismo artículo solo en el {VECINO_MISMO_ARTICULO} de los casos: no hay fuga por reparto."),
        "aviso": (f"Cifras exploratorias ({IMAGEN_N_FIGURAS:,} figuras; 1.000 remuestreos por artículo).".replace(",", ".")
                  + " El intervalo no incluye la incertidumbre de reentrenar ni la de haber probado varias variantes. "
                  f"La fusión tardía usa un peso fijo 50/50 elegido de antemano. Una variante con otra regla de decisión llega a "
                  f"{c3(F1_VARIANTE[0])} [{c3(F1_VARIANTE[1])}–{c3(F1_VARIANTE[2])}]; no se usa como titular."),
    }


def figuras() -> list[dict]:
    carpeta = SALIDA / "assets" / "figuras"
    carpeta.mkdir(parents=True, exist_ok=True)
    out = []
    carpeta9 = carpeta / "figura_9.png"
    if carpeta9.exists():  # la Figura 9 (muestra de 20 artículos) se retiró de la presentación
        carpeta9.unlink()
    for n in (1, 2, 3, 4, 5, 6, 7, 8, 10):
        shutil.copyfile(FIGS / f"figura_{n}.png", carpeta / f"figura_{n}.png")
        out.append({"n": n, "archivo": f"assets/figuras/figura_{n}.png", "pie": PIES_FIGURAS[n]})
    return out


def _num(s: str) -> float:
    return float(s.replace(".", "").replace(",", ".")) if re.fullmatch(r"\d{1,3}(\.\d{3})+", s) else float(s.replace(",", "."))


def calidad_figuras() -> dict:
    """Cifras del control de calidad de figuras, leídas de los archivos (no de memoria). Falla si no las encuentra."""
    fv = RAIZ / "modelos" / "flujo_figuras"
    n_figuras = sum(1 for _ in leer_csv(fv / "figuras_vision.csv"))
    cajas = leer_csv(fv / "segmentacion" / "cajas" / "paneles.csv")
    indice = leer_csv(fv / "segmentacion" / "cajas" / "indice_recortes.csv")
    elegibles = [r for r in indice if r["elegible_morfologia"] == "True" and r["clase"]]
    estado = (RAIZ / "equipo" / "ESTADO_FIGURAS_24OCT_NOCHE.md").read_text(encoding="utf-8")
    prog = (fv / "PROGRESO.md").read_text(encoding="utf-8")
    m_aud = re.search(r"(\d+)/(\d+) \(([\d,]+) %\) en número de paneles", estado)
    m_iou = re.search(r"\((?:Héctor, )?(\d+) figuras, (\d+) paneles\) en `segmentacion/anotador/`; Haiku vs humano: IoU (0,\d+)", estado)
    m_cls = re.search(r"Figuras clasificadas: \*\*(\d+)\*\* de (\d+)", prog)
    if not (m_aud and m_iou and m_cls):
        raise SystemExit("No se encontraron las cifras de auditoría/IoU/clasificación en ESTADO_FIGURAS_24OCT_NOCHE.md o PROGRESO.md")
    assert int(m_cls.group(1)) == n_figuras, "PROGRESO.md y figuras_vision.csv no coinciden"
    carpeta = SALIDA / "assets" / "figuras_calidad"
    carpeta.mkdir(parents=True, exist_ok=True)
    for idioma in ("es", "en"):
        shutil.copyfile(RAIZ / "figuras" / f"flujo_calidad_figuras_{idioma}.png", carpeta / f"flujo_calidad_figuras_{idioma}.png")
    return {
        "n_figuras": n_figuras, "n_recortes": len(cajas), "n_recortes_clase": len(elegibles),
        "n_articulos_recortes_clase": len({r["pmcid"] for r in elegibles}),
        "auditoria": {"bien": int(m_aud.group(1)), "total": int(m_aud.group(2)), "pct": m_aud.group(3)},
        "iou": {"valor": m_iou.group(3), "n_figuras": int(m_iou.group(1)), "n_paneles": int(m_iou.group(2))},
        "imagen": {"es": "assets/figuras_calidad/flujo_calidad_figuras_es.png", "en": "assets/figuras_calidad/flujo_calidad_figuras_en.png"},
        "fuentes": "modelos/flujo_figuras/PROGRESO.md, figuras_vision.csv, segmentacion/cajas/paneles.csv, equipo/ESTADO_FIGURAS_24OCT_NOCHE.md",
    }


def descriptores_v03() -> dict:
    t = (RAIZ / "modelos" / "descriptores_v02" / "DESCRIPTORES_V03.md").read_text(encoding="utf-8")
    m = re.search(r"usable_v03: (\d+) de (\d+)", t)
    a = re.search(r"Filas: (\d+) · auditadas: (\d+)", t)
    if not (m and a):
        raise SystemExit("No se encontraron las cifras en DESCRIPTORES_V03.md")
    return {"usables": int(m.group(1)), "filas": int(m.group(2)), "auditadas": int(a.group(2)),
            "fuente": "modelos/descriptores_v02/DESCRIPTORES_V03.md"}


def recortes() -> dict:
    """Análisis preliminar con recortes de panel (cuaderno 04). Muestras distintas de las de la tabla v0.1: no mezclar."""
    comp = RAIZ / "modelos" / "comparacion"
    a = json.loads((comp / "ANALISIS_04_RECORTES.json").read_text(encoding="utf-8"))
    f = json.loads((comp / "ANALISIS_FUSION_04.json").read_text(encoding="utf-8"))

    def r3(v):
        return round(v, 3)
    imagen = []
    for clave, nombre in (("resnet50", "ResNet50"), ("dinov2_vits14", "DINOv2")):
        d = a[clave]
        imagen.append({"nombre": nombre, "recortes_f1": r3(d["recortes"]["f1"]), "mismas_vistas_f1": r3(d["control_mismas_vistas"]["f1"]),
                       "completa_f1": r3(d["figura_completa_03"]["f1"]), "dif_f1": r3(d["dif_f1"]),
                       "dif_f1_ic": [r3(x) for x in d["diferencia_IC95"]["f1"]],
                       "dif_mismas_vistas_f1": r3(d["control_mismas_vistas"]["f1"] - d["figura_completa_03"]["f1"]),
                       "dif_mismas_vistas_acc": r3(d["control_mismas_vistas"]["acc"] - d["figura_completa_03"]["acc"])})
    p = a["promedio"]
    nombres = {"medidas": "Solo medidas (logística)", "imagen_03": "Imagen, figura completa", "imagen_04": "Imagen, recortes de panel",
               "fusion_03": "Fusión medidas + figura completa", "fusion_04": "Fusión medidas + recortes"}
    fusion = [{"nombre": nombres[k], "acc": r3(v["acc"]), "acc_bal": r3(v["acc_bal"]), "f1": r3(v["f1"])} for k, v in f["modelos"].items()]
    difs = [{"nombre": k.replace("imagen_04", "imagen recortes").replace("imagen_03", "imagen completa").replace("fusion_04", "fusión recortes")
             .replace("fusion_03", "fusión completa").replace("medidas", "solo medidas"), "f1": r3(v["f1"]), "ic": [r3(x) for x in v["IC95"]["f1"]]}
            for k, v in f["diferencias"].items()]
    return {"imagen": {"n_articulos": a["resnet50"]["n_articulos"], "filas": imagen,
                       "promedio": {"recortes_f1": r3(p["recortes"]["f1"]), "completa_f1": r3(p["figura_completa_03"]["f1"]),
                                    "dif_f1": r3(p["recortes"]["f1"] - p["figura_completa_03"]["f1"]),
                                    "dif_ic": [r3(x) for x in p["diferencia_IC95"]["f1"]]},
                       "vistas_03": round(a["resnet50"]["control_mismas_vistas"]["vistas_medias_03"], 2),
                       "vistas_04": round(a["resnet50"]["control_mismas_vistas"]["vistas_medias_04"], 2)},
            "fusion": {"n_articulos": f["n_articulos"], "linea_base_acc": r3(f["linea_base_mayoritaria_acc"]), "filas": fusion, "difs": difs},
            "fuente": "modelos/comparacion/ANALISIS_04_RECORTES.md y ANALISIS_FUSION_04.md"}


def nffa() -> dict:
    """Experimento NFFA (cuaderno 06): cifras de metricas_06.json y lectura de ANALISIS_06_NFFA.md. Falla si no las encuentra."""
    j = json.loads((RAIZ / "modelos" / "comparacion" / "entrada_kabre" / "06_nffa" / "metricas_06.json").read_text(encoding="utf-8"))
    md = (RAIZ / "modelos" / "comparacion" / "ANALISIS_06_NFFA.md").read_text(encoding="utf-8")
    m_ens = re.search(r"\+(0,\d+) de exactitud y \+(0,\d+) de F1 macro frente a una semilla", md)
    m_sem = re.search(r"Por semilla, B − A = ([^.]+)\.", md)
    if not (m_ens and m_sem):
        raise SystemExit("No se encontraron las cifras de ensamble o por semilla en ANALISIS_06_NFFA.md")
    nombres = {"A": "A · línea base (LVD → recortes)", "B": "B · NFFA antes de los recortes", "C": "C · control (etiquetas de NFFA mezcladas)"}
    arms = [{"id": a["brazo"], "nombre": nombres[a["brazo"]], "acc": a["acc_media"], "acc_sd": a["acc_sd"], "f1": a["f1_media"], "f1_sd": a["f1_sd"],
             "f1_ens": a["f1_ensamble"]} for a in j["tabla"]]
    difs = [{"nombre": k, "f1": v["f1"], "ic": v["IC95"]["f1"]} for k, v in j["diferencias"].items()]
    return {"n_articulos": j["articulos_comunes"], "brazos": arms, "difs": difs, "por_semilla_BA": m_sem.group(1),
            "ens_acc": m_ens.group(1), "ens_f1": m_ens.group(2), "veredicto": j["veredicto"],
            "fuente": "modelos/comparacion/ANALISIS_06_NFFA.md y entrada_kabre/06_nffa/metricas_06.json"}


def modelo_final() -> dict:
    card = json.loads((RAIZ / "modelos" / "modelo_final" / "02_onnx" / "modelo_card.json").read_text(encoding="utf-8"))
    ref = card["desempeno_de_referencia_validacion_cruzada"]
    idx = leer_csv(RAIZ / "modelos" / "flujo_figuras" / "segmentacion" / "cajas" / "indice_recortes.csv")
    por_art = {r["pmcid"]: r["clase"] for r in idx if r["elegible_morfologia"] == "True" and r["clase"]}
    mayor = max(Counter(por_art.values()).values())
    base_acc = mayor / len(por_art)  # exactitud de la clase mayoritaria con los mismos artículos (492 de 1.114)
    n04 = len(por_art)
    m = re.search(r"(\d+) recortes de panel de micrograf[ií]a de part[ií]culas de (\d+) art[ií]culos", card["entrenamiento"]["datos"])
    if not m:
        raise SystemExit("No se encontraron los recortes de entrenamiento en la ficha del modelo")
    return {"n_recortes": int(m.group(1)), "n_articulos_entrenamiento": int(m.group(2)), "n_articulos": ref["articulos"], "exactitud": ref["exactitud"],
            "exactitud_bal": round(ref["exactitud_balanceada"], 3), "f1": round(ref["f1_macro"], 3), "linea_base": round(base_acc, 3), "n_linea_base": n04, "mayoritaria_n": mayor,
            "validacion": ref["validacion"], "fuente": "modelos/modelo_final/LEEME.md y 02_onnx/modelo_card.json"}


PIES_MODELOS = {
    "hero": {
        "es": "Fuentes: modelos/flujo_figuras/figuras_vision.csv e indice_recortes.csv. Solo figuras con paneles (compuestas y parejas con micrografía o espectro útil); las simples y las de espectros superpuestos no se recortan. La clase es la del ARTÍCULO, no la del recorte. *Validación cruzada por artículo, ensamble de 3 semillas de DINOv2 (modelos/comparacion/ANALISIS_06_NFFA.md); exploratorio; línea base de la clase mayoritaria: exactitud 0,442.",
        "en": "Sources: modelos/flujo_figuras/figuras_vision.csv and indice_recortes.csv. Only figures with panels (composite and pair figures with a micrograph or a clean spectrum); simple figures and overlaid-spectra figures are not cropped. The class is the ARTICLE's, not the crop's. *Article-level cross-validation, 3-seed DINOv2 ensemble (modelos/comparacion/ANALISIS_06_NFFA.md); exploratory; majority-class baseline: accuracy 0.442."},
    "recortes": {
        "es": "n = 1.112 artículos en (a) y las 3 primeras filas de (b); n = 786 en las 2 últimas (artículos con figura completa, recortes y medidas). IC 95 % por bootstrap de artículos (2.000). Los puntos huecos son el promedio de 200 sorteos sin IC. Fuentes: modelos/comparacion/ANALISIS_04_RECORTES.md y ANALISIS_FUSION_04.md. Con el mismo número de vistas por artículo la ventaja de los recortes se reduce (control); el IC de «fusión 04 − fusión 03» incluye el 0.",
        "en": "n = 1,112 articles in (a) and the first three rows of (b); n = 786 in the last two (articles with a full figure, crops and measurements). 95% CI by article bootstrap (2,000). Hollow points are the mean of 200 draws, without CI. Sources: modelos/comparacion/ANALISIS_04_RECORTES.md and ANALISIS_FUSION_04.md. With the same number of views per article the advantage of crops shrinks (control); the CI of “fusion 04 − fusion 03” includes 0."},
    "nffa": {
        "es": "1.114 artículos; 5 particiones por artículo; 3 semillas por brazo; la etapa 1 (NFFA, 7 morfologías, 8.204 teselas, 96,8 % de exactitud interna) corrió una vez. IC 95 % por bootstrap de artículos (2.000) sobre las probabilidades promediadas entre semillas. Resultado: B no supera a A (IC incluye 0); mezclar las etiquetas daña (C − A). Fuente: modelos/comparacion/ANALISIS_06_NFFA.md. Criterio fijado antes de ver los resultados.",
        "en": "1,114 articles; 5 article-level splits; 3 seeds per arm; stage 1 (NFFA, 7 morphologies, 8,204 tiles, 96.8% internal accuracy) ran once. 95% CI by article bootstrap (2,000) on probabilities averaged across seeds. Result: B does not beat A (CI includes 0); shuffling the labels hurts (C − A). Source: modelos/comparacion/ANALISIS_06_NFFA.md. Criterion fixed before seeing the results."},
}
FIGURAS_MODELOS = {"hero": "fig_hero_flujo", "recortes": "fig_modelos_2", "nffa": "fig_modelos_3"}


def figuras_modelos() -> dict:
    carpeta = SALIDA / "assets" / "figuras_modelos"
    carpeta.mkdir(parents=True, exist_ok=True)
    out = {}
    for clave, base in FIGURAS_MODELOS.items():
        d = {}
        for i in ("es", "en"):
            shutil.copyfile(RAIZ / "figuras" / "modelos" / f"{base}_{i}.png", carpeta / f"{base}_{i}.png")
            d[i] = f"assets/figuras_modelos/{base}_{i}.png"
        out[clave] = {**d, "pie": PIES_MODELOS[clave]}
    return out


def descargas() -> int:
    return sum(1 for r in leer_csv(IMAGENES / "descargas.csv") if r["ok"] == "1")


def sellar_version() -> None:
    """Añade ?v=<hash> a estilo.css, datos.js y app.js en index.html, para que el navegador no use copias viejas en caché."""
    import hashlib
    ruta = SALIDA / "index.html"
    html = ruta.read_text(encoding="utf-8")
    for nombre in ("estilo.css", "datos.js", "app.js"):
        h = hashlib.md5((SALIDA / nombre).read_bytes()).hexdigest()[:8]
        html = re.sub(rf'(["\']){re.escape(nombre)}(\?v=[0-9a-f]+)?(["\'])', rf'\1{nombre}?v={h}\3', html)
    ruta.write_text(html, encoding="utf-8")


def main() -> None:
    num = json.loads((CUR / "v0.1" / "RESUMEN_NUMEROS.json").read_text(encoding="utf-8"))["despues"]
    datos = {
        "version": "v0.1",
        "cifras": {"leidos": num["articulos"], "evidencia": num["E1"] + num["E2"], "E1": num["E1"], "E2": num["E2"],
                   "micrografias": num["paneles"], "descriptores": num["descriptores"], "espectros": num["espectros"],
                   "imagenes_descargadas": descargas()},
        # La muestra de 20 artículos (equipo/qc_carlos/RESUMEN_QC.md) ya no es el eje: queda como una frase en «Limitaciones».
        # Las cifras con recortes de panel, el modelo final y NFFA ya están en los archivos de modelos/comparacion y modelos/modelo_final.
        "calidad_figuras": calidad_figuras(),
        "descriptores_v03": descriptores_v03(),
        "figuras_recortes": figuras_recortes.construir(),
        "recortes": recortes(),
        "nffa": nffa(),
        "modelo_final": modelo_final(),
        "figuras_modelos": figuras_modelos(),
        "ejemplos": ejemplos(),
        "decisiones": decisiones(),
        "modelos": modelos(),
        "figuras": figuras(),
    }
    MF, NF, RCs = datos["modelo_final"], datos["nffa"], datos["recortes"]
    datos["siguientes_hecho"] = [
        f"**Recortes de panel:** {miles(datos['figuras_recortes']['recortes']['total'])} recortes, {miles(datos['figuras_recortes']['recortes']['elegibles_con_clase'])} de micrografías de partículas con clase (preliminar: su ventaja viene en buena parte de más vistas por artículo).",
        f"**Ajuste fino en GPU** de ResNet50 y DINOv2: F1 {ic(F1_AJUSTE_FINO)}, sin mejora clara frente a los vectores congelados ({c2(F1_IMAGEN[0])}).",
        f"**Experimento NFFA:** no mejoró (B − A = {dif((NF['difs'][0]['f1'], NF['difs'][0]['ic'][0], NF['difs'][0]['ic'][1]))}).",
        f"**Modelo final:** DINOv2 con ensamble de 3 semillas; exactitud {c3(MF['exactitud'])} y F1 {c3(MF['f1'])} por validación cruzada por artículo (n = {miles(MF['n_articulos'])}).",
        "**Demo «sube tu micrografía»** en el navegador, con ONNX.",
    ]
    datos["siguientes"] = [
        f"**Recoger más figuras por artículo** (el modelo con figura completa ve ≈ {c2(datos['recortes']['imagen']['vistas_03'])} por artículo; con recortes, ≈ {c2(datos['recortes']['imagen']['vistas_04'])}).",
        "**Entrenar sin una clase** (sin inorgánicos, sin poliméricas…): mide cuánto depende el modelo de cada clase y si generaliza.",
        "**Modelos específicos por clase**, con espectros de referencia (seminario 3).",
        "**Validación externa**, con artículos nuevos.",
        "**Extraer más condiciones de preparación** (proporciones, métodos), que hoy faltan en la base.",
        "**Revisión humana a ciegas** de una muestra de extracciones.",
    ]
    # Aviso de consistencia: equipo/DECISIONES.md (D17) cita las cifras de imagen; deben coincidir con las de arriba.
    for f in datos["decisiones"]["filas"]:
        for patron, esperado, nombre in [(r"imagen sola F1 ~?(\d,\d\d)", F1_IMAGEN, "imagen sola"), (r"imagen \+ medidas ~?(\d,\d\d)", F1_FUSION, "imagen + medidas"),
                                         (r"ajuste fino ~?(\d,\d\d)", F1_AJUSTE_FINO, "ajuste fino"), (r"fusión tardía[^;)]*? ~?(\d,\d\d)", F1_FUSION_TARDIA, "fusión tardía")]:
            m = re.search(patron, f["decision"])
            if m and m.group(1) != c2(esperado[0]):
                print(f"AVISO: {f['id']} en DECISIONES.md dice {nombre} {m.group(1)}, pero aquí es {c2(esperado[0])}. Pedir a Héctor que lo actualice.")
    (SALIDA / "datos.js").write_text("window.DATOS = " + json.dumps(datos, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    sellar_version()
    print(f"datos.js listo: {len(datos['decisiones']['filas'])} decisiones, {len(datos['ejemplos'])} ejemplos, {len(datos['figuras'])} figuras")


if __name__ == "__main__":
    main()
