"""Casi duplicados entre artículos distintos medidos con los vectores DINOv2 (más fiables que un hash de 8x8).

Entradas: vectores de Kabré (02_embeddings) y producto/imagenes. Salida: pares_similares_dinov2.csv, resumen_duplicados_dinov2.json, muestras/pares_dinov2_top.png
Uso: python modelos/auditoria_imagenes/duplicados_embeddings.py [carpeta_resultados_kabre] [umbral=0.97]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from sklearn.preprocessing import normalize

RAIZ = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
R = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Desktop" / "Kabre_Nano2Predict" / "Resultados"
U = float(sys.argv[2]) if len(sys.argv) > 2 else 0.97
idx = pd.read_csv(R / "indice_embeddings.csv")
X = normalize(np.load(R / "emb_dinov2_vits14.npy"))
S = X @ X.T
pm = idx.pmcid.to_numpy(dtype=object)
fold = idx.fold.astype(int).values
S[pm[:, None] == pm[None, :]] = -1                     # solo entre artículos distintos
iu = np.triu_indices(len(idx), 1)
v = S[iu]
res = {"umbral_coseno": U, "imagenes": int(len(idx))}
for u in (0.90, 0.95, 0.97, 0.98, 0.99):
    res[f"pares_cos_>={u}"] = int((v >= u).sum())
sel = v >= U
a, b, s = iu[0][sel], iu[1][sel], v[sel]
par = pd.DataFrame({"pmcid_a": pm[a], "imagen_a": idx.image_file.to_numpy(dtype=object)[a], "fold_a": fold[a], "pmcid_b": pm[b], "imagen_b": idx.image_file.to_numpy(dtype=object)[b], "fold_b": fold[b], "coseno": s.round(4)})
par["distinto_fold"] = par.fold_a != par.fold_b
par.sort_values("coseno", ascending=False).to_csv(OUT / "pares_similares_dinov2.csv", index=False, encoding="utf-8")
res["pares_en_distinto_fold"] = int(par.distinto_fold.sum())
res["imagenes_afectadas_distinto_fold"] = int(len(set(par[par.distinto_fold].pmcid_a + "/" + par[par.distinto_fold].imagen_a) | set(par[par.distinto_fold].pmcid_b + "/" + par[par.distinto_fold].imagen_b)))
(OUT / "resumen_duplicados_dinov2.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=2))

top = np.argsort(-v)[:5]                              # los 5 pares MÁS parecidos (peor caso)
(OUT / "muestras").mkdir(exist_ok=True)
H = Image.new("RGB", (860, 340 * 5), "white")
for k, t in enumerate(top):
    i, j = iu[0][t], iu[1][t]
    d = ImageDraw.Draw(H)
    for c, q in enumerate((i, j)):
        im = Image.open(RAIZ / "producto/imagenes" / pm[q] / idx.image_file.to_numpy(dtype=object)[q]).convert("RGB"); im.thumbnail((420, 300))
        H.paste(im, (10 + 430 * c, 340 * k + 30)); d.text((10 + 430 * c, 340 * k + 8), f"{pm[q]} fold {fold[q]}  cos {v[t]:.3f}", fill="black")
H.save(OUT / "muestras" / "pares_dinov2_top.png")
print("hoja:", OUT / "muestras" / "pares_dinov2_top.png")

