"""Figuras 1 a 7 (PNG + SVG estaticos; HTML interactivo con modo claro/oscuro para 1, 2, 5, 6).

Paleta: referencia validada del skill dataviz (secuencial azul, divergente azul<->rojo con punto medio gris,
categorica en orden fijo). Los titulos se escriben como hallazgos y salen de `figure_titles()`, calculados desde los datos.
"""
from __future__ import annotations

import json
import math
import textwrap

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from plotly.offline import get_plotlyjs  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402

from .common import DATA, FIGS, load_yaml  # noqa: E402
from .data import FAMILY_ORDER, ORGANIC, reliability_table  # noqa: E402
from .detect import load_techniques  # noqa: E402

THEMES = {
    "light": dict(surface="#fcfcfb", text="#0b0b0b", text2="#52514e", muted="#898781", grid="#e1e0d9", axis="#c3c2b7",
                  gray="#dcdbd5", mid="#f0efec", seq=["#fcfcfb", "#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"],
                  cat=["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]),
    "dark": dict(surface="#1a1a19", text="#ffffff", text2="#c3c2b7", muted="#898781", grid="#2c2c2a", axis="#383835",
                 gray="#2f2f2d", mid="#383835", seq=["#1a1a19", "#15304f", "#184f95", "#256abf", "#3987e5", "#86b6ef", "#cde2fb"],
                 cat=["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]),
}
DIV_POS, DIV_NEG = {"light": "#2a78d6", "dark": "#3987e5"}, {"light": "#e34948", "dark": "#e66767"}
FAM_LABEL = {"ALL": "Todas", "ORGANIC": "Orgánicas", "LNP": "LNP", "liposome": "Liposomas", "SLN_NLC": "SLN/NLC", "PLN": "PLN (híbridas)",
             "polymeric": "Poliméricas", "inorganic": "Inorgánicas", "AAV": "AAV"}
PANELS = ["ALL", "LNP", "liposome", "SLN_NLC", "PLN", "polymeric", "inorganic", "AAV"]
CATEGORY_GROUP = {"microscopy": "Microscopía", "light_scattering": "Dispersión de luz", "hydrodynamic": "Dispersión de luz",
                  "scattering_diffraction": "Espectroscopía y difracción", "spectroscopy": "Espectroscopía y difracción",
                  "elemental": "Espectroscopía y difracción", "molecular": "Otras", "assay": "Otras", "porosity": "Otras",
                  "magnetic": "Otras", "thermal": "Térmica"}
GROUP_ORDER = ["Microscopía", "Dispersión de luz", "Espectroscopía y difracción", "Térmica", "Otras"]
RELIAB_NOTE = {"recall_low": "†", "precision_low": "‡", "unvalidated": "°", "ok": ""}


def cmap_for(theme: str, kind: str = "seq"):
    t = THEMES[theme]
    if kind == "seq":
        return LinearSegmentedColormap.from_list("seq", t["seq"])
    return LinearSegmentedColormap.from_list("div", [DIV_NEG[theme], t["mid"], DIV_POS[theme]])


def setup_mpl(theme="light"):
    t = THEMES[theme]
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "DejaVu Sans"], "figure.facecolor": t["surface"],
                         "axes.facecolor": t["surface"], "savefig.facecolor": t["surface"], "text.color": t["text"],
                         "axes.labelcolor": t["text2"], "xtick.color": t["text2"], "ytick.color": t["text2"], "axes.edgecolor": t["axis"],
                         "svg.fonttype": "none"})


def save(fig, name):
    FIGS.mkdir(exist_ok=True)
    fig.savefig(FIGS / f"{name}.png", dpi=170, bbox_inches="tight")
    fig.savefig(FIGS / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------------------------
# datos
# ----------------------------------------------------------------------------------------------
class Ctx:
    def __init__(self):
        self.pairs = pd.read_csv(DATA / "pairs.csv")
        self.prev = pd.read_csv(DATA / "prevalence.csv")
        self.em = pd.read_csv(DATA / "em_row.csv")
        self.trend = pd.read_csv(DATA / "trend.csv")
        self.meta = json.loads((DATA / "analysis_meta.json").read_text(encoding="utf-8"))
        self.definition = self.meta["definition"]
        self.techs = self.meta["techniques_in_matrix"]
        self.rel = reliability_table(self.definition).set_index("technique")["reliability"]
        _, tl = load_techniques()
        self.cat = {t.name: CATEGORY_GROUP[t.category] for t in tl}
        self.arts = pd.read_csv(DATA / "articles.csv", dtype={"pmcid": str}, low_memory=False)
        X = self.arts[self.techs].to_numpy(dtype=bool)
        from .stats import cluster_order
        self.order = [self.techs[i] for i in cluster_order(X)]

    def label(self, t):
        return t.replace("_", "/") + RELIAB_NOTE.get(self.rel.get(t, ""), "")

    def mat(self, stratum, col):
        sub = self.pairs[self.pairs.stratum == stratum].set_index(["A", "B"])
        k = len(self.order)
        M = np.full((k, k), np.nan)
        for i, a in enumerate(self.order):
            for j, b in enumerate(self.order):
                if (a, b) in sub.index:
                    M[i, j] = sub.loc[(a, b), col]
        return M

    def nA(self, stratum):
        sub = self.pairs[self.pairs.stratum == stratum].groupby("A")["nA"].first()
        return np.array([int(sub.get(t, 0)) for t in self.order])


# ----------------------------------------------------------------------------------------------
# Figura 1 - matriz de P(B|A)
# ----------------------------------------------------------------------------------------------

def fig1_static(c: Ctx, title: str):
    setup_mpl("light")
    th = THEMES["light"]
    cmap = cmap_for("light")
    fig, axes = plt.subplots(2, 4, figsize=(34, 19.5))
    for ax, st in zip(axes.ravel(), PANELS):
        P, nA = c.mat(st, "P_B_given_A"), c.nA(st)
        width = c.mat(st, "ci_hi") - c.mat(st, "ci_lo")
        k = len(c.order)
        for i in range(k):
            for j in range(k):
                if i == j:
                    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, color=th["surface"], zorder=1))
                    continue
                v = P[i, j]
                low = nA[i] < 20
                if np.isnan(v) or low:
                    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, facecolor=th["gray"], hatch="////" if not np.isnan(v) else None,
                                               edgecolor=th["surface"], linewidth=.6, zorder=1))
                    continue
                alpha = 0.45 if width[i, j] > 0.3 else 1.0
                ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, facecolor=cmap(v), alpha=alpha, edgecolor=th["surface"], linewidth=.6, zorder=1))
                tc = "white" if (v >= .5 and alpha == 1.0) else th["text"]
                ax.text(j, i, f"{100 * v:.0f}", ha="center", va="center", fontsize=8.5, color=tc, zorder=3)
        ax.set_xlim(-.5, k - .5); ax.set_ylim(k - .5, -.5)
        ax.set_xticks(range(k)); ax.set_xticklabels([c.label(t) for t in c.order], rotation=60, ha="right", fontsize=10)
        ax.set_yticks(range(k)); ax.set_yticklabels([f"{c.label(t)}  n={n}" for t, n in zip(c.order, nA)], fontsize=10)
        for lbl, n in zip(ax.get_yticklabels(), nA):
            lbl.set_color(th["muted"] if n < 20 else th["text"])
        n_art = int(c.pairs[c.pairs.stratum == st]["N"].iloc[0]) if (c.pairs.stratum == st).any() else 0
        ax.set_title(f"{FAM_LABEL[st]} (N = {n_art})", fontsize=15, loc="left", color=th["text"])
        ax.set_xlabel("B (resultado)", fontsize=10); ax.set_ylabel("A (condición)", fontsize=10)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(length=0)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 100))
    fig.subplots_adjust(left=.07, right=.93, wspace=.62, hspace=.42, top=.9, bottom=.07)
    cb = fig.colorbar(sm, cax=fig.add_axes([0.945, 0.35, 0.008, 0.3]))
    cb.set_label("P(B | A)  (%)", fontsize=12)
    fig.suptitle(title, fontsize=22, x=0.01, ha="left", y=0.985, color=th["text"])
    fig.text(0.01, 0.945, "Fila = técnica condicionante A (con n(A)); columna = resultado B. Celdas con hachurado gris: n(A) < 20. Celdas pálidas: IC95 % más ancho que 0,3. "
             "Técnicas ordenadas por agrupamiento jerárquico sobre 1 − phi. † recall < 0,85 en validación; ‡ precisión < 0,80; ° sin validar (sin positivos en el conjunto de validación).",
             fontsize=11, color=th["text2"], ha="left", wrap=True)
    save(fig, "fig1_matriz_P_B_dado_A")


# ----------------------------------------------------------------------------------------------
# HTML interactivo: plantilla con modo claro/oscuro
# ----------------------------------------------------------------------------------------------
PAGE = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{--bg:#f9f9f7;--surface:#fcfcfb;--text:#0b0b0b;--text2:#52514e;--border:rgba(11,11,11,.10)}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0d0d0d;--surface:#1a1a19;--text:#fff;--text2:#c3c2b7;--border:rgba(255,255,255,.10)}}}}
:root[data-theme="dark"]{{--bg:#0d0d0d;--surface:#1a1a19;--text:#fff;--text2:#c3c2b7;--border:rgba(255,255,255,.10)}}
body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:16px}}
h1{{font-size:20px;margin:8px 0 4px}} p.sub{{color:var(--text2);margin:0 0 12px;max-width:110ch}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:8px}}
button{{background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:6px 10px;cursor:pointer}}
#cell{{margin-top:12px;color:var(--text2);word-break:break-word}} #cell a{{color:inherit;text-decoration:underline}}
</style></head><body><main>
<div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start"><div><h1>{title}</h1><p class="sub">{sub}</p></div>
<button id="tg" aria-label="Cambiar tema claro u oscuro">Tema claro/oscuro</button></div>
<div class="card"><div id="plot" style="width:100%;height:{height}px"></div></div>
<div id="cell" class="card" hidden></div>
<script>{plotly}</script>
<script>
const FIG={{light:{light},dark:{dark}}}; const CELLS={cells};
function theme(){{const t=document.documentElement.getAttribute('data-theme'); if(t) return t; return matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}}
function draw(){{const f=FIG[theme()]; Plotly.react('plot',f.data,f.layout,{{responsive:true,displaylogo:false}}); }}
draw();
document.getElementById('tg').onclick=()=>{{document.documentElement.setAttribute('data-theme',theme()==='dark'?'light':'dark');draw()}};
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',draw);
document.getElementById('plot').on?.('plotly_click',e=>{{}});
(function(){{const el=document.getElementById('plot');
 const bind=()=>{{ if(!el.on){{setTimeout(bind,100);return}} el.on('plotly_click',ev=>{{const p=ev.points[0]; const cd=p.customdata; if(!cd||!CELLS) return;
   const st=cd[0],A=cd[1],B=cd[2]; const key=[A,B].sort().join('|'); const ids=(CELLS[st]||{{}})[key]||[]; const box=document.getElementById('cell'); box.hidden=false;
   box.innerHTML='<b>'+st+': '+A+' y '+B+'</b> — '+ids.length+' artículos con ambas técnicas. '+ids.slice(0,300).map(i=>'<a href="https://europepmc.org/article/PMC/'+i+'" target="_blank" rel="noopener">'+i+'</a>').join(', ')+(ids.length>300?' …':'');}})}}; bind();}})();
</script></body></html>"""


def write_html(name, title, sub, figs: dict, height=900, cells=None):
    html = PAGE.format(title=title, sub=sub, height=height, plotly=get_plotlyjs(), light=figs["light"].to_json(), dark=figs["dark"].to_json(),
                       cells=json.dumps(cells) if cells else "null")
    (FIGS / f"{name}.html").write_text(html, encoding="utf-8")


def plotly_layout(theme, fig, height, title=None):
    t = THEMES[theme]
    fig.update_layout(height=height, paper_bgcolor=t["surface"], plot_bgcolor=t["surface"], font=dict(color=t["text2"], family="system-ui,Segoe UI,sans-serif", size=12),
                      margin=dict(l=10, r=10, t=40 if title else 10, b=10), hoverlabel=dict(bgcolor=t["surface"], font_color=t["text"], bordercolor=t["axis"]))


def fig1_html(c: Ctx, title: str):
    cells = {}
    for st in PANELS:
        p = DATA / "cell_pmcids" / f"{st}.csv"
        if p.exists():
            d = pd.read_csv(p)
            cells[st] = {"|".join(sorted([r.A, r.B])): r.pmcids.split("|") for r in d.itertuples()}
    figs = {}
    for theme in ("light", "dark"):
        th = THEMES[theme]
        fig = make_subplots(rows=2, cols=4, subplot_titles=[FAM_LABEL[s] for s in PANELS], horizontal_spacing=.045, vertical_spacing=.12)
        for idx, st in enumerate(PANELS):
            r, col = idx // 4 + 1, idx % 4 + 1
            P = c.mat(st, "P_B_given_A")
            lo, hi, nAB = c.mat(st, "ci_lo"), c.mat(st, "ci_hi"), c.mat(st, "nAB")
            lift, padj = c.mat(st, "lift"), c.mat(st, "p_adj_bh")
            nA = c.nA(st)
            k = len(c.order)
            custom = np.empty((k, k), dtype=object)
            for i in range(k):
                for j in range(k):
                    custom[i, j] = [st, c.order[i], c.order[j], f"{100 * P[i, j]:.1f}" if P[i, j] == P[i, j] else "n.d.",
                                    f"{100 * lo[i, j]:.0f}–{100 * hi[i, j]:.0f}" if P[i, j] == P[i, j] else "", int(nAB[i, j]) if nAB[i, j] == nAB[i, j] else 0,
                                    int(nA[i]), f"{lift[i, j]:.2f}" if lift[i, j] == lift[i, j] else "n.d.", f"{padj[i, j]:.3g}" if padj[i, j] == padj[i, j] else "n.d."]
            ok = np.array([[(i != j) and nA[i] >= 20 and P[i, j] == P[i, j] for j in range(k)] for i in range(k)])
            wide = ok & ((hi - lo) > 0.3)
            ylabs = [f"{c.label(t)}  n={n}" for t, n in zip(c.order, nA)]
            xlabs = [c.label(t) for t in c.order]
            ht = ("<b>%{customdata[1]} → %{customdata[2]}</b> (" + FAM_LABEL[st] + ")<br>P(B|A) = %{customdata[3]} %  IC95 % [%{customdata[4]}]"
                  "<br>n(A∧B) = %{customdata[5]} de n(A) = %{customdata[6]}<br>lift = %{customdata[7]}  ·  p ajustado (BH) = %{customdata[8]}<extra></extra>")
            cs = [[i / (len(th["seq"]) - 1), col_] for i, col_ in enumerate(th["seq"])]
            for mask, tcol in ((ok & (P < .5), th["text"]), (ok & (P >= .5), "#ffffff")):
                z = np.where(mask, P, np.nan)
                fig.add_trace(go.Heatmap(z=z, x=xlabs, y=ylabs, zmin=0, zmax=1, colorscale=cs, showscale=False, xgap=1, ygap=1,
                                         texttemplate="%{z:.0%}", textfont=dict(size=8, color=tcol), customdata=custom, hovertemplate=ht), row=r, col=col)
            low = np.where((~ok) & ~np.eye(k, dtype=bool), 1.0, np.nan)
            fig.add_trace(go.Heatmap(z=low, x=xlabs, y=ylabs, zmin=0, zmax=1, colorscale=[[0, th["gray"]], [1, th["gray"]]], showscale=False, xgap=1, ygap=1,
                                     customdata=custom, hovertemplate="<b>%{customdata[1]} → %{customdata[2]}</b><br>n(A) = %{customdata[6]} < 20: celda no mostrada<extra></extra>"),
                          row=r, col=col)
            fig.add_trace(go.Heatmap(z=np.where(wide, 1.0, np.nan), x=xlabs, y=ylabs, zmin=0, zmax=1, opacity=.55,
                                     colorscale=[[0, th["surface"]], [1, th["surface"]]], showscale=False, xgap=1, ygap=1, hoverinfo="skip"), row=r, col=col)
            fig.update_yaxes(autorange="reversed", tickfont=dict(size=8), row=r, col=col, showgrid=False)
            fig.update_xaxes(tickangle=60, tickfont=dict(size=8), row=r, col=col, showgrid=False)
        plotly_layout(theme, fig, 1500)
        fig.update_annotations(font=dict(size=14, color=th["text"]))
        figs[theme] = fig
    write_html("fig1_matriz_P_B_dado_A", title, "Haz clic en una celda para ver los PMCID de los artículos que tienen ambas técnicas. Celdas grises: n(A) < 20; celdas pálidas: IC95 % más ancho que 0,3.", figs, 1500, cells)


# ----------------------------------------------------------------------------------------------
# Figura 2 - divergente
# ----------------------------------------------------------------------------------------------

def _signed_log2(x):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.clip(np.log2(x), -3, 3)


def fig2_static(c: Ctx, title: str):
    setup_mpl("light")
    th = THEMES["light"]
    cmap = cmap_for("light", "div")
    fig, axes = plt.subplots(2, 4, figsize=(34, 19.5))
    panels = ["ALL"] + PANELS[1:]
    for ax, st in zip(axes.ravel(), panels):
        if st == "ALL":
            Z, pa = _signed_log2(c.mat("ALL", "MH_OR")), c.mat("ALL", "MH_p_adj")
            sub = "OR de Mantel-Haenszel por familia, log₂"
        else:
            Z, pa = _signed_log2(c.mat(st, "lift")), c.mat(st, "p_adj_bh")
            sub = "lift, log₂"
        nA = c.nA(st)
        k = len(c.order)
        for i in range(k):
            for j in range(k):
                if i == j:
                    continue
                v = Z[i, j]
                if np.isnan(v) or nA[i] < 20:
                    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, facecolor=th["gray"], hatch="////", edgecolor=th["surface"], linewidth=.6))
                    continue
                ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, facecolor=cmap((v + 3) / 6), edgecolor=th["surface"], linewidth=.6))
                if pa[i, j] == pa[i, j] and pa[i, j] < 0.05:
                    ax.text(j, i, "*", ha="center", va="center", fontsize=13, color=th["text"] if abs(v) < 1.6 else "white")
        ax.set_xlim(-.5, k - .5); ax.set_ylim(k - .5, -.5)
        ax.set_xticks(range(k)); ax.set_xticklabels([c.label(t) for t in c.order], rotation=60, ha="right", fontsize=10)
        ax.set_yticks(range(k)); ax.set_yticklabels([f"{c.label(t)}  n={n}" for t, n in zip(c.order, nA)], fontsize=10)
        ax.set_title(f"{FAM_LABEL[st]}: {sub}", fontsize=14, loc="left")
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(length=0)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(-3, 3))
    fig.subplots_adjust(left=.07, right=.93, wspace=.62, hspace=.42, top=.9, bottom=.07)
    cb = fig.colorbar(sm, cax=fig.add_axes([0.945, 0.35, 0.008, 0.3]))
    cb.set_label("log₂  (azul: B más probable de lo esperado dado A; rojo: menos probable)", fontsize=12)
    fig.suptitle(title, fontsize=22, x=0.01, ha="left", y=0.985)
    fig.text(0.01, 0.945, "* FDR < 5 % (Benjamini-Hochberg). Panel 'Todas': OR de Mantel-Haenszel estratificado por familia, que corrige la paradoja de Simpson; "
             "paneles por familia: lift. Valores recortados a ±3. Hachurado: n(A) < 20.", fontsize=11, color=th["text2"], ha="left")
    save(fig, "fig2_divergente_lift_logOR")


def fig2_html(c: Ctx, title: str):
    figs = {}
    panels = ["ALL"] + PANELS[1:]
    for theme in ("light", "dark"):
        th = THEMES[theme]
        fig = make_subplots(rows=2, cols=4, subplot_titles=[FAM_LABEL[s] + (" (MH)" if s == "ALL" else " (lift)") for s in panels], horizontal_spacing=.045, vertical_spacing=.12)
        cs = [[0, DIV_NEG[theme]], [.5, th["mid"]], [1, DIV_POS[theme]]]
        for idx, st in enumerate(panels):
            r, col = idx // 4 + 1, idx % 4 + 1
            if st == "ALL":
                raw, pa = c.mat("ALL", "MH_OR"), c.mat("ALL", "MH_p_adj")
            else:
                raw, pa = c.mat(st, "lift"), c.mat(st, "p_adj_bh")
            Z = _signed_log2(raw)
            nA = c.nA(st)
            k = len(c.order)
            Z = np.where((nA[:, None] >= 20) & ~np.eye(k, dtype=bool), Z, np.nan)
            text = np.where((pa < .05) & ~np.isnan(Z), "*", "")
            custom = np.empty((k, k), dtype=object)
            for i in range(k):
                for j in range(k):
                    custom[i, j] = [st, c.order[i], c.order[j], f"{raw[i, j]:.2f}" if raw[i, j] == raw[i, j] else "n.d.", f"{pa[i, j]:.3g}" if pa[i, j] == pa[i, j] else "n.d.", int(nA[i])]
            fig.add_trace(go.Heatmap(z=Z, x=[c.label(t) for t in c.order], y=[f"{c.label(t)}  n={n}" for t, n in zip(c.order, nA)], zmin=-3, zmax=3, colorscale=cs,
                                     showscale=(idx == 0), colorbar=dict(title="log₂", len=.4, y=.8), text=text, texttemplate="%{text}", textfont=dict(size=12),
                                     xgap=1, ygap=1, customdata=custom,
                                     hovertemplate="<b>%{customdata[1]} → %{customdata[2]}</b> (" + FAM_LABEL[st] + ")<br>" + ("OR MH" if st == "ALL" else "lift") +
                                                   " = %{customdata[3]}<br>p ajustado (BH) = %{customdata[4]}<br>n(A) = %{customdata[5]}<extra></extra>"), row=r, col=col)
            fig.update_yaxes(autorange="reversed", tickfont=dict(size=8), row=r, col=col, showgrid=False)
            fig.update_xaxes(tickangle=60, tickfont=dict(size=8), row=r, col=col, showgrid=False)
        plotly_layout(theme, fig, 1500)
        fig.update_annotations(font=dict(size=14, color=th["text"]))
        figs[theme] = fig
    write_html("fig2_divergente_lift_logOR", title, "Azul: B más probable de lo esperado dado A; rojo: menos probable. * FDR < 5 %. Panel 'Todas': OR de Mantel-Haenszel por familia.", figs, 1500)


# ----------------------------------------------------------------------------------------------
# Figura 3 - red
# ----------------------------------------------------------------------------------------------

def fig3(c: Ctx, title: str):
    setup_mpl("light")
    th = THEMES["light"]
    sub = c.pairs[(c.pairs.stratum == "ALL") & (c.pairs.A < c.pairs.B) & (c.pairs.phi > 0.2) & (c.pairs.p_adj_bh < 0.05)]
    G = nx.Graph()
    prev = c.prev[c.prev.stratum == "ALL"].set_index("technique")["prevalence"]
    for r in sub.itertuples():
        G.add_edge(r.A, r.B, phi=r.phi, dist=1.0 / max(r.phi, 0.05))
    for t in G.nodes:
        G.nodes[t]["prev"] = float(prev.get(t, 0))
    isolated = [t for t in c.techs if t not in G.nodes]
    comps = sorted(nx.connected_components(G), key=len, reverse=True)
    pos = {}
    for ci, comp in enumerate(comps):
        H = G.subgraph(comp)
        if len(comp) >= 3:
            local = nx.kamada_kawai_layout(H, weight="dist", scale=1.0)
        else:
            a, b = list(comp)
            local = {a: np.array([-.25, 0.0]), b: np.array([.25, 0.0])}
        off = np.array([0.0, 0.0]) if ci == 0 else np.array([1.9, 1.0 - 0.9 * (ci - 1)])
        for n_, v_ in local.items():
            pos[n_] = np.asarray(v_) + off
    fig, ax = plt.subplots(figsize=(13, 10))
    colors = {g: th["cat"][i] for i, g in enumerate(GROUP_ORDER[:4])}
    colors["Otras"] = th["muted"]
    for u, v, d in G.edges(data=True):
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color=th["axis"], lw=1 + 14 * d["phi"], alpha=.9, zorder=1, solid_capstyle="round")
    for t in G.nodes:
        ax.scatter(*pos[t], s=200 + 2600 * G.nodes[t]["prev"], color=colors[c.cat[t]], edgecolor=th["surface"], linewidth=2, zorder=3)
        ax.annotate(c.label(t), pos[t], ha="center", va="center", fontsize=11, color=th["text"], zorder=4,
                    xytext=(0, -14 - 22 * math.sqrt(G.nodes[t]["prev"])), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.15", fc=th["surface"], ec="none", alpha=.8))
    ax.axis("off")
    handles = [plt.Line2D([], [], marker="o", color="none", markerfacecolor=colors[g], markersize=11, label=g) for g in GROUP_ORDER if g in set(c.cat.values())]
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=11)
    fig.suptitle(textwrap.fill(title, 95), x=0.01, ha="left", fontsize=16)
    iso = ", ".join(c.label(t) for t in isolated)
    fig.text(0.01, 0.01, "Nodo: tamaño proporcional a la prevalencia (muestra completa); arista: phi > 0,2 y FDR < 5 % (grosor proporcional a phi).\n"
             f"Sin ninguna arista (no se dibujan): {iso}.", fontsize=10, color=th["text2"], va="bottom")
    save(fig, "fig3_red_de_tecnicas")


# ----------------------------------------------------------------------------------------------
# Figura 4 - UpSet
# ----------------------------------------------------------------------------------------------

def fig4(c: Ctx, title: str):
    setup_mpl("light")
    th = THEMES["light"]
    pats = pd.read_csv(DATA / "patterns.csv")
    fig = plt.figure(figsize=(30, 17))
    outer = fig.add_gridspec(2, 4, wspace=.18, hspace=.3)
    for idx, st in enumerate(PANELS):
        sub = pats[pats.stratum == st].sort_values("count", ascending=False).head(15)
        gs = outer[idx // 4, idx % 4].subgridspec(2, 1, height_ratios=[3, 2.2], hspace=.05)
        axb, axd = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
        if sub.empty:
            axb.axis("off"); axd.axis("off"); axb.set_title(f"{FAM_LABEL[st]}: sin patrones", loc="left"); continue
        sets = [p.split(" + ") for p in sub["pattern"]]
        techs_used = sorted({t for s in sets for t in s}, key=lambda t: -sum(t in s for s in sets))
        n_total = int(c.pairs[c.pairs.stratum == st]["N"].iloc[0])
        axb.bar(range(len(sub)), 100 * sub["count"] / n_total, color=th["cat"][0], width=.7)
        for i, v in enumerate(sub["count"]):
            axb.text(i, 100 * v / n_total, f"{v}", ha="center", va="bottom", fontsize=9, color=th["text"])
        axb.set_xticks([]); axb.set_ylabel("% de artículos", fontsize=10)
        axb.set_title(f"{FAM_LABEL[st]} (N = {n_total})", loc="left", fontsize=14)
        for sp in ("top", "right"):
            axb.spines[sp].set_visible(False)
        for yi, t in enumerate(techs_used):
            axd.axhline(yi, color=th["grid"], lw=7, zorder=0)
        for xi, s in enumerate(sets):
            ys = [techs_used.index(t) for t in s]
            axd.plot([xi] * len(ys), ys, color=th["text2"], lw=2, zorder=1)
            axd.scatter([xi] * len(ys), ys, color=th["text"], s=60, zorder=2)
        axd.set_yticks(range(len(techs_used))); axd.set_yticklabels([c.label(t) for t in techs_used], fontsize=9)
        axd.set_xticks([]); axd.set_ylim(len(techs_used) - .5, -.5); axd.set_xlim(-.7, len(sub) - .3)
        for sp in axd.spines.values():
            sp.set_visible(False)
        axd.tick_params(length=0)
    fig.suptitle(title, fontsize=22, x=0.01, ha="left", y=0.99)
    fig.text(0.01, 0.935, "Combinación exacta de técnicas (definición 'usada o mostrada') por familia primaria; 15 combinaciones más frecuentes. Barra = % de los artículos de la familia (número = conteo).",
             fontsize=11, color=th["text2"])
    save(fig, "fig4_upset_combinaciones")


# ----------------------------------------------------------------------------------------------
# Figura 5 - prevalencias
# ----------------------------------------------------------------------------------------------

def _prev_order(c: Ctx):
    p = c.prev[(c.prev.stratum == "ALL") & c.prev.technique.isin(c.techs)].sort_values("prevalence", ascending=False)
    return list(p.technique)


def fig5_static(c: Ctx, title: str):
    setup_mpl("light")
    th = THEMES["light"]
    order = _prev_order(c)
    fig, axes = plt.subplots(2, 4, figsize=(26, 16), sharey=True)
    for ax, st in zip(axes.ravel(), PANELS):
        d = c.prev[c.prev.stratum == st].set_index("technique").loc[order]
        y = np.arange(len(order))
        col = [th["cat"][["Microscopía", "Dispersión de luz", "Espectroscopía y difracción", "Térmica", "Otras"].index(c.cat[t])] if c.cat[t] != "Otras" else th["muted"] for t in order]
        ax.barh(y, 100 * d["prevalence"], color=col, height=.62)
        ax.errorbar(100 * d["prevalence"], y, xerr=[100 * (d["prevalence"] - d["ci_lo"]).clip(lower=0), 100 * (d["ci_hi"] - d["prevalence"]).clip(lower=0)],
                    fmt="none", ecolor=th["text2"], elinewidth=1.2, capsize=2)
        ax.set_yticks(y); ax.set_yticklabels([c.label(t) for t in order], fontsize=10)
        ax.invert_yaxis(); ax.set_xlim(0, 100)
        n = int(d["n"].iloc[0])
        ax.set_title(f"{FAM_LABEL[st]} (N = {n})", loc="left", fontsize=14)
        ax.set_xlabel("Prevalencia (%) con IC95 % de Wilson", fontsize=10)
        ax.grid(axis="x", color=th["grid"], lw=.8); ax.set_axisbelow(True)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(length=0)
    handles = [plt.Line2D([], [], marker="s", color="none", markerfacecolor=th["cat"][i] if g != "Otras" else th["muted"], markersize=11, label=g)
               for i, g in enumerate(GROUP_ORDER) if g in set(c.cat.values())]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, fontsize=12)
    fig.suptitle(title, fontsize=22, x=0.01, ha="left", y=1.0)
    save(fig, "fig5_prevalencia_marginal")


def fig5_html(c: Ctx, title: str):
    order = _prev_order(c)
    figs = {}
    for theme in ("light", "dark"):
        th = THEMES[theme]
        fig = go.Figure()
        for i, st in enumerate(PANELS):
            d = c.prev[c.prev.stratum == st].set_index("technique").loc[order]
            fig.add_trace(go.Bar(y=[c.label(t) for t in order], x=100 * d["prevalence"], orientation="h", name=FAM_LABEL[st], visible=True if st == "ALL" else "legendonly",
                                 marker_color=th["cat"][i % 8],
                                 error_x=dict(type="data", symmetric=False, array=100 * (d["ci_hi"] - d["prevalence"]).clip(lower=0),
                                              arrayminus=100 * (d["prevalence"] - d["ci_lo"]).clip(lower=0), color=th["text2"], thickness=1.2),
                                 customdata=np.column_stack([d["k"], d["n"], 100 * d["ci_lo"], 100 * d["ci_hi"]]),
                                 hovertemplate="<b>%{y}</b> (" + FAM_LABEL[st] + ")<br>%{x:.1f} %  IC95 % [%{customdata[2]:.1f}–%{customdata[3]:.1f}]<br>%{customdata[0]} de %{customdata[1]} artículos<extra></extra>"))
        plotly_layout(theme, fig, 800)
        fig.update_layout(barmode="group", yaxis=dict(autorange="reversed"), xaxis=dict(title="Prevalencia (%) — clic en la leyenda para comparar familias", gridcolor=th["grid"], range=[0, 100]),
                          legend=dict(orientation="h", y=1.06))
        figs[theme] = fig
    write_html("fig5_prevalencia_marginal", title, "Barras con IC95 % de Wilson. Active o desactive familias en la leyenda.", figs, 800)


# ----------------------------------------------------------------------------------------------
# Figura 6 - fila EM para la base de datos
# ----------------------------------------------------------------------------------------------

def _em_items(c: Ctx):
    e = c.em[(c.em.stratum == "ALL") & ~c.em.what.str.startswith("same_figure") & (c.em.what != "micrograph+spectrum_same_figure")]
    keep = [t for t in e.sort_values("P", ascending=False).what if t in c.techs][:16]
    return keep


def fig6_static(c: Ctx, title: str):
    setup_mpl("light")
    th = THEMES["light"]
    cmap = cmap_for("light")
    fams = FAMILY_ORDER
    items = _em_items(c) + ["micrograph+spectrum_same_figure"]
    fig, ax = plt.subplots(figsize=(13, 11))
    for xi, f in enumerate(fams):
        for yi, w in enumerate(items):
            r = c.em[(c.em.stratum == f) & (c.em.what == w)]
            if r.empty:
                continue
            r = r.iloc[0]
            if r.n_EM < 20 or r.P != r.P:
                ax.add_patch(plt.Rectangle((xi - .5, yi - .5), 1, 1, facecolor=th["gray"], hatch="////", edgecolor=th["surface"], linewidth=.8))
                continue
            wide = (r.ci_hi - r.ci_lo) > 0.3
            ax.add_patch(plt.Rectangle((xi - .5, yi - .5), 1, 1, facecolor=cmap(r.P), alpha=.5 if wide else 1, edgecolor=th["surface"], linewidth=.8))
            ax.text(xi, yi, f"{100 * r.P:.0f}", ha="center", va="center", fontsize=10, color="white" if (r.P >= .5 and not wide) else th["text"])
    ax.set_xlim(-.5, len(fams) - .5); ax.set_ylim(len(items) - .5, -.5)
    nEM = [int(c.em[(c.em.stratum == f)].n_EM.iloc[0]) if (c.em.stratum == f).any() else 0 for f in fams]
    ax.set_xticks(range(len(fams))); ax.set_xticklabels([f"{FAM_LABEL[f]}\nn(EM) = {n}" for f, n in zip(fams, nEM)], fontsize=11)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([("Micrografía + espectro en la misma figura" if w == "micrograph+spectrum_same_figure" else c.label(w)) for w in items], fontsize=11)
    ax.axhline(len(items) - 1.5, color=th["text2"], lw=1)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 100))
    fig.colorbar(sm, ax=ax, shrink=.5, pad=.02).set_label("% de los artículos con micrografía (cryo-EM, TEM, STEM, SEM o AFM)")
    ax.set_title(title, loc="left", fontsize=16, pad=70)
    fig.text(0.01, 0.01, "Celdas hachuradas: menos de 20 artículos con micrografía en la familia. Celdas pálidas: IC95 % más ancho que 0,3. 'Misma figura': el pie de una figura contiene un término de microscopía y uno de espectroscopía.",
             fontsize=9, color=th["text2"], wrap=True)
    save(fig, "fig6_fila_EM_para_la_base")


def fig6_html(c: Ctx, title: str):
    fams = FAMILY_ORDER
    items = _em_items(c) + ["micrograph+spectrum_same_figure"]
    figs = {}
    for theme in ("light", "dark"):
        th = THEMES[theme]
        z, txt, cd = [], [], []
        for w in items:
            zr, tr, cr = [], [], []
            for f in fams:
                r = c.em[(c.em.stratum == f) & (c.em.what == w)]
                if r.empty or r.iloc[0].n_EM < 20 or r.iloc[0].P != r.iloc[0].P:
                    zr.append(np.nan); tr.append(""); cr.append([f, w, "n(EM) < 20", "", "", ""])
                    continue
                r = r.iloc[0]
                zr.append(r.P); tr.append(f"{100 * r.P:.0f}")
                cr.append([f, w, f"{100 * r.P:.1f}", f"{100 * r.ci_lo:.0f}–{100 * r.ci_hi:.0f}", int(r.k), int(r.n_EM)])
            z.append(zr); txt.append(tr); cd.append(cr)
        cs = [[i / (len(th["seq"]) - 1), col_] for i, col_ in enumerate(th["seq"])]
        fig = go.Figure(go.Heatmap(z=z, x=[FAM_LABEL[f] for f in fams], y=[("Micrografía + espectro en la misma figura" if w == "micrograph+spectrum_same_figure" else c.label(w)) for w in items],
                                   zmin=0, zmax=1, colorscale=cs, text=txt, texttemplate="%{text}", textfont=dict(size=11), xgap=2, ygap=2, customdata=cd,
                                   colorbar=dict(title="P", tickformat=".0%"),
                                   hovertemplate="<b>%{y}</b> en %{x}<br>P(·|EM) = %{customdata[2]} %  IC95 % [%{customdata[3]}]<br>%{customdata[4]} de %{customdata[5]} artículos con micrografía<extra></extra>"))
        plotly_layout(theme, fig, 780)
        fig.update_layout(yaxis=dict(autorange="reversed"), xaxis=dict(side="top"))
        figs[theme] = fig
    write_html("fig6_fila_EM_para_la_base", title, "Dado que el artículo tiene micrografía, probabilidad de que reporte también cada técnica. Gris: menos de 20 artículos con micrografía.", figs, 780)


# ----------------------------------------------------------------------------------------------
# Figura 7 - tendencia (secundaria)
# ----------------------------------------------------------------------------------------------

def fig7(c: Ctx, title: str):
    setup_mpl("light")
    th = THEMES["light"]
    techs = list(c.trend["technique"].unique())
    fig, axes = plt.subplots(2, 4, figsize=(22, 9), sharex=True, sharey=True)
    for ax, t in zip(axes.ravel(), techs):
        d = c.trend[c.trend.technique == t]
        ax.fill_between(d.year, 100 * d.ci_lo, 100 * d.ci_hi, color=th["cat"][0], alpha=.18, lw=0)
        ax.plot(d.year, 100 * d.prevalence, color=th["cat"][0], lw=2, marker="o", ms=5, mec=th["surface"], mew=1.5)
        p = d.CA_p.iloc[0]
        ax.set_title(f"{c.label(t)}   Cochran-Armitage p = {p:.2g}", loc="left", fontsize=12)
        ax.grid(color=th["grid"], lw=.8); ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    for ax in axes[1]:
        ax.set_xlabel("Año")
    for ax in axes[:, 0]:
        ax.set_ylabel("Prevalencia (%)")
    fig.suptitle(title, fontsize=18, x=0.01, ha="left")
    fig.text(0.01, 0.0, "Las 8 técnicas más frecuentes. 2015-2017 proviene de una submuestra pequeña (≈ 40 artículos por familia): sus IC son anchos. Banda: IC95 % de Wilson.", fontsize=10, color=th["text2"])
    save(fig, "fig7_tendencia_temporal")


# ----------------------------------------------------------------------------------------------
# Titulos-hallazgo calculados desde los datos
# ----------------------------------------------------------------------------------------------

def figure_titles(c: Ctx) -> dict:
    p = c.pairs
    allp = p[(p.stratum == "ALL") & ~p.low_n]

    def pc(st, a, b):
        r = p[(p.stratum == st) & (p.A == a) & (p.B == b)]
        return 100 * float(r.P_B_given_A.iloc[0]) if len(r) and r.P_B_given_A.iloc[0] == r.P_B_given_A.iloc[0] else float("nan")

    t = {}
    t["fig1"] = (f"Dado TEM, el DLS aparece en {pc('ORGANIC', 'TEM', 'DLS'):.0f} % de los artículos orgánicos, pero solo en {pc('inorganic', 'TEM', 'DLS'):.0f} % de los inorgánicos; "
                 f"la matriz de co-ocurrencia depende de la familia")
    mh = p[(p.stratum == "ALL") & (p.MH_p_adj < 0.05) & ~p.low_n]
    n_up, n_dn = int((mh.MH_OR > 1).sum()), int((mh.MH_OR < 1).sum())
    t["fig2"] = f"Tras estratificar por familia, {n_up} pares ordenados son más frecuentes de lo esperado y {n_dn} menos (FDR < 5 %)"
    pa = p[(p.stratum == "ALL") & (p.A < p.B)]
    top = pa[pa.p_adj_bh < 0.05].sort_values("phi", ascending=False).head(1)
    tp = f"{top.A.iloc[0]}–{top.B.iloc[0]} (phi = {top.phi.iloc[0]:.2f})" if len(top) else "sin pares"
    n_edge = int(((pa.phi > 0.2) & (pa.p_adj_bh < 0.05)).sum())
    t["fig3"] = f"La asociación más fuerte entre técnicas es {tp}; solo {n_edge} de {len(pa)} parejas superan phi = 0,2 con FDR < 5 %"
    pats = pd.read_csv(DATA / "patterns.csv")
    pa_ = pats[pats.stratum == "ALL"].sort_values("count", ascending=False)
    if len(pa_):
        n_all = int(p[p.stratum == "ALL"]["N"].iloc[0])
        nfam = p[p.stratum.isin(FAMILY_ORDER)].groupby("stratum")["N"].first()
        po = pats[pats.stratum.isin([f for f in FAMILY_ORDER if f != "AAV"])].copy()
        po["pct"] = [100 * r.count / nfam[r.stratum] for r in po.itertuples()]
        t["fig4"] = (f"La combinación exacta más frecuente ({pa_.iloc[0]['pattern']} sola) cubre {100 * pa_.iloc[0]['count'] / n_all:.0f} % de los artículos; "
                     f"fuera de AAV ninguna combinación supera {po.pct.max():.0f} % de su familia: hay muchas combinaciones distintas")
    else:
        t["fig4"] = "Combinaciones de técnicas más frecuentes por familia"
    top_prev = c.prev[(c.prev.stratum == "ALL") & c.prev.technique.isin(c.techs)].sort_values("prevalence", ascending=False).head(3)
    t["fig5"] = "Prevalencia marginal: " + ", ".join(f"{r.technique} {100 * r.prevalence:.0f} %" for r in top_prev.itertuples()) + " son las técnicas más reportadas; lo demás varía mucho por familia"
    e = c.em[(c.em.stratum == "ALL") & (c.em.what == "micrograph+spectrum_same_figure")]
    share = 100 * float(e.P.iloc[0]) if len(e) else float("nan")
    t["fig6"] = f"Entre artículos con micrografía, solo {share:.0f} % muestra micrografía y espectro en la misma figura: pocos pares imagen-espectro son directos"
    t["fig7"] = "Tendencia 2015-2026 de las 8 técnicas más frecuentes (prueba de Cochran-Armitage)"
    return t


def main() -> None:
    FIGS.mkdir(exist_ok=True)
    c = Ctx()
    T = figure_titles(c)
    (FIGS / "titles.json").write_text(json.dumps(T, ensure_ascii=False, indent=1), encoding="utf-8")
    fig1_static(c, T["fig1"]); fig1_html(c, T["fig1"])
    fig2_static(c, T["fig2"]); fig2_html(c, T["fig2"])
    fig3(c, T["fig3"])
    fig4(c, T["fig4"])
    fig5_static(c, T["fig5"]); fig5_html(c, T["fig5"])
    fig6_static(c, T["fig6"]); fig6_html(c, T["fig6"])
    fig7(c, T["fig7"])
    print("figuras listas en", FIGS)


if __name__ == "__main__":
    main()
