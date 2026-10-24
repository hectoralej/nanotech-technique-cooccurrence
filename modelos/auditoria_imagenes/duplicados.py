"""Imágenes casi duplicadas entre artículos distintos (riesgo de fuga entre particiones) y su efecto en las predicciones fuera de muestra.

Lee imagenes_calidad.csv (auditar_imagenes.py). Escribe pares_duplicados.csv, resumen_duplicados.json y muestras/pares_*.png (5 pares al azar).
Uso: python modelos/auditoria_imagenes/duplicados.py [umbral_hamming=6]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
UMBRAL = int(sys.argv[1]) if len(sys.argv) > 1 else 6
d = pd.read_csv(OUT / "imagenes_calidad.csv", encoding="utf-8", dtype={"dhash": str, "ahash": str})
d = d[d.dhash.notna()].reset_index(drop=True)
arr = lambda col: np.array([[int(c) for c in s.zfill(64)] for s in d[col]], dtype=np.uint8)
A, B = arr("dhash"), arr("ahash")
n = len(d)
pm = d.pmcid.values
fold = d.fold.astype(int).values
dist = np.zeros((n, n), dtype=np.int16)
for i in range(n):                                   # distancia de Hamming: se exige que coincidan AMBOS hashes
    dist[i] = np.maximum((A != A[i]).sum(1), (B != B[i]).sum(1))
iu = np.triu_indices(n, 1)
ok = (dist[iu] <= UMBRAL) & (pm[iu[0]] != pm[iu[1]])
ii, jj = iu[0][ok], iu[1][ok]
par = pd.DataFrame({"pmcid_a": pm[ii], "imagen_a": d.image_file.values[ii], "fold_a": fold[ii], "clase_a": d.clase_modelo.values[ii],
                    "pmcid_b": pm[jj], "imagen_b": d.image_file.values[jj], "fold_b": fold[jj], "clase_b": d.clase_modelo.values[jj], "distancia": dist[ii, jj]})
par["distinto_fold"] = par.fold_a != par.fold_b
par["distinta_clase"] = par.clase_a != par.clase_b
par.sort_values("distancia").to_csv(OUT / "pares_duplicados.csv", index=False, encoding="utf-8")

con_dup = np.zeros(n, dtype=bool)                     # imagen con un casi duplicado de OTRO artículo en OTRO fold (posible fuga)
for a, b, f in zip(ii, jj, (fold[ii] != fold[jj])):
    if f:
        con_dup[a] = con_dup[b] = True
atlas = pd.DataFrame(json.load(open(RAIZ / "producto/modelo/predicciones.json", encoding="utf-8")))
m = d[["pmcid", "image_file"]].assign(con_dup=con_dup).merge(atlas, on=["pmcid", "image_file"], how="left")
m["acierto"] = m.prediccion == m.real
res = {"umbral_hamming": UMBRAL, "imagenes": int(n), "pares_entre_articulos": int(len(par)), "pares_en_distinto_fold": int(par.distinto_fold.sum()),
       "pares_distinta_clase": int(par.distinta_clase.sum()), "imagenes_con_casi_duplicado_en_otro_fold": int(con_dup.sum()),
       "acierto_con_duplicado": round(float(m[m.con_dup].acierto.mean()), 3) if con_dup.any() else None,
       "acierto_sin_duplicado": round(float(m[~m.con_dup].acierto.mean()), 3)}
(OUT / "resumen_duplicados.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=2))

# 5 pares al azar para inspección visual (semilla fija): imagen A | imagen B
(OUT / "muestras").mkdir(exist_ok=True)
sel = par[par.distinto_fold].sample(min(5, int(par.distinto_fold.sum())), random_state=0) if par.distinto_fold.any() else par.sample(min(5, len(par)), random_state=0)
hojas = []
for r in sel.itertuples():
    ims = []
    for pmc, f in ((r.pmcid_a, r.imagen_a), (r.pmcid_b, r.imagen_b)):
        im = Image.open(RAIZ / "producto/imagenes" / pmc / f).convert("RGB"); im.thumbnail((420, 300)); ims.append((pmc, im))
    hoja = Image.new("RGB", (860, 340), "white"); dr = ImageDraw.Draw(hoja)
    for k, (pmc, im) in enumerate(ims):
        hoja.paste(im, (10 + 430 * k, 30)); dr.text((10 + 430 * k, 8), f"{pmc}  fold {r.fold_a if k == 0 else r.fold_b}  dist {r.distancia}", fill="black")
    hojas.append(hoja)
if hojas:
    H = Image.new("RGB", (860, 340 * len(hojas)), "white")
    for k, h in enumerate(hojas):
        H.paste(h, (0, 340 * k))
    H.save(OUT / "muestras" / "pares_duplicados.png")
    print("hoja de muestra:", OUT / "muestras" / "pares_duplicados.png")

