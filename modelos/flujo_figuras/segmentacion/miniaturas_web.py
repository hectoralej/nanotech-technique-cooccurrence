"""Miniaturas JPEG (lado máx. 320 px) de todos los recortes de panel válidos, para la web (Atlas). Salida: entrega/web_paneles_miniaturas.zip
con paneles/<pmcid>/<archivo>.jpg y paneles_web.csv (fig_id, pmcid, panel, tipo, tecnica, contenido, elegible_morfologia, padre, rel, cascada, clase, fold, x0,y0,x1,y1, miniatura).
Uso: python modelos/flujo_figuras/segmentacion/miniaturas_web.py"""
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
from PIL import Image

RAIZ = Path(__file__).resolve().parents[3]
p = pd.read_csv(RAIZ / "modelos/flujo_figuras/segmentacion/cajas/indice_recortes.csv", dtype=str, encoding="utf-8-sig")
p["miniatura"] = p.recorte.map(lambda r: f"paneles/{Path(r).parent.name}/{Path(r).stem}.jpg")
cols = ["fig_id", "pmcid", "panel", "tipo", "tecnica", "contenido", "elegible_morfologia", "padre", "rel", "cascada", "clase", "fold", "x0", "y0", "x1", "y1", "ancho_px", "alto_px", "miniatura"]
sal = RAIZ / "entrega" / "web_paneles_miniaturas.zip"
with zipfile.ZipFile(sal, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("paneles_web.csv", p[cols].to_csv(index=False))
    for r in p.itertuples():
        im = Image.open(RAIZ / r.recorte).convert("RGB"); im.thumbnail((320, 320))
        b = BytesIO(); im.save(b, "JPEG", quality=80); z.writestr(r.miniatura, b.getvalue())
print(len(p), "miniaturas →", sal, f"({sal.stat().st_size / 1e6:.0f} MB)")
