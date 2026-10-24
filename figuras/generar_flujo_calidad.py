"""Diagrama del flujo de control de calidad de figuras (estilo artículo, como la Fig. 1 de EXSCLAIM!).
Genera figuras/flujo_calidad_figuras_{es,en}.{png,svg,pdf}. Uso: python figuras/generar_flujo_calidad.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parent
INK, MUT, ACC, BG, EDGE = "#1d2427", "#5b6a70", "#0f6e6a", "#f3f6f6", "#3b4d52"
CHIP = {"simple": "#0f6e6a", "pareja": "#1e88e5", "compuesta": "#d81b60", "superpuesto": "#ef8f00", "excluir": "#8a979c"}

T = {
 "es": {
  "title": "Nano2Predict · de la literatura a un conjunto de datos de paneles verificados",
  "c1": "1 · Literatura", "c2": "2 · Base v0.1 (congelada)", "c3": "3 · Control de calidad de figuras", "c4": "4 · Salida",
  "art": "1.707 artículos\nEurope PMC · CC BY\nnanoportadores\n(sin virus como vector)", "txt": "Texto y pies\nde figura", "fig": "Figuras\noriginales",
  "d1": "Descriptores\nDLS · PDI · ζ", "d2": "Espectros\nFTIR · XRD · UV-vis · EDS…", "d3": "Micrografías\nTEM · SEM · AFM…",
  "foot2": "Cada dato con su cita textual,\nverificada por código (≥ 90 %)",
  "s": [("Tipología por pie", "paneles (a, b, c…), plurales,\ncurvas superpuestas"),
        ("Clasificación visual", "hojas de contacto; Claude y Codex\nsin ver el pie; doble lectura parcial"),
        ("Imagen ↔ pie", "coinciden → aceptada\nno coinciden → cola humana"),
        ("Cinco bases", ""),
        ("Separación de paneles", "cajas sobre cuadrícula;\ncontrol geométrico;\nacuerdo de dos modelos"),
        ("Clasificador por recorte", "DINOv2 + etiquetas humanas;\nfragmento del pie por panel"),
        ("Verificación humana", "anotador de paneles (verdad de referencia) · muestra de 200 paneles con IC 95 % (Wilson)")],
  "chips": ["simple", "pareja", "compuesta", "superpuesto", "excluir"],
  "principio": "Principio: precisión antes que recall. Se descarta lo dudoso; lo aceptado tiene doble evidencia (pie + imagen).",
  "o1": "Paneles curados", "o1d": "micrografía ·\nespectro limpio\nid · clase · técnica\npie · caja", "o2": "Modelos de\nclase y tamaño", "o3": "Atlas web\ny demo",
  "ref": "Metodología inspirada en EXSCLAIM!, MedICaT y FigEx2",
 },
 "en": {
  "title": "Nano2Predict · from the literature to a dataset of verified panels",
  "c1": "1 · Literature", "c2": "2 · Base v0.1 (frozen)", "c3": "3 · Figure quality control", "c4": "4 · Output",
  "art": "1,707 articles\nEurope PMC · CC BY\nnanocarriers\n(no viral vectors)", "txt": "Text and\nfigure captions", "fig": "Original\nfigures",
  "d1": "Descriptors\nDLS · PDI · ζ", "d2": "Spectra\nFTIR · XRD · UV-vis · EDS…", "d3": "Micrographs\nTEM · SEM · AFM…",
  "foot2": "Every datum with its verbatim quote,\nverified by code (≥ 90 %)",
  "s": [("Caption typology", "panel labels (a, b, c…), plurals,\noverlaid curves"),
        ("Visual classification", "contact sheets; Claude and Codex\nblind to the caption; partial double reading"),
        ("Image ↔ caption", "agree → accepted\ndisagree → human queue"),
        ("Five databases", ""),
        ("Panel separation", "boxes on a grid;\ngeometric checks;\ntwo-model agreement"),
        ("Per-crop classifier", "DINOv2 + human labels;\ncaption fragment per panel"),
        ("Human verification", "panel annotator (ground truth) · 200-panel sample with 95 % CI (Wilson)")],
  "chips": ["single", "pair", "compound", "overlaid", "exclude"],
  "principio": "Principle: precision over recall. Doubtful items are dropped; accepted items carry double evidence (caption + image).",
  "o1": "Curated panels", "o1d": "micrograph ·\nclean spectrum\nid · class · technique\ncaption · box", "o2": "Class and size\nmodels", "o3": "Web Atlas\nand demo",
  "ref": "Methodology inspired by EXSCLAIM!, MedICaT and FigEx2",
 },
}


def caja(ax, x, y, w, h, fc="white", ec=EDGE, lw=1.6, r=1.2, z=1, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z, ls=ls))


def texto(ax, x, y, s, size=9, w="normal", c=INK, ha="center", va="center", z=5, style="normal"):
    ax.text(x, y, s, fontsize=size, fontweight=w, color=c, ha=ha, va=va, zorder=z, fontstyle=style, linespacing=1.25)


def flecha(ax, x0, y0, x1, y1, c=EDGE, lw=1.8, rad=0.0):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=16, lw=lw, color=c, zorder=4, connectionstyle=f"arc3,rad={rad}"))


def numero(ax, x, y, n):
    ax.add_patch(Circle((x, y), 1.25, fc=ACC, ec="white", lw=1.2, zorder=6))
    texto(ax, x, y, str(n), 10.5, "bold", "white", z=7)


def dibujar(lang):
    t = T[lang]
    fig, ax = plt.subplots(figsize=(20, 10.8)); ax.set_xlim(0, 100); ax.set_ylim(0, 54); ax.axis("off")
    texto(ax, 50, 52.3, t["title"], 16, "bold")
    for x, w, ttl in [(1, 20, t["c1"]), (24, 20, t["c2"]), (47, 37, t["c3"]), (86.6, 12.4, t["c4"])]:
        caja(ax, x, 7.5, w, 41.5, fc=BG, ec=EDGE, lw=2, r=1.8)
        texto(ax, x + w / 2, 46.9, ttl, 12.5, "bold")
    for x0, x1 in [(21, 24), (44, 47), (84, 86.6)]:
        flecha(ax, x0 + 0.1, 28, x1 - 0.1, 28, lw=2.4)

    # 1 · literatura
    caja(ax, 3, 31, 16, 12, fc="white", ec=ACC); texto(ax, 11, 37, t["art"], 9.5, "bold")
    for k in range(3):                                                       # pila de "artículos"
        ax.add_patch(Rectangle((14 + k * 0.7, 40.2 - k * 0.7), 3.2, 3.6, fc="#e5eceb", ec=EDGE, lw=0.8, zorder=2))
    for xx, s, yy in [(7, t["txt"], 18), (15, t["fig"], 18)]:
        ax.add_patch(Ellipse((xx, yy), 7.4, 7.4, fc="white", ec=EDGE, lw=1.6, zorder=3)); texto(ax, xx, yy, s, 8.2)
    flecha(ax, 9.5, 31, 7.6, 21.8); flecha(ax, 12.5, 31, 14.4, 21.8)
    for k in range(6):                                                       # mini composición de paneles
        ax.add_patch(Rectangle((5.5 + (k % 3) * 2.4, 9.5 + (k // 3) * 2.4), 2.1, 2.1, fc="#cfd8da", ec=EDGE, lw=0.7, zorder=2))
    texto(ax, 15, 11, "…", 14)

    # 2 · base v0.1
    for k, key in enumerate(["d1", "d2", "d3"]):
        caja(ax, 25.5, 35.5 - k * 9.5, 17, 7.5, fc="white", ec=ACC)
        texto(ax, 34, 39.2 - k * 9.5, t[key], 9.5, "bold")
    texto(ax, 34, 12, t["foot2"], 8.6, c=MUT, style="italic")

    # 3 · control de calidad (2 columnas × 3 filas + fila final)
    cols, rows = [48.5, 67.0], [37.0, 26.5, 16.0]
    pos = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 2), (1, 2)]      # serpentina: 1→2 ⟶, 2→3 ↓, 3→4 ⟵, 4→5 ↓, 5→6 ⟶, 6→7 ↓
    centros = []
    for i, (c, r) in enumerate(pos):
        x, y = cols[c], rows[r]
        caja(ax, x, y, 16.5, 8.2, fc="white", ec=ACC, lw=1.8)
        numero(ax, x + 1.6, y + 6.6, i + 1)
        texto(ax, x + 9.4, y + 6.5, t["s"][i][0], 10.3, "bold")
        if i != 3:
            texto(ax, x + (7.2 if i == 4 else 8.25), y + 3.0, t["s"][i][1], 8.0 if i == 4 else 8.2, c=INK)
        centros.append((x, y))
    # chips de las cinco bases (paso 4)
    x, y = centros[3]
    for k, (name, col) in enumerate(zip(t["chips"], CHIP.values())):
        cx, cy = x + 2.9 + (k % 3) * 4.9 + (0 if k < 3 else 2.5), y + 3.6 - (k // 3) * 2.4
        caja(ax, cx - 2.2, cy - 1.0, 4.4, 2.0, fc=col, ec=col, r=0.5, z=3)
        texto(ax, cx, cy, name, 6.6, "bold", "white", z=6)
    # mini composición con cajas (paso 5)
    x, y = centros[4]
    for k, col in enumerate(["#d81b60", "#d81b60", "#1e88e5", "#43a047"]):
        ax.add_patch(Rectangle((x + 13.6 + (k % 2) * 1.3, y + 1.4 + (k // 2) * 1.3), 1.1, 1.1, fc="white", ec=col, lw=1.6, zorder=6))
    # flechas del flujo (serpentina)
    flecha(ax, cols[0] + 16.6, rows[0] + 4.1, cols[1] - 0.1, rows[0] + 4.1)
    flecha(ax, cols[1] + 8.2, rows[0] - 0.1, cols[1] + 8.2, rows[1] + 8.3)
    flecha(ax, cols[1] - 0.1, rows[1] + 4.1, cols[0] + 16.6, rows[1] + 4.1)
    flecha(ax, cols[0] + 8.2, rows[1] - 0.1, cols[0] + 8.2, rows[2] + 8.3)
    flecha(ax, cols[0] + 16.6, rows[2] + 4.1, cols[1] - 0.1, rows[2] + 4.1)
    # verificación humana (ancho completo)
    caja(ax, cols[0], 9.0, 35, 5.4, fc="white", ec=ACC, lw=2.2)
    numero(ax, cols[0] + 1.6, 12.8, 7); texto(ax, cols[0] + 9.6, 12.7, t["s"][6][0], 10.3, "bold")
    texto(ax, cols[0] + 17.5, 10.3, t["s"][6][1], 8.2)
    flecha(ax, cols[1] + 8.2, rows[2] - 0.1, cols[1] + 8.2, 14.5)

    # 4 · salida
    caja(ax, 87.6, 31.5, 10.8, 12.5, fc="white", ec=ACC, lw=2)
    texto(ax, 93, 41.8, t["o1"], 10, "bold"); texto(ax, 93, 36.3, t["o1d"], 7.4)
    for k, key in enumerate(["o2", "o3"]):
        ax.add_patch(Ellipse((93, 25.5 - k * 9.5), 9.8, 6.8, fc="white", ec=EDGE, lw=1.6, zorder=3)); texto(ax, 93, 25.5 - k * 9.5, t[key], 8.6)
    flecha(ax, 93, 31.5, 93, 29.0); flecha(ax, 93, 22.0, 93, 19.5)

    # principio y referencia
    caja(ax, 1, 1.6, 98, 4.2, fc="#e8f2f1", ec=ACC, lw=1.4, r=0.9)
    texto(ax, 50, 3.7, t["principio"], 10.2, "bold", ACC)
    texto(ax, 99, 0.4, t["ref"], 8, c=MUT, ha="right", style="italic")
    for ext in ("png", "svg", "pdf"):
        fig.savefig(OUT / f"flujo_calidad_figuras_{lang}.{ext}", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    for lang in T:
        dibujar(lang)
    print("listo:", [p.name for p in OUT.glob("flujo_calidad_figuras_*")])
