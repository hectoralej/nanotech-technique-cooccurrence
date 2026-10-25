"""Figura estética (diagrama de flujo tipo Sankey) del recorrido de los datos: de las figuras de los artículos a los recortes que entran al modelo y a su clase de portador.
Lee los conteos reales de modelos/flujo_figuras/figuras_vision.csv y segmentacion/cajas/indice_recortes.csv (no hay cifras escritas a mano salvo el F1 de referencia).
Salida: figuras/modelos/fig_hero_flujo_{es,en}.{png,svg}.  Uso: python figuras/generar_figura_flujo_datos.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path as MPath

RAIZ = Path(__file__).resolve().parents[1]
SAL = Path(__file__).resolve().parent / "modelos"; SAL.mkdir(exist_ok=True)
BG, INK, SOFT, DIM = "#0B1220", "#F3F4F6", "#9CA3AF", "#6B7280"
plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})

f = pd.read_csv(RAIZ / "modelos/flujo_figuras/figuras_vision.csv", encoding="utf-8-sig", dtype=str)
c = pd.read_csv(RAIZ / "modelos/flujo_figuras/segmentacion/cajas/indice_recortes.csv", encoding="utf-8-sig", dtype=str)
m = c.merge(f[["fig_id", "destino_vision"]], on="fig_id", how="left")
top = m.padre.isna(); el = top & (m.elegible_morfologia == "True") & m.clase.notna()
N_FIG, N_SEG, N_PAN, N_ENT = len(f), c.fig_id.nunique(), len(c), int(el.sum())
cd = m.groupby(["destino_vision", "tipo"]).size().to_dict()
micro = m[m.tipo == "micro"]
sin_clase = int((micro.padre.isna() & (micro.elegible_morfologia == "True") & micro.clase.isna()).sum())
indet = int((micro.padre.isna() & (micro.elegible_morfologia != "True")).sum())
inset = int(micro.padre.notna().sum())
n_esp, n_otro, n_micro = int((m.tipo == "espectro").sum()), int((m.tipo == "otro").sum()), int((m.tipo == "micro").sum())
clases = m[el].clase.value_counts().to_dict()
assert n_micro == N_ENT + sin_clase + indet + inset, (n_micro, N_ENT, sin_clase, indet, inset)

T = {"es": {"title": "Del artículo al recorte: qué entra al modelo", "sub": "Cada banda es un conjunto de paneles de figura. Ancho proporcional al número de paneles.",
            "s1": "figuras clasificadas", "s2": "figuras con paneles", "s3": "paneles recortados", "s4": "recortes para el modelo", "s5": "F1 macro por artículo*",
            "c1": "Tipo de figura", "c2": "Tipo de panel", "c3": "Decisión", "c4": "Clase del artículo",
            "compuesta": "compuesta", "pareja": "pareja", "excluir": "excluir", "micro": "micrografía", "espectro": "espectro", "otro": "otro (foto, fluorescencia, biología…)",
            "entra": "Entra al modelo", "no_esp": "No entra: espectro", "no_otro": "No entra: otro", "no_ins": "No entra: inset", "no_ind": "No entra: sin clase o indeterminado",
            "inorganico": "Inorgánico", "lipidico": "Lipídico", "nanomaterial": "Nanomaterial", "polimerico": "Polimérico",
            "pie": "Fuentes: modelos/flujo_figuras/figuras_vision.csv e indice_recortes.csv. Solo figuras con paneles (compuestas y parejas con micrografía o espectro útil); las simples y las de espectros superpuestos no se recortan. La clase es la del ARTÍCULO, no la del recorte.\n*Validación cruzada por artículo, ensamble de 3 semillas de DINOv2 (modelos/comparacion/ANALISIS_06_NFFA.md); exploratorio; línea base de la clase mayoritaria: exactitud 0,442."},
     "en": {"title": "From article to crop: what enters the model", "sub": "Each band is a set of figure panels. Width is proportional to the number of panels.",
            "s1": "figures classified", "s2": "figures with panels", "s3": "panels cropped", "s4": "crops for the model", "s5": "macro F1 per article*",
            "c1": "Figure type", "c2": "Panel type", "c3": "Decision", "c4": "Article class",
            "compuesta": "composite", "pareja": "pair", "excluir": "exclude", "micro": "micrograph", "espectro": "spectrum", "otro": "other (photo, fluorescence, biology…)",
            "entra": "Enters the model", "no_esp": "Excluded: spectrum", "no_otro": "Excluded: other", "no_ins": "Excluded: inset", "no_ind": "Excluded: no class or indeterminate",
            "inorganico": "Inorganic", "lipidico": "Lipid", "nanomaterial": "Nanomaterial", "polimerico": "Polymeric",
            "pie": "Sources: modelos/flujo_figuras/figuras_vision.csv and indice_recortes.csv. Only figures with panels (composites and pairs with a useful micrograph or spectrum); single-panel and overlaid-spectra figures are not cropped. The class is the ARTICLE class, not the crop class.\n*Article-level cross-validation, 3-seed DINOv2 ensemble (modelos/comparacion/ANALISIS_06_NFFA.md); exploratory; majority-class baseline accuracy 0.442."}}
COL = {"compuesta": "#2DD4BF", "pareja": "#FBBF24", "excluir": "#6B7280", "micro": "#34D399", "espectro": "#60A5FA", "otro": "#FB923C", "entra": "#A7F3D0",
       "no_esp": "#4B5563", "no_otro": "#4B5563", "no_ins": "#4B5563", "no_ind": "#4B5563",
       "inorganico": "#56B4E9", "lipidico": "#E69F00", "nanomaterial": "#009E73", "polimerico": "#CC79A7"}


SEP = {"v": "."}


def miles(n):
    return f"{n:,}".replace(",", SEP["v"])


def ribbon(ax, x0, y0a, y0b, x1, y1a, y1b, color, alpha=0.5):
    xm = (x0 + x1) / 2
    v = [(x0, y0a), (xm, y0a), (xm, y1a), (x1, y1a), (x1, y1b), (xm, y1b), (xm, y0b), (x0, y0b), (x0, y0a)]
    cod = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.LINETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MPath(v, cod), fc=color, ec="none", alpha=alpha, zorder=1))


def figura(L):
    SEP["v"] = "." if L == "es" else ","; t = T[L]; fig = plt.figure(figsize=(16, 9), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.04, 0.945, t["title"], color=INK, fontsize=24, fontweight="bold", va="center")
    ax.text(0.04, 0.905, t["sub"], color=SOFT, fontsize=11, va="center")
    stats = [(miles(N_FIG), t["s1"], "#2DD4BF"), (miles(N_SEG), t["s2"], "#FBBF24"), (miles(N_PAN), t["s3"], "#34D399"), (miles(N_ENT), t["s4"], "#A7F3D0"), ("0,52" if L == "es" else "0.52", t["s5"], "#E69F00")]
    for i, (num, lab, col) in enumerate(stats):
        x = 0.04 + i * 0.185
        ax.text(x, 0.835, num, color=col, fontsize=27, fontweight="bold", va="center"); ax.text(x, 0.795, lab, color=SOFT, fontsize=10, va="center")
        if i < 4: ax.text(x + 0.15, 0.835, "→", color=DIM, fontsize=22, va="center")
    colx = [0.09, 0.36, 0.62, 0.88]; w = 0.012; y_top, y_bot = 0.70, 0.12; gap = 0.014
    c1 = [(k, sum(v for (d, _), v in cd.items() if d == k)) for k in ("compuesta", "pareja", "excluir")]
    c2 = [("micro", n_micro), ("espectro", n_esp), ("otro", n_otro)]
    c3 = [("entra", N_ENT), ("no_ind", sin_clase + indet), ("no_ins", inset), ("no_esp", n_esp), ("no_otro", n_otro)]
    c4 = [(k, clases[k]) for k in ("nanomaterial", "polimerico", "inorganico", "lipidico")]
    cols = [c1, c2, c3, c4]; escala = (y_top - y_bot - gap * 4) / N_PAN
    pos = []
    for ci, nodos in enumerate(cols):
        y = pos[2]["entra"][0] if ci == 3 else y_top; d = {}
        for k, v in nodos:
            d[k] = (y, v * escala); y -= v * escala + (0.004 if ci == 3 else gap)
        pos.append(d)

    def fluir(ci, flujos, colorear):
        usado_s, usado_t = {}, {}
        for a, b, v in flujos:
            ya, _ = pos[ci][a]; yb, _ = pos[ci + 1][b]; sa, tb = usado_s.get(a, 0), usado_t.get(b, 0)
            ribbon(ax, colx[ci] + w, ya - sa, ya - sa - v * escala, colx[ci + 1], yb - tb, yb - tb - v * escala, COL[colorear(a, b)])
            usado_s[a] = sa + v * escala; usado_t[b] = tb + v * escala

    fluir(0, [(d, tp, cd[(d, tp)]) for d in ("compuesta", "pareja", "excluir") for tp in ("micro", "espectro", "otro") if (d, tp) in cd], lambda a, b: a)
    fluir(1, [("micro", "entra", N_ENT), ("micro", "no_ind", sin_clase + indet), ("micro", "no_ins", inset), ("espectro", "no_esp", n_esp), ("otro", "no_otro", n_otro)],
          lambda a, b: "micro" if b == "entra" else b)
    fluir(2, [("entra", k, v) for k, v in c4], lambda a, b: b)
    for ci, nodos in enumerate(cols):
        for k, v in nodos:
            y, h = pos[ci][k]; ax.add_patch(Rectangle((colx[ci], y - h), w, h, fc=COL[k], ec="none", zorder=3))
    caja = dict(boxstyle="round,pad=0.25", fc=BG, ec="none", alpha=0.8)
    for k, v in c1:
        y, h = pos[0][k]; ax.text(colx[0] - 0.012, y - h / 2, f"{t[k]}\n{miles(v)}", color=INK, fontsize=10.5, va="center", ha="right", zorder=5, linespacing=1.15)
    for k, v in c2:
        y, h = pos[1][k]; ax.text(colx[1] + 0.02, y - h / 2, f"{t[k]}\n{miles(v)}", color=INK, fontsize=10.5, va="center", ha="left", zorder=5, linespacing=1.15, bbox=caja)
    ys = {k: pos[2][k][0] - pos[2][k][1] / 2 - (0.0 if k == "entra" else 0.012) for k, _ in c3}; ys["entra"] = pos[2]["entra"][0] + 0.016; prev = None
    for k, _ in c3:                                                   # separa las etiquetas pequeñas para que no se pisen
        if k == "entra": continue
        if prev is not None and ys[prev] - ys[k] < 0.045: ys[k] = ys[prev] - 0.045
        prev = k
    for k, v in c3:
        ax.text(colx[2] + 0.02, ys[k], f"{t[k]}   {miles(v)}", color=INK if k == "entra" else SOFT, fontsize=10.5, fontweight="bold" if k == "entra" else "normal", va="center", ha="left", zorder=5, bbox=caja)
    for k, v in c4:
        y, h = pos[3][k]; ax.text(colx[3] + 0.02, y - h / 2, f"{t[k]}\n{miles(v)}", color=INK, fontsize=11, fontweight="bold", va="center", ha="left", zorder=5, linespacing=1.15)
    for ci, key in enumerate(("c1", "c2", "c3", "c4")):
        ax.text(colx[ci] + (w if ci == 0 else 0), y_top + 0.03, t[key].upper(), color=SOFT, fontsize=9, fontweight="bold", ha="right" if ci == 0 else "left", va="bottom")
    ax.text(0.04, 0.05, t["pie"], color=DIM, fontsize=7.8, va="center", linespacing=1.4)
    fig.savefig(SAL / f"fig_hero_flujo_{L}.png", dpi=220, facecolor=BG); fig.savefig(SAL / f"fig_hero_flujo_{L}.svg", facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    for lang in ("es", "en"): figura(lang)
    print("figura en", SAL, "| paneles", N_PAN, "| entran", N_ENT, "| figuras con paneles", N_SEG, "| figuras", N_FIG)
