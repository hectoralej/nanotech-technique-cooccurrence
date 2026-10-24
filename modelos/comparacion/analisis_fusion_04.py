"""Fusión tardía por artículo: imagen (recortes 04, o figura completa 03) + medidas (logística sobre descriptores), peso fijo 50/50 (decisión D24).
Imagen: promedio de ResNet50 y DINOv2, y de las vistas de cada artículo. Medidas: predicciones fuera de muestra de modelos/tabular_v2 (una fila por muestra; se promedian por artículo).
Todo con las mismas particiones por artículo. IC 95 % por bootstrap de artículos (2.000). Salida: ANALISIS_FUSION_04.md/.json
Uso: python modelos/comparacion/analisis_fusion_04.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(__file__).resolve().parent
RAIZ = D.parents[1]
E = D / "entrada_kabre"
CL = ["inorganico", "lipidico", "nanomaterial", "polimerico"]; PC = ["p_" + c for c in CL]
rng = np.random.default_rng(20261026)


def art(o):
    return o.groupby("pmcid").agg({**{c: "mean" for c in PC}, "real": "first", "fold": "first"})


def imagen(carpeta):
    ps = [art(pd.read_csv(E / carpeta / f"predicciones_ft_{m}.csv", encoding="utf-8-sig", dtype={"pmcid": str})) for m in ("resnet50", "dinov2_vits14")]
    com = ps[0].index.intersection(ps[1].index)
    g = ps[0].loc[com].copy(); g[PC] = (ps[0].loc[com, PC].values + ps[1].loc[com, PC].values) / 2
    return g


def metr(real, P):
    pred = np.array(CL)[P.argmax(1)]; real = np.asarray(real); f1 = []; rec = []
    for c in CL:
        tp = float(((pred == c) & (real == c)).sum()); pr = tp / max(1, (pred == c).sum()); re = tp / max(1, (real == c).sum())
        f1.append(0.0 if pr + re == 0 else 2 * pr * re / (pr + re)); rec.append(re)
    return {"acc": float((pred == real).mean()), "acc_bal": float(np.mean(rec)), "f1": float(np.mean(f1))}


def boot(real, A, B, n=2000):
    N = len(real); d = []
    for _ in range(n):
        i = rng.integers(0, N, N); a, b = metr(real[i], A[i]), metr(real[i], B[i]); d.append([a["acc"] - b["acc"], a["f1"] - b["f1"]])
    d = np.array(d)
    return {"acc": [float(np.percentile(d[:, 0], 2.5)), float(np.percentile(d[:, 0], 97.5))], "f1": [float(np.percentile(d[:, 1], 2.5)), float(np.percentile(d[:, 1], 97.5))]}


i4, i3 = imagen("04_recortes/A_todos"), imagen("03_ajuste_fino")
tab = pd.read_csv(RAIZ / "modelos/tabular_v2/resultados/predicciones_clase4_mediciones_logistica.csv", encoding="utf-8-sig", dtype={"pmcid": str})
tab = tab.rename(columns={"y_real": "real"}).groupby("pmcid").agg({**{c: "mean" for c in PC}, "real": "first", "fold": "first"})
com = i4.index.intersection(i3.index).intersection(tab.index)
i4, i3, tab = i4.loc[com], i3.loc[com], tab.loc[com]
real = i4.real.values; assert (real == i3.real.values).all() and (real == tab.real.values).all() and (i4.fold.values == tab.fold.values).all()
P = {"medidas": tab[PC].values, "imagen_03": i3[PC].values, "imagen_04": i4[PC].values}
P["fusion_03"] = (P["medidas"] + P["imagen_03"]) / 2; P["fusion_04"] = (P["medidas"] + P["imagen_04"]) / 2
res = {"n_articulos": int(len(com)), "linea_base_mayoritaria_acc": float(pd.Series(real).value_counts(normalize=True).max()), "modelos": {k: metr(real, v) for k, v in P.items()}, "diferencias": {}}
for a, b in (("imagen_04", "imagen_03"), ("fusion_04", "fusion_03"), ("fusion_04", "medidas"), ("fusion_03", "medidas"), ("medidas", "imagen_04")):
    res["diferencias"][f"{a} - {b}"] = {**{k: res["modelos"][a][k] - res["modelos"][b][k] for k in ("acc", "f1")}, "IC95": boot(real, P[a], P[b])}
nom = {"medidas": "Solo medidas (logística)", "imagen_03": "Imagen, figura completa (03)", "imagen_04": "Imagen, recortes (04)", "fusion_03": "Fusión medidas + imagen 03", "fusion_04": "Fusión medidas + imagen 04"}
md = ["# Fusión por artículo: medidas + imagen (recortes frente a figura completa)", "", f"{len(com)} artículos con medidas, figura completa y recortes. Particiones por artículo; fusión tardía 50/50; IC 95 % por bootstrap de artículos. Clase mayoritaria: exactitud {res['linea_base_mayoritaria_acc']:.3f}.", "",
      "| Modelo | Exactitud | Exactitud balanceada | F1 macro |", "|---|---:|---:|---:|"]
md += [f"| {nom[k]} | {v['acc']:.3f} | {v['acc_bal']:.3f} | {v['f1']:.3f} |" for k, v in res["modelos"].items()]
md += ["", "**Diferencias pareadas** (mismos remuestreos):", "", "| Comparación | Δ exactitud [IC 95 %] | Δ F1 macro [IC 95 %] |", "|---|---|---|"]
md += [f"| {k} | {v['acc']:+.3f} [{v['IC95']['acc'][0]:+.3f}, {v['IC95']['acc'][1]:+.3f}] | {v['f1']:+.3f} [{v['IC95']['f1'][0]:+.3f}, {v['IC95']['f1'][1]:+.3f}] |" for k, v in res["diferencias"].items()]
(D / "ANALISIS_FUSION_04.md").write_text("\n".join(md), encoding="utf-8"); (D / "ANALISIS_FUSION_04.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n".join(md))
