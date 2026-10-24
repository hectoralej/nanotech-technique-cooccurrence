"""Análisis del cuaderno 04 (recortes) frente al 03 (figura completa), por artículo, con intervalos por bootstrap de artículos y un control de «mismo número de vistas».
Entradas: entrada_kabre/04_recortes/A_todos/predicciones_ft_*.csv y entrada_kabre/03_ajuste_fino/predicciones_ft_*.csv. Salida: ANALISIS_04_RECORTES.md/.json en esta carpeta.
Uso: python modelos/comparacion/analisis_04_recortes.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(__file__).resolve().parent
E = D / "entrada_kabre"
CL = ["inorganico", "lipidico", "nanomaterial", "polimerico"]
PC = ["p_" + c for c in CL]
rng = np.random.default_rng(20261025)


def carga(ruta):
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype={"pmcid": str})


def por_art(o):
    g = o.groupby("pmcid").agg({**{c: "mean" for c in PC}, "real": "first", "fold": "first"})
    return g


def metr(real, P):
    pred = np.array(CL)[P.argmax(1)]
    real = np.asarray(real)
    acc = float((pred == real).mean())
    rec = [float((pred[real == c] == c).mean()) for c in CL if (real == c).any()]
    f1 = []
    for c in CL:
        tp = float(((pred == c) & (real == c)).sum()); pr = tp / max(1, (pred == c).sum()); re = tp / max(1, (real == c).sum())
        f1.append(0.0 if pr + re == 0 else 2 * pr * re / (pr + re))
    return acc, float(np.mean(rec)), float(np.mean(f1))


def boot_dif(real, Pa, Pb, n=2000):
    N = len(real); idx = rng.integers(0, N, (n, N)); d = []
    for i in idx:
        a, b = metr(real[i], Pa[i]), metr(real[i], Pb[i]); d.append([a[0] - b[0], a[2] - b[2]])
    d = np.array(d)
    return {"acc": [float(np.percentile(d[:, 0], 2.5)), float(np.percentile(d[:, 0], 97.5))], "f1": [float(np.percentile(d[:, 1], 2.5)), float(np.percentile(d[:, 1], 97.5))]}


res, md = {}, ["# Cuaderno 04 (recortes) frente al 03 (figura completa), por artículo", "",
               "Unidad: artículo (promedio de las probabilidades de sus recortes o figuras). IC 95 % por bootstrap de artículos (2.000 remuestreos). 5 particiones por artículo; última época.", ""]
P4, P3 = {}, {}
for m in ("resnet50", "dinov2_vits14"):
    o4 = carga(E / "04_recortes/A_todos" / f"predicciones_ft_{m}.csv"); o3 = carga(E / "03_ajuste_fino" / f"predicciones_ft_{m}.csv")
    a4, a3 = por_art(o4), por_art(o3); com = a4.index.intersection(a3.index)
    a4, a3 = a4.loc[com], a3.loc[com]
    real = a4.real.values; assert (real == a3.real.values).all()
    p4, p3 = a4[PC].values, a3[PC].values; P4[m], P3[m] = p4, p3
    m4, m3 = metr(real, p4), metr(real, p3)
    dif = boot_dif(real, p4, p3)
    # control: mismo número de vistas por artículo (k = nº de figuras del 03 para ese artículo)
    k = o3.groupby("pmcid").size().loc[com]
    g4 = {pm: x[PC].values for pm, x in o4.groupby("pmcid")}
    f1s, accs = [], []
    for _ in range(200):
        P = np.stack([g4[pm][rng.choice(len(g4[pm]), size=min(int(k[pm]), len(g4[pm])), replace=False)].mean(0) for pm in com])
        r = metr(real, P); accs.append(r[0]); f1s.append(r[2])
    res[m] = {"n_articulos": int(len(com)), "recortes": {"acc": m4[0], "acc_bal": m4[1], "f1": m4[2]}, "figura_completa_03": {"acc": m3[0], "acc_bal": m3[1], "f1": m3[2]},
              "diferencia_IC95": dif, "dif_acc": m4[0] - m3[0], "dif_f1": m4[2] - m3[2], "control_mismas_vistas": {"acc": float(np.mean(accs)), "f1": float(np.mean(f1s)), "vistas_medias_03": float(k.mean()), "vistas_medias_04": float(o4.groupby('pmcid').size().loc[com].mean())}}
    md += [f"## {m} ({len(com)} artículos comunes)", "", "| | Exactitud | Exactitud balanceada | F1 macro |", "|---|---:|---:|---:|",
           f"| Recortes (04), todas las vistas | {m4[0]:.3f} | {m4[1]:.3f} | {m4[2]:.3f} |", f"| Recortes (04), mismas vistas que el 03 (media de 200 sorteos) | {np.mean(accs):.3f} | – | {np.mean(f1s):.3f} |",
           f"| Figura completa (03) | {m3[0]:.3f} | {m3[1]:.3f} | {m3[2]:.3f} |", "",
           f"Diferencia recortes − 03: exactitud {m4[0] - m3[0]:+.3f} [IC {dif['acc'][0]:+.3f}, {dif['acc'][1]:+.3f}]; F1 macro {m4[2] - m3[2]:+.3f} [IC {dif['f1'][0]:+.3f}, {dif['f1'][1]:+.3f}]. Vistas por artículo: 03 = {k.mean():.2f}, 04 = {res[m]['control_mismas_vistas']['vistas_medias_04']:.2f}.", ""]
# promedio de los dos modelos
com_all = None
real = None
o4a, o3a = por_art(carga(E / "04_recortes/A_todos/predicciones_ft_resnet50.csv")), por_art(carga(E / "03_ajuste_fino/predicciones_ft_resnet50.csv"))
com = o4a.index.intersection(o3a.index); real = o4a.loc[com].real.values
pe4 = (P4["resnet50"] + P4["dinov2_vits14"]) / 2; pe3 = (P3["resnet50"] + P3["dinov2_vits14"]) / 2
m4, m3 = metr(real, pe4), metr(real, pe3); dif = boot_dif(real, pe4, pe3)
res["promedio"] = {"recortes": {"acc": m4[0], "f1": m4[2]}, "figura_completa_03": {"acc": m3[0], "f1": m3[2]}, "diferencia_IC95": dif}
md += ["## Promedio de ResNet50 y DINOv2", "", f"Recortes: exactitud {m4[0]:.3f}, F1 {m4[2]:.3f}. Figura completa (03): exactitud {m3[0]:.3f}, F1 {m3[2]:.3f}. Diferencia: exactitud {m4[0] - m3[0]:+.3f} [{dif['acc'][0]:+.3f}, {dif['acc'][1]:+.3f}], F1 {m4[2] - m3[2]:+.3f} [{dif['f1'][0]:+.3f}, {dif['f1'][1]:+.3f}].", "",
       f"Línea base (clase mayoritaria por artículo): exactitud {pd.Series(real).value_counts(normalize=True).max():.3f}.", ""]
(D / "ANALISIS_04_RECORTES.md").write_text("\n".join(md), encoding="utf-8")
(D / "ANALISIS_04_RECORTES.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n".join(md))
