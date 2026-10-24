"""Genera producto/presentacion/datos.js y copia las imagenes que usa la presentacion.

Lee solo archivos congelados del repositorio (curation/v0.1, ext_*.csv, equipo/DECISIONES.md, figuras/, modelos/).
Uso (desde la raiz del repositorio):  python producto/presentacion/construir_datos.py
Despues la presentacion se abre con `python -m http.server 8000` desde producto/ -> http://localhost:8000/presentacion/
(tambien funciona abriendo index.html con doble clic: los datos van en datos.js, no se hace fetch).
"""
import csv
import json
import re
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent
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


def decisiones() -> dict:
    texto = (RAIZ / "equipo" / "DECISIONES.md").read_text(encoding="utf-8")
    secciones, actual, filas = [], None, []
    for linea in texto.splitlines():
        m = re.match(r"## ([A-D])\. (.+)", linea)
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
            filas.append({"id": n, "seccion": actual, "decision": dec, "porque": porque, "evidencia": evid, "estado": estado})
    siguientes = re.findall(r"^\d+\. (.+)$", texto.split("## D.")[1], flags=re.M)
    return {"secciones": [s for s in secciones if s[0] != "D"], "filas": filas, "experimentos": siguientes}


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
# Fuente: modelos/comparacion/METRICAS_CON_IC.md (Héctor, 23 oct): 2.100 figuras, 1.641 artículos, 4 clases,
# 5 particiones por artículo, 1.000 remuestreos por artículo. Cifras EXPLORATORIAS: el ajuste fino en el clúster
# puede sustituirlas (Héctor las entrega el sábado 24 a las 3 pm). Al cambiarlas, volver a ejecutar este script y
# actualizar a mano video/GUION.md y video/GUION_EN.md (lista en producto/presentacion/LEEME.md).
IMAGEN_N_FIGURAS, IMAGEN_N_ARTICULOS = 2100, 1641
IMAGEN_FUENTE = "modelos/comparacion/METRICAS_CON_IC.md"
F1_MAYORITARIA = (0.156, 0.149, 0.162)
F1_IMAGEN = (0.442, 0.416, 0.467)          # modelo del Atlas (SVM con probabilidades); es la cifra principal
F1_MEDIDAS = (0.526, 0.500, 0.553)
F1_FUSION = (0.561, 0.535, 0.585)
DIF_FUSION_MEDIDAS = (0.035, 0.014, 0.056)  # fusión − solo medidas, IC pareado
F1_VARIANTE = (0.475, 0.451, 0.499)         # SVM con otra regla de decisión: variante exploratoria, no titular
VECINO_MISMO_ARTICULO = "2,7 %"
# ══════════════════════════════════════════════════════════════════════════════════════


def c2(v: float) -> str:
    return f"{v:.2f}".replace(".", ",")


def c3(v: float) -> str:
    return f"{v:.3f}".replace(".", ",")


def ic(t: tuple) -> str:
    return f"{c2(t[0])} [{c2(t[1])}–{c2(t[2])}]"


def imagen() -> dict:
    def item(i, nombre, t, **extra):
        return {"id": i, "nombre": nombre, "valor": t[0], "lo": t[1], "hi": t[2], **extra}
    return {
        "items": [
            item("may", "Clase mayoritaria", F1_MAYORITARIA, base=True),
            item("atlas", "Imagen sola (modelo del Atlas)", F1_IMAGEN),
            item("medidas", "Solo medidas (logística)", F1_MEDIDAS),
            item("fusion", "Fusión: imagen + medidas", F1_FUSION, destacado=True),
        ],
        "n_filas": IMAGEN_N_FIGURAS, "n_articulos": IMAGEN_N_ARTICULOS, "metrica": "F1 macro (4 clases)", "fuente": IMAGEN_FUENTE,
        "titulo": f"Solo la imagen: F1 ≈ {c2(F1_IMAGEN[0])}. Imagen + medidas: ≈ {c2(F1_FUSION[0])}",
        "texto": (f"Vectores de ResNet50 y DINOv2 congelados, un clasificador sencillo encima y la <strong>figura completa</strong> "
                  f"(a menudo con varios paneles). <strong>La imagen sola es débil</strong>: F1 {ic(F1_IMAGEN)} frente a {c2(F1_MAYORITARIA[0])} de la línea base. "
                  f"Combinarla con las medidas ayuda un poco: de {c2(F1_MEDIDAS[0])} a {c2(F1_FUSION[0])}. La diferencia es de "
                  f"+{c3(DIF_FUSION_MEDIDAS[0])} [{c3(DIF_FUSION_MEDIDAS[1])}–{c3(DIF_FUSION_MEDIDAS[2])}]: pequeña, pero su intervalo no incluye el cero. "
                  f"El vecino más cercano de una imagen es del mismo artículo solo en el {VECINO_MISMO_ARTICULO} de los casos: no hay fuga por reparto."),
        "aviso": (f"Cifras exploratorias ({IMAGEN_N_FIGURAS:,} figuras; 1.000 remuestreos por artículo).".replace(",", ".")
                  + " El intervalo no incluye la incertidumbre de reentrenar ni la de haber probado varias variantes. "
                  f"Una variante con otra regla de decisión llega a {c3(F1_VARIANTE[0])} [{c3(F1_VARIANTE[1])}–{c3(F1_VARIANTE[2])}]; no se usa como titular. "
                  "El ajuste fino en el clúster puede sustituir estas cifras."),
    }


def figuras() -> list[dict]:
    carpeta = SALIDA / "assets" / "figuras"
    carpeta.mkdir(parents=True, exist_ok=True)
    out = []
    for n in range(1, 11):
        shutil.copyfile(FIGS / f"figura_{n}.png", carpeta / f"figura_{n}.png")
        out.append({"n": n, "archivo": f"assets/figuras/figura_{n}.png", "pie": PIES_FIGURAS[n]})
    return out


def descargas() -> int:
    return sum(1 for r in leer_csv(IMAGENES / "descargas.csv") if r["ok"] == "1")


def main() -> None:
    num = json.loads((CUR / "v0.1" / "RESUMEN_NUMEROS.json").read_text(encoding="utf-8"))["despues"]
    datos = {
        "version": "v0.1",
        "cifras": {"leidos": num["articulos"], "evidencia": num["E1"] + num["E2"], "E1": num["E1"], "E2": num["E2"],
                   "micrografias": num["paneles"], "descriptores": num["descriptores"], "espectros": num["espectros"],
                   "imagenes_descargadas": descargas()},
        "qc": {"fuente": "equipo/qc_carlos/RESUMEN_QC.md", "n_articulos": 20, "asistido_por_ia": True, "filas": [
            {"campo": "Micrografías", "si": 19, "no": 0, "no_comprobable": 1},
            {"campo": "Descriptores", "si": 9, "no": 1, "no_comprobable": 10},
            {"campo": "Espectros", "si": 14, "no": 2, "no_comprobable": 4}]},
        "ejemplos": ejemplos(),
        "decisiones": decisiones(),
        "modelos": modelos(),
        "figuras": figuras(),
    }
    # Aviso de consistencia: equipo/DECISIONES.md (D17) cita las cifras de imagen; deben coincidir con las de arriba.
    for f in datos["decisiones"]["filas"]:
        m = re.search(r"imagen sola F1 ~(\d,\d+)", f["decision"])
        if m and m.group(1) != c2(F1_IMAGEN[0]):
            print(f"AVISO: {f['id']} en DECISIONES.md dice imagen sola F1 ~{m.group(1)}, pero aquí es {c2(F1_IMAGEN[0])}. Pedir a Héctor que lo actualice.")
        m = re.search(r"fusión F1 ~(\d,\d+)", f["decision"])
        if m and m.group(1) != c2(F1_FUSION[0]):
            print(f"AVISO: {f['id']} en DECISIONES.md dice fusión F1 ~{m.group(1)}, pero aquí es {c2(F1_FUSION[0])}. Pedir a Héctor que lo actualice.")
    (SALIDA / "datos.js").write_text("window.DATOS = " + json.dumps(datos, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"datos.js listo: {len(datos['decisiones']['filas'])} decisiones, {len(datos['ejemplos'])} ejemplos, {len(datos['figuras'])} figuras")


if __name__ == "__main__":
    main()
