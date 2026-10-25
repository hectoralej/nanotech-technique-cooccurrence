"""Tres figuras de los modelos de Nano2Predict, de los primeros modelos al último experimento (español e inglés; PNG 300 ppp, SVG y PDF).
Todas las cifras salen de los informes del repositorio (rutas en el pie de cada figura). Gráficos de puntos con intervalos (forest plots): una sola escala por panel,
línea de referencia visible, paleta Okabe-Ito (segura para daltonismo), IC 95 % por bootstrap de artículos.
Uso: python figuras/generar_figuras_modelos.py   ->  figuras/modelos/fig_modelos_{1,2,3}_{es,en}.{png,svg,pdf}
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SAL = Path(__file__).resolve().parent / "modelos"; SAL.mkdir(exist_ok=True)
INK, MUTED, GRID = "#1F2937", "#6B7280", "#E5E7EB"
C = {"base": "#8A8F98", "med": "#0072B2", "img": "#D55E00", "fus": "#009E73", "ctl": "#CC79A7", "neg": "#8A8F98"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
                     "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none"})


def fmt(v, d=3):
    return f"{v:+.{d}f}" if v < 0 or d == -1 else f"{v:.{d}f}"


def forest(ax, filas, xlabel, xlim, ref=None, ref_label=None, signed=False, zero_shade=False):
    """filas: (etiqueta, estimación, lo, hi|None, color, marcador, relleno)"""
    n = len(filas)
    ax.set_xlim(*xlim); ax.set_ylim(n - 0.4, -0.6)
    ax.grid(axis="x", color=GRID, lw=0.7); ax.set_axisbelow(True)
    if ref is not None:
        ax.axvline(ref, color=MUTED, lw=1.0, ls=(0, (4, 3)), zorder=1)
        if ref_label: ax.text(ref, -0.75, ref_label, color=MUTED, ha="center", va="bottom", fontsize=7)
    if zero_shade: ax.axvspan(xlim[0], 0, color="#F3F4F6", zorder=0)
    for i, (et, est, lo, hi, col, mk, fill) in enumerate(filas):
        if hi is not None: ax.plot([lo, hi], [i, i], color=col, lw=2.0, solid_capstyle="round", zorder=2)
        ax.plot([est], [i], marker=mk, ms=7.5, mfc=col if fill else "white", mec=col, mew=1.6, zorder=3, ls="none")
        txt = (f"{est:+.3f}" if signed else f"{est:.3f}") + (f"  [{lo:+.3f}, {hi:+.3f}]" if (signed and hi is not None) else (f"  [{lo:.3f}, {hi:.3f}]" if hi is not None else ""))
        ax.text(xlim[1], i, " " + txt, va="center", ha="left", fontsize=7.2, color=INK, clip_on=False)
    ax.set_yticks(range(n)); ax.set_yticklabels([f[0] for f in filas]); ax.tick_params(axis="y", length=0)
    ax.set_xlabel(xlabel)


def pie(fig, texto):
    fig.text(0.01, 0.005, texto, fontsize=6.6, color=MUTED, ha="left", va="bottom", wrap=True)


def guardar(fig, nombre):
    for ext in ("png", "svg", "pdf"):
        fig.savefig(SAL / f"{nombre}.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def leyenda(ax, items, loc="lower right", anchor=None):
    h = [plt.Line2D([0], [0], marker="o", color="none", mfc=c, mec=c, ms=7, label=l) for l, c in items]
    ax.legend(handles=h, loc=loc, frameon=False, fontsize=7.2, handletextpad=0.3, borderaxespad=0.2, bbox_to_anchor=anchor)


T = {
 "es": {
  "f1_title": "Figura 1 · De las medidas a la imagen y la fusión (v0.1, figura completa)",
  "a": "a · Tamaño de partícula (regresión)", "b": "b · Clase de portador (4 clases)",
  "r2": "R² fuera de muestra", "f1": "F1 macro fuera de muestra",
  "g_mean": "Media global", "c_mean": "Media por clase", "lin": "Regresión lineal", "ridge": "Ridge", "rf": "Random Forest", "hgb": "Gradient Boosting",
  "maj": "Clase mayoritaria", "img_fz": "Imagen: vectores congelados", "img_ft": "Imagen: ajuste fino", "med": "Solo medidas (logística)",
  "fus_fz": "Fusión: imagen congelada + medidas", "fus_ft": "Fusión: ajuste fino + medidas (50/50)",
  "lg_base": "Línea base", "lg_med": "Medidas / tabular", "lg_img": "Imagen", "lg_fus": "Fusión",
  "pie1": "Particiones por artículo (5); predicciones fuera de muestra; IC 95 % por bootstrap de artículos (1.000), sin incertidumbre de reentrenamiento. (a) 2.749 tamaños de 1.080 artículos, entradas B. (b) 2.100 figuras de 1.641 artículos.\nFuentes: modelos/tabular/REPORTE_TABULAR.md, modelos/comparacion/METRICAS_CON_IC.md y METRICAS_AJUSTE_FINO_CON_IC.md. Exploratorio: se probaron varias variantes sobre las mismas particiones.",
  "n_err": "error relativo mediano ≈ 44 % (piso: 43,6 %)",
  "f2_title": "Figura 2 · De la figura completa a los recortes de panel (por artículo)",
  "a2": "a · F1 macro por artículo", "b2": "b · Diferencias pareadas (IC 95 %)",
  "full": "Figura completa (03)", "crop_eq": "Recortes, mismas vistas que el 03", "crop_all": "Recortes, todas las vistas (04)",
  "x_f1": "F1 macro por artículo", "x_df": "Δ F1 macro",
  "d1": "ResNet50: recortes − figura", "d2": "DINOv2: recortes − figura", "d3": "Promedio: recortes − figura",
  "d4": "DINOv2: control, mismas vistas − figura", "d5": "ResNet50: control, mismas vistas − figura",
  "d6": "Imagen 04 − imagen 03 (n = 786)", "d7": "Fusión 04 − fusión 03 (n = 786)",
  "pie2": "n = 1.112 artículos en (a) y las 3 primeras filas de (b); n = 786 en las 2 últimas (artículos con figura completa, recortes y medidas). IC 95 % por bootstrap de artículos (2.000). Los puntos huecos son el promedio de 200 sorteos sin IC.\nFuentes: modelos/comparacion/ANALISIS_04_RECORTES.md y ANALISIS_FUSION_04.md. Con el mismo número de vistas por artículo la ventaja de los recortes se reduce (control); el IC de «fusión 04 − fusión 03» incluye el 0.",
  "f3_title": "Figura 3 · Preentrenar con NFFA-EUROPE antes de ajustar con nuestros recortes (DINOv2)",
  "a3": "a · F1 macro por artículo, por semilla", "b3": "b · Diferencias entre brazos (ensamble, IC 95 %)",
  "A": "A · LVD → recortes\n(línea base)", "B": "B · LVD → NFFA → recortes", "Cc": "C · control: NFFA con\netiquetas mezcladas → recortes",
  "seed": "semilla", "ens": "ensamble de 3 semillas", "x_f1b": "F1 macro por artículo",
  "e1": "B − A (NFFA frente a línea base)", "e2": "B − C (NFFA frente a control)", "e3": "C − A (control frente a línea base)",
  "pie3": "1.114 artículos; 5 particiones por artículo; 3 semillas por brazo; la etapa 1 (NFFA, 7 morfologías, 8.204 teselas, 96,8 % de exactitud interna) corrió una vez. IC 95 % por bootstrap de artículos (2.000) sobre las probabilidades promediadas entre semillas.\nResultado: B no supera a A (IC incluye 0); mezclar las etiquetas daña (C − A). Fuente: modelos/comparacion/ANALISIS_06_NFFA.md. Criterio fijado antes de ver los resultados.",
 },
 "en": {
  "f1_title": "Figure 1 · From measurements to image and fusion (v0.1, whole figure)",
  "a": "a · Particle size (regression)", "b": "b · Carrier class (4 classes)",
  "r2": "Out-of-sample R²", "f1": "Out-of-sample macro F1",
  "g_mean": "Global mean", "c_mean": "Per-class mean", "lin": "Linear regression", "ridge": "Ridge", "rf": "Random Forest", "hgb": "Gradient Boosting",
  "maj": "Majority class", "img_fz": "Image: frozen embeddings", "img_ft": "Image: fine-tuning", "med": "Measurements only (logistic)",
  "fus_fz": "Fusion: frozen image + measurements", "fus_ft": "Fusion: fine-tuning + measurements (50/50)",
  "lg_base": "Baseline", "lg_med": "Measurements / tabular", "lg_img": "Image", "lg_fus": "Fusion",
  "pie1": "Article-level 5-fold splits; out-of-sample predictions; 95 % CI by article bootstrap (1,000), excluding retraining uncertainty. (a) 2,749 sizes from 1,080 articles, feature set B. (b) 2,100 figures from 1,641 articles.\nSources: modelos/tabular/REPORTE_TABULAR.md, modelos/comparacion/METRICAS_CON_IC.md and METRICAS_AJUSTE_FINO_CON_IC.md. Exploratory: several variants were tried on the same splits.",
  "n_err": "median relative error ≈ 44 % (floor: 43.6 %)",
  "f2_title": "Figure 2 · From the whole figure to panel crops (article level)",
  "a2": "a · Macro F1 per article", "b2": "b · Paired differences (95 % CI)",
  "full": "Whole figure (03)", "crop_eq": "Crops, same number of views as 03", "crop_all": "Crops, all views (04)",
  "x_f1": "Macro F1 per article", "x_df": "Δ macro F1",
  "d1": "ResNet50: crops − figure", "d2": "DINOv2: crops − figure", "d3": "Average: crops − figure",
  "d4": "DINOv2: control, same views − figure", "d5": "ResNet50: control, same views − figure",
  "d6": "Image 04 − image 03 (n = 786)", "d7": "Fusion 04 − fusion 03 (n = 786)",
  "pie2": "n = 1,112 articles in (a) and the first 3 rows of (b); n = 786 in the last 2 (articles with a whole figure, crops and measurements). 95 % CI by article bootstrap (2,000). Hollow points are the mean of 200 draws, no CI.\nSources: modelos/comparacion/ANALISIS_04_RECORTES.md and ANALISIS_FUSION_04.md. With the same number of views per article the crop advantage shrinks (control); the CI of 'fusion 04 − fusion 03' includes 0.",
  "f3_title": "Figure 3 · Pre-training on NFFA-EUROPE before fine-tuning on our crops (DINOv2)",
  "a3": "a · Macro F1 per article, per seed", "b3": "b · Differences between arms (ensemble, 95 % CI)",
  "A": "A · LVD → crops\n(baseline)", "B": "B · LVD → NFFA → crops", "Cc": "C · control: NFFA with\nshuffled labels → crops",
  "seed": "seed", "ens": "3-seed ensemble", "x_f1b": "Macro F1 per article",
  "e1": "B − A (NFFA vs baseline)", "e2": "B − C (NFFA vs control)", "e3": "C − A (control vs baseline)",
  "pie3": "1,114 articles; article-level 5-fold; 3 seeds per arm; stage 1 (NFFA, 7 morphologies, 8,204 tiles, 96.8 % internal accuracy) ran once. 95 % CI by article bootstrap (2,000) on seed-averaged probabilities.\nResult: B does not beat A (CI includes 0); shuffling labels hurts (C − A). Source: modelos/comparacion/ANALISIS_06_NFFA.md. Criterion fixed before seeing results.",
 }}


def fig1(L):
    t = T[L]; fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.8, 4.4), gridspec_kw={"wspace": 1.5})
    forest(ax1, [(t["g_mean"], -0.003, -0.009, -0.001, C["base"], "s", True), (t["c_mean"], 0.180, 0.127, 0.226, C["base"], "s", True),
                 (t["lin"], 0.237, 0.181, 0.288, C["med"], "o", True), (t["ridge"], 0.240, 0.189, 0.287, C["med"], "o", True),
                 (t["rf"], 0.198, 0.129, 0.263, C["med"], "o", True), (t["hgb"], 0.167, 0.090, 0.239, C["med"], "o", True)],
           t["r2"], (-0.05, 0.32), ref=0.180, ref_label=t["c_mean"])
    ax1.set_title(t["a"], loc="left", fontsize=9.5, fontweight="bold", pad=18); ax1.text(0.0, -0.2, t["n_err"], fontsize=7, color=MUTED, ha="left", va="top", transform=ax1.transAxes)
    forest(ax2, [(t["maj"], 0.156, 0.149, 0.162, C["base"], "s", True), (t["img_fz"], 0.442, 0.416, 0.467, C["img"], "o", True), (t["img_ft"], 0.460, 0.437, 0.484, C["img"], "o", True),
                 (t["med"], 0.526, 0.500, 0.553, C["med"], "o", True), (t["fus_fz"], 0.561, 0.535, 0.585, C["fus"], "D", True), (t["fus_ft"], 0.580, 0.554, 0.603, C["fus"], "D", True)],
           t["f1"], (0.10, 0.65), ref=0.156, ref_label=t["maj"])
    ax2.set_title(t["b"], loc="left", fontsize=9.5, fontweight="bold", pad=18)
    leyenda(ax2, [(t["lg_base"], C["base"]), (t["lg_med"], C["med"]), (t["lg_img"], C["img"]), (t["lg_fus"], C["fus"])], loc="center left", anchor=(0.2, 0.5))
    fig.suptitle(t["f1_title"], x=0.01, ha="left", fontsize=11, fontweight="bold", y=1.03); pie(fig, t["pie1"]); fig.subplots_adjust(bottom=0.24)
    guardar(fig, f"fig_modelos_1_{L}")


def fig2(L):
    t = T[L]; fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.3), gridspec_kw={"wspace": 0.95, "width_ratios": [1, 1.15]})
    # (a) puntos agrupados por modelo
    datos = {"ResNet50": (0.416, 0.447, 0.472), "DINOv2": (0.458, 0.471, 0.509)}
    cols = [C["base"], C["ctl"], C["img"]]; etq = [t["full"], t["crop_eq"], t["crop_all"]]
    ax1.set_xlim(0.38, 0.54); ax1.grid(axis="x", color=GRID, lw=0.7); ax1.set_axisbelow(True); ax1.set_ylim(1.7, -0.7)
    for j, (m, vals) in enumerate(datos.items()):
        ax1.plot([vals[0], vals[2]], [j, j], color=GRID, lw=3, zorder=1)
        for k, v in enumerate(vals):
            ax1.plot([v], [j + (k - 1) * 0.0], marker="o", ms=9, color=cols[k], mec="white", mew=1.2, zorder=3, ls="none")
            arriba = k != 1
            ax1.text(v, j - 0.22 if arriba else j + 0.22, f"{v:.3f}", ha="center", va="bottom" if arriba else "top", fontsize=7.3)
    ax1.set_yticks([0, 1]); ax1.set_yticklabels(list(datos)); ax1.tick_params(axis="y", length=0); ax1.set_xlabel(t["x_f1"])
    ax1.set_title(t["a2"], loc="left", fontsize=9.5, fontweight="bold", pad=18); leyenda(ax1, list(zip(etq, cols)), loc="upper center", anchor=(0.5, -0.17))
    # (b) diferencias pareadas
    filas = [(t["d1"], 0.056, 0.020, 0.091, C["img"], "o", True), (t["d2"], 0.052, 0.013, 0.086, C["img"], "o", True), (t["d3"], 0.042, 0.007, 0.079, C["img"], "o", True),
             (t["d5"], 0.447 - 0.416, None, None, C["ctl"], "o", False), (t["d4"], 0.471 - 0.458, None, None, C["ctl"], "o", False),
             (t["d6"], 0.044, 0.002, 0.086, C["med"], "D", True), (t["d7"], 0.031, -0.010, 0.071, C["fus"], "D", True)]
    forest(ax2, filas, t["x_df"], (-0.03, 0.12), ref=0.0, signed=True)
    ax2.set_title(t["b2"], loc="left", fontsize=9.5, fontweight="bold", pad=18)
    fig.suptitle(t["f2_title"], x=0.01, ha="left", fontsize=11, fontweight="bold", y=1.03); pie(fig, t["pie2"]); fig.subplots_adjust(bottom=0.3)
    guardar(fig, f"fig_modelos_2_{L}")


def fig3(L):
    t = T[L]; fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.2), gridspec_kw={"wspace": 1.25, "width_ratios": [1, 1.1]})
    brazos = [("A", t["A"], C["base"], [0.512, 0.512, 0.490], 0.521), ("B", t["B"], C["img"], [0.480, 0.479, 0.503], 0.502), ("Cc", t["Cc"], C["ctl"], [0.459, 0.454, 0.479], 0.476)]
    ax1.set_xlim(0.43, 0.55); ax1.set_ylim(2.6, -0.6); ax1.grid(axis="x", color=GRID, lw=0.7); ax1.set_axisbelow(True)
    for i, (k, et, col, vals, ens) in enumerate(brazos):
        mu = sum(vals) / 3; sd = (sum((v - mu) ** 2 for v in vals) / 3) ** 0.5
        ax1.plot([mu - sd, mu + sd], [i, i], color=col, lw=5, alpha=0.25, solid_capstyle="round", zorder=1)
        for s, v in enumerate(vals): ax1.plot([v], [i + (s - 1) * 0.12], marker="o", ms=6, color=col, mec="white", mew=0.8, ls="none", zorder=3)
        ax1.plot([ens], [i], marker="D", ms=8, mfc="white", mec=col, mew=1.8, ls="none", zorder=4)
        ax1.text(0.55, i, f" {mu:.3f} ± {sd:.3f}\n ens. {ens:.3f}", va="center", fontsize=7.2, clip_on=False)
    ax1.set_yticks(range(3)); ax1.set_yticklabels([b[1] for b in brazos]); ax1.tick_params(axis="y", length=0); ax1.set_xlabel(t["x_f1b"])
    ax1.set_title(t["a3"], loc="left", fontsize=9.5, fontweight="bold", pad=18)
    h = [plt.Line2D([0], [0], marker="o", color="none", mfc=MUTED, mec="white", ms=6, label=t["seed"]), plt.Line2D([0], [0], marker="D", color="none", mfc="white", mec=MUTED, ms=7, label=t["ens"])]
    ax1.legend(handles=h, loc="upper left", frameon=False, fontsize=7.2)
    forest(ax2, [(t["e1"], -0.019, -0.042, 0.005, C["img"], "o", True), (t["e2"], 0.026, 0.001, 0.050, C["ctl"], "o", True), (t["e3"], -0.045, -0.070, -0.020, C["base"], "s", True)],
           t["x_df"], (-0.09, 0.08), ref=0.0, signed=True)
    ax2.set_xticks([-0.05, 0.0, 0.05]); ax2.set_title(t["b3"], loc="left", fontsize=9.5, fontweight="bold", pad=18)
    fig.suptitle(t["f3_title"], x=0.01, ha="left", fontsize=11, fontweight="bold", y=1.03); pie(fig, t["pie3"]); fig.subplots_adjust(bottom=0.22)
    guardar(fig, f"fig_modelos_3_{L}")


if __name__ == "__main__":
    for lang in ("es", "en"):
        fig1(lang); fig2(lang); fig3(lang)
    print("figuras en", SAL, sorted(p.name for p in SAL.glob("*.png")))
