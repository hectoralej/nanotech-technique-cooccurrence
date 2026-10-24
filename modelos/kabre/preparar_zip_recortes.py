"""Empaqueta los recortes de micrografía de partículas aptos para entrenar (elegible_morfologia, con clase de portador) para subirlos a Kabré.

Salida (no va a Git): entrega/recortes_v02.zip con recortes/<pmcid>/<archivo>.png e indice_recortes_entrenamiento.csv.
Columnas del índice: pmcid, image_file, clase_modelo, fold, fig_id, panel, tecnica, contenido, ancho_px, alto_px.
Uso: python modelos/kabre/preparar_zip_recortes.py
"""
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
p = pd.read_csv(RAIZ / "modelos/flujo_figuras/segmentacion/cajas/indice_recortes.csv", dtype=str, encoding="utf-8-sig")
e = p[p.padre.isna() & (p.elegible_morfologia == "True") & p.clase.notna()].copy()
e["image_file"] = e.recorte.map(lambda r: Path(r).name)
e = e.rename(columns={"clase": "clase_modelo"})
assert e.groupby("pmcid").fold.nunique().max() == 1, "un artículo en dos folds"
assert e.groupby("pmcid").image_file.apply(lambda s: s.is_unique).all(), "nombres de recorte repetidos dentro de un artículo"
idx = e[["pmcid", "image_file", "clase_modelo", "fold", "fig_id", "panel", "tecnica", "contenido", "ancho_px", "alto_px"]]
sal = RAIZ / "entrega"; sal.mkdir(exist_ok=True)
with zipfile.ZipFile(sal / "recortes_v02.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("indice_recortes_entrenamiento.csv", idx.to_csv(index=False))
    for r in e.itertuples():
        z.write(RAIZ / r.recorte, f"recortes/{r.pmcid}/{r.image_file}")
print(len(idx), "recortes,", idx.pmcid.nunique(), "artículos →", sal / "recortes_v02.zip", f"({(sal / 'recortes_v02.zip').stat().st_size / 1e6:.0f} MB)")
print(idx.clase_modelo.value_counts().to_dict(), "| folds:", idx.fold.value_counts().sort_index().to_dict())
