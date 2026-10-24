"""Cuánto de lo que ve el modelo de clase son figuras simples, parejas o compuestas, y cómo rinde en cada grupo.

Une las predicciones por imagen (embeddings congelados y ajuste fino, validación por artículo) con la tipología del pie.
IC 95 % por bootstrap de artículos (las imágenes de un artículo no son independientes). No entrena nada.
Uso: python modelos/tipologia_figuras/impacto_en_modelo.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
K = RAIZ / "modelos/comparacion/entrada_kabre"
PRED = {"ResNet50 congelado": K / "predicciones_resnet50.csv", "DINOv2 congelado": K / "predicciones_dinov2_vits14.csv",
        "ResNet50 ajuste fino": K / "03_ajuste_fino/predicciones_ft_resnet50.csv", "DINOv2 ajuste fino": K / "03_ajuste_fino/predicciones_ft_dinov2_vits14.csv"}
GRUPOS = {"simple": ["micro_unica", "espectro_unico"], "pareja": ["pareja_micro", "pareja_micro_espectro", "pareja_espectro"],
          "micro_multiple_sin_etiquetas": ["micro_multiple_sin_etiquetas"],
          "compuesta": ["compuesta_micro", "compuesta_mixta", "compuesta_espectro", "compuesta_con_otros", "una_util_con_otros"],
          "superpuesto": ["espectro_superpuesto"], "sin_micro_ni_espectro": ["sin_micro_ni_espectro", "solo_descriptores"]}
INV = {t: g for g, ts in GRUPOS.items() for t in ts}
rng = np.random.default_rng(20261023)

tip = pd.read_csv(OUT / "tipologia_figuras.csv", dtype=str, encoding="utf-8-sig")[["pmcid", "archivo_grafico", "tipologia", "n_paneles_pie", "n_micro", "n_espectro"]]
tip = tip.drop_duplicates(["pmcid", "archivo_grafico"])
tip["grupo"] = tip.tipologia.map(INV)
tip["contenido"] = np.select([(tip.n_micro.astype(int) > 0) & (tip.n_espectro.astype(int) == 0), (tip.n_micro.astype(int) > 0), tip.n_espectro.astype(int) > 0],
                             ["solo_micrografias", "micrografias_y_espectros", "solo_espectros"], "ni_micro_ni_espectro")


def boot(df, n=1000):
    arts = df.groupby("pmcid").acierto.agg(["sum", "count"])
    s, c = arts["sum"].to_numpy(), arts["count"].to_numpy()
    idx = rng.integers(0, len(arts), (n, len(arts)))
    acc = s[idx].sum(1) / c[idx].sum(1)
    return float(np.percentile(acc, 2.5)), float(np.percentile(acc, 97.5))


res, md = {}, ["# Rendimiento del modelo de clase según el tipo de figura (por el pie)", "",
               "Validación por artículo. IC 95 % por bootstrap de artículos. `n` = imágenes. Los grupos se asignan solo con el texto del pie (estimación, no verdad humana).", ""]
for nombre, f in PRED.items():
    p = pd.read_csv(f, dtype={"pmcid": str, "image_file": str}, encoding="utf-8-sig")
    p["acierto"] = (p.real == p.prediccion).astype(int)
    m = p.merge(tip, left_on=["pmcid", "image_file"], right_on=["pmcid", "archivo_grafico"], how="left")
    m["grupo"] = m.grupo.fillna("sin_pie_en_inventario")
    fila = {"n": int(len(m)), "acc_global": round(float(m.acierto.mean()), 3), "grupos": {}}
    md += [f"## {nombre} (n = {len(m)}, exactitud global {m.acierto.mean():.1%})", "", "| Grupo | n | % del total | Exactitud | IC 95 % |", "|---|---:|---:|---:|---|"]
    for g, d in m.groupby("grupo"):
        lo, hi = boot(d)
        fila["grupos"][g] = {"n": int(len(d)), "acc": round(float(d.acierto.mean()), 3), "ic95": [round(lo, 3), round(hi, 3)]}
        md.append(f"| {g} | {len(d)} | {len(d)/len(m):.1%} | {d.acierto.mean():.1%} | {lo:.1%}–{hi:.1%} |")
    md.append("")
    m["contenido"] = m.contenido.fillna("sin_pie_en_inventario")
    md += ["Por contenido (qué dice el pie que hay en la figura):", "", "| Contenido | n | % del total | Exactitud | IC 95 % |", "|---|---:|---:|---:|---|"]
    fila["contenido"] = {}
    for g, d in m.groupby("contenido"):
        lo, hi = boot(d)
        fila["contenido"][g] = {"n": int(len(d)), "acc": round(float(d.acierto.mean()), 3), "ic95": [round(lo, 3), round(hi, 3)]}
        md.append(f"| {g} | {len(d)} | {len(d)/len(m):.1%} | {d.acierto.mean():.1%} | {lo:.1%}–{hi:.1%} |")
    md.append("")
    res[nombre] = fila
(OUT / "impacto_en_modelo.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "IMPACTO_EN_MODELO.md").write_text("\n".join(md), encoding="utf-8")
print("\n".join(md))
