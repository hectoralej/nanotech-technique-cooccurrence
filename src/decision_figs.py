"""Tres figuras simples para decidir (entrega/): que capturar, que mas reporta un artículo con TEM, y pares imagen-espectro."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from .common import DATA, ROOT  # noqa: E402
from .data import load_articles  # noqa: E402

OUT = ROOT / "entrega"
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e1e0d9"
BLUE, ORANGE = "#2a78d6", "#eb6834"
SEQ = LinearSegmentedColormap.from_list("s", ["#fcfcfb", "#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])
FAM = {"LNP": "LNP", "liposome": "Liposomas", "SLN_NLC": "SLN/NLC", "PLN": "PLN", "polymeric": "Poliméricas", "inorganic": "Inorgánicas"}
NICE = {"DSC_TGA": "DSC / TGA", "cryoEM": "cryo-EM", "UVVis": "UV-Vis"}


def setup():
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "DejaVu Sans"], "figure.facecolor": SURF, "axes.facecolor": SURF,
                         "savefig.facecolor": SURF, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})


def heat(ax, M, rows, cols, fmt="{:.0f}"):
    ax.imshow(M, cmap=SEQ, vmin=0, vmax=100, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            if v == v:
                ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=11, color="white" if v >= 50 else INK)
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, fontsize=11)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows, fontsize=12)
    ax.xaxis.tick_top(); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-.5, len(cols), 1), minor=True); ax.set_yticks(np.arange(-.5, len(rows), 1), minor=True)
    ax.grid(which="minor", color=SURF, lw=2); ax.tick_params(which="minor", length=0)


def d1(prev):
    rows = ["DLS", "zeta", "TEM", "SEM", "UVVis", "FTIR", "XRD", "DSC_TGA", "cryoEM", "EDS", "AFM", "NTA", "SAXS"]
    cols = list(FAM)
    M = np.array([[100 * float(prev[(prev.stratum == f) & (prev.technique == t)].prevalence.iloc[0]) for f in cols] for t in rows])
    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    heat(ax, M, [NICE.get(r, r) for r in rows], [FAM[c] for c in cols])
    ax.axhline(4.5, color=INK2, lw=1, ls=":"); ax.axhline(8.5, color=INK2, lw=1, ls=":")
    for y, txt in [(2, "capturar siempre"), (6.5, "capturar como opcional"), (10.5, "solo bandera")]:
        ax.text(len(cols) - .35, y, txt, rotation=-90, va="center", ha="left", fontsize=10, color=INK2)
    fig.suptitle("DLS y zeta se reportan en 50–90 % de los artículos de lípidos y polímeros; SAXS casi nunca", x=0.02, ha="left", fontsize=14, y=0.99)
    fig.text(0.02, 0.01, "% de artículos que reportan la técnica (muestra de 2.025 artículos). Líneas punteadas separan los niveles recomendados.", fontsize=9.5, color=INK2)
    fig.subplots_adjust(top=.84, left=.14, right=.9, bottom=.07)
    fig.savefig(OUT / "decision_1_que_capturar.png", dpi=170); plt.close(fig)


def d2(pairs):
    rows = ["DLS", "zeta", "UVVis", "SEM", "FTIR", "XRD", "EDS", "SAXS"]
    cols = list(FAM)
    M = np.full((len(rows), len(cols)), np.nan)
    nA = []
    for j, f in enumerate(cols):
        for i, b in enumerate(rows):
            r = pairs[(pairs.stratum == f) & (pairs.A == "TEM") & (pairs.B == b)]
            M[i, j] = 100 * float(r.P_B_given_A.iloc[0])
        nA.append(int(pairs[(pairs.stratum == f) & (pairs.A == "TEM")].nA.iloc[0]))
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    heat(ax, M, [NICE.get(r, r) for r in rows], [f"{FAM[c]}\nn={n}" for c, n in zip(cols, nA)])
    fig.suptitle("Si un artículo muestra TEM, entre 77 y 96 % también trae DLS y zeta; en inorgánicas, solo ~52 %", x=0.02, ha="left", fontsize=14, y=0.99)
    fig.text(0.02, 0.01, "% de los artículos con TEM que también reportan la técnica de la fila; n = artículos con TEM.", fontsize=9.5, color=INK2)
    fig.subplots_adjust(top=.76, left=.1, right=.98, bottom=.09)
    fig.savefig(OUT / "decision_2_dado_TEM.png", dpi=170); plt.close(fig)


def d3(em, df):
    spectra = ["UVVis", "FTIR", "XRD", "NMR", "EDS", "SAXS", "Raman_SERS", "XPS"]
    fams = list(FAM)
    a_same, a_art, lo, hi, n_em = [], [], [], [], []
    for f in fams:
        sub = df[df.primary_family == f]
        e = sub[sub["EM"]]
        n = len(e)
        n_em.append(n)
        a_art.append(100 * e[spectra].any(axis=1).mean())
        r = em[(em.stratum == f) & (em.what == "micrograph+spectrum_same_figure")].iloc[0]
        a_same.append(100 * r.P); lo.append(100 * (r.P - r.ci_lo)); hi.append(100 * (r.ci_hi - r.P))
    y = np.arange(len(fams))
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.barh(y - .19, a_art, height=.34, color=BLUE, label="en el mismo artículo")
    ax.barh(y + .19, a_same, height=.34, color=ORANGE, label="en la misma figura")
    ax.errorbar(a_same, y + .19, xerr=[lo, hi], fmt="none", ecolor=INK2, elinewidth=1.2, capsize=3)
    for yi, v1, v2, h in zip(y, a_art, a_same, hi):
        ax.text(v1 + 1, yi - .19, f"{v1:.0f} %", va="center", fontsize=10.5, color=INK)
        ax.text(v2 + h + 1.5, yi + .19, f"{v2:.0f} %", va="center", fontsize=10.5, color=INK)
    ax.set_yticks(y); ax.set_yticklabels([f"{FAM[f]}  (n={n})" for f, n in zip(fams, n_em)], fontsize=11.5)
    ax.invert_yaxis(); ax.set_xlim(0, 100)
    ax.grid(axis="x", color=GRID); ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    ax.set_xlabel("% de los artículos con micrografía que también traen un espectro")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.09), ncol=2, fontsize=11)
    fig.suptitle("La mayoría de los artículos con micrografía trae también un espectro, pero pocos los muestran juntos en una figura", x=0.02, ha="left", fontsize=13, y=0.99)
    fig.text(0.02, 0.01, "Espectro = UV-Vis, FTIR, XRD, RMN, EDS, SAXS, Raman o XPS. 'Misma figura' = proxy por pie de figura, con IC95 %. n = artículos con micrografía.", fontsize=9, color=INK2)
    fig.subplots_adjust(top=.82, left=.22, right=.97, bottom=.18)
    fig.savefig(OUT / "decision_3_pares_imagen_espectro.png", dpi=170); plt.close(fig)


def d4(prev):
    techs = ["DLS", "zeta", "TEM", "UVVis", "SEM", "FTIR", "cryoEM", "qPCR_ddPCR"]
    labels = ["DLS", "Zeta", "TEM", "UV-Vis", "SEM", "FTIR", "cryo-EM", "qPCR / ddPCR"]
    groups = [("ORGANIC", "Lípidos y polímeros", BLUE), ("inorganic", "Inorgánicas", "#1baf7a"), ("AAV", "AAV", ORANGE)]
    y = np.arange(len(techs))
    fig, ax = plt.subplots(figsize=(9.5, 6.4))
    for k, (st, name, col) in enumerate(groups):
        v = [100 * float(prev[(prev.stratum == st) & (prev.technique == t)].prevalence.iloc[0]) for t in techs]
        off = (k - 1) * 0.26
        ax.barh(y + off, v, height=.24, color=col, label=name)
        for yi, vi in zip(y, v):
            ax.text(vi + 1, yi + off, f"{vi:.0f}", va="center", fontsize=9.5, color=INK)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=12)
    ax.invert_yaxis(); ax.set_xlim(0, 100)
    ax.grid(axis="x", color=GRID); ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    ax.set_xlabel("% de los artículos que reportan la técnica")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.08), ncol=3, fontsize=11)
    fig.suptitle("AAV es la excepción: casi sin DLS ni zeta, y con qPCR/ddPCR en 3 de cada 4 artículos", x=0.02, ha="left", fontsize=13.5, y=0.99)
    fig.text(0.02, 0.01, "Muestra de 2.025 artículos. Fuera de AAV, el qPCR es sobre todo expresión génica (RT-qPCR), no título de vector.", fontsize=9.5, color=INK2)
    fig.subplots_adjust(top=.85, left=.17, right=.97, bottom=.12)
    fig.savefig(OUT / "decision_4_AAV_excepcion.png", dpi=170); plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    setup()
    prev = pd.read_csv(DATA / "prevalence.csv"); pairs = pd.read_csv(DATA / "pairs.csv"); em = pd.read_csv(DATA / "em_row.csv")
    df = load_articles()
    d1(prev); d2(pairs); d3(em, df); d4(prev)
    print("ok")


if __name__ == "__main__":
    main()
