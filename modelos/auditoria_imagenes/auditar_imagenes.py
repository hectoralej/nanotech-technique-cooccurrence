"""Auditoría de calidad de las imágenes originales (producto/imagenes, v0.1) por lotes, con checkpoints y reanudación.

Por imagen: tamaño en píxeles, peso, fracción de píxeles blancos, fracción casi gris (color), contraste, hash perceptual (dHash 64 bits y aHash 64 bits).
No modifica ninguna imagen ni ningún CSV de curation/. Salida: modelos/auditoria_imagenes/imagenes_calidad.csv y progreso.json.
Uso: python modelos/auditoria_imagenes/auditar_imagenes.py [tamano_lote=430]
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PROG, CSV = OUT / "progreso.json", OUT / "imagenes_calidad.csv"
t = pd.read_csv(RAIZ / "curation/v0.1/tabla_modelo.csv", encoding="utf-8-sig")
t = t.drop_duplicates(["pmcid", "image_file"]).reset_index(drop=True)
t["ruta"] = [RAIZ / "producto/imagenes" / str(a) / str(b) for a, b in zip(t.pmcid, t.image_file)]
t = t[t.ruta.map(lambda p: p.exists())].reset_index(drop=True)
LOTE = int(sys.argv[1]) if len(sys.argv) > 1 else 430


def bits(a):
    return "".join("1" if x else "0" for x in a.ravel())


def medir(ruta):
    with Image.open(ruta) as im:
        w, h = im.size
        rgb = im.convert("RGB")
        p = np.asarray(rgb.resize((min(w, 256), min(h, 256))), dtype=np.uint8)
        g = np.asarray(rgb.convert("L").resize((9, 8), Image.BILINEAR), dtype=np.float32)
        g8 = np.asarray(rgb.convert("L").resize((8, 8), Image.BILINEAR), dtype=np.float32)
    blanco = float(((p > 240).all(axis=2)).mean())
    mx, mn = p.max(axis=2).astype(np.int16), p.min(axis=2).astype(np.int16)
    color = float(((mx - mn) > 40).mean())
    gris = np.asarray(Image.fromarray(p).convert("L"), dtype=np.float32)
    return dict(ancho=w, alto=h, megapix=round(w * h / 1e6, 3), kb=round(ruta.stat().st_size / 1024, 1), frac_blanco=round(blanco, 4), frac_color=round(color, 4),
                contraste=round(float(gris.std()), 2), dhash=bits(g[:, 1:] > g[:, :-1]), ahash=bits(g8 > g8.mean()))


prog = json.loads(PROG.read_text(encoding="utf-8")) if PROG.exists() else {"lotes_hechos": 0, "total": int(len(t)), "lote": LOTE}
hecho = pd.read_csv(CSV, encoding="utf-8", dtype={"dhash": str, "ahash": str}) if CSV.exists() else pd.DataFrame()
n_lotes = int(np.ceil(len(t) / LOTE))
for L in range(prog["lotes_hechos"], n_lotes):
    t0 = time.time()
    sub = t.iloc[L * LOTE:(L + 1) * LOTE]
    filas = []
    for r in sub.itertuples():
        try:
            m = medir(r.ruta)
            filas.append(dict(pmcid=r.pmcid, image_file=r.image_file, fold=r.fold, clase_modelo=r.clase_modelo, **m))
        except Exception as exc:  # noqa: BLE001
            filas.append(dict(pmcid=r.pmcid, image_file=r.image_file, fold=r.fold, clase_modelo=r.clase_modelo, error=str(exc)[:80]))
    hecho = pd.concat([hecho, pd.DataFrame(filas)], ignore_index=True)
    hecho.to_csv(CSV, index=False, encoding="utf-8")
    prog.update(lotes_hechos=L + 1, filas=int(len(hecho)))
    PROG.write_text(json.dumps(prog, ensure_ascii=False, indent=1), encoding="utf-8")
    sub_ok = hecho.iloc[L * LOTE:(L + 1) * LOTE]
    print(f"[checkpoint] lote {L+1}/{n_lotes}: {len(sub)} imágenes en {time.time()-t0:.0f}s | errores {int(sub_ok.get('error', pd.Series(dtype=object)).notna().sum())} | "
          f"mediana {sub_ok.megapix.median():.2f} MP | <0,1 MP: {int((sub_ok.megapix < 0.1).sum())} | >70 % blanco: {int((sub_ok.frac_blanco > 0.7).sum())}", flush=True)
print("auditoría de calidad completa:", len(hecho), "imágenes")

