"""Empaqueta las figuras originales que NO estan en producto/imagenes (v0.1) y estan en producto/imagenes_v02, reducidas a 900 px de lado mayor, para el Atlas.
Salida (no va a Git): entrega/web_figuras_v02_reducidas.zip con rutas producto/imagenes_v02/<pmcid>/<archivo> (se extrae en la raiz del repositorio).
Uso: python modelos/flujo_figuras/segmentacion/figuras_web.py
"""
import io
import zipfile
from pathlib import Path

import pandas as pd
from PIL import Image

RAIZ = Path(__file__).resolve().parents[3]
d = pd.read_csv(RAIZ / "modelos/flujo_figuras/figuras_vision.csv", encoding="utf-8-sig", dtype=str)
rutas = sorted({p for p in d.imagen if p.startswith("producto/imagenes_v02/")})
sal = RAIZ / "entrega"; sal.mkdir(exist_ok=True)
zp = sal / "web_figuras_v02_reducidas.zip"; n = antes = 0; copias = 0; rotas = []
with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
    for r in rutas:
        f = RAIZ / r; antes += f.stat().st_size
        try:
            if f.suffix.lower() in (".jpg", ".jpeg"):
                im = Image.open(f).convert("RGB"); im.thumbnail((900, 900), Image.LANCZOS)
                b = io.BytesIO(); im.save(b, "JPEG", quality=80, optimize=True); z.writestr(r, b.getvalue()); n += 1
            else:
                Image.open(f).verify(); z.write(f, r); copias += 1
        except Exception:
            rotas.append(r)
print(len(rotas), "archivos ilegibles (vacios o corruptos):", rotas[:5])
print(len(rutas), "figuras (", n, "jpg reducidos,", copias, "copiadas) | original", round(antes / 1e6), "MB ->", round(zp.stat().st_size / 1e6), "MB:", zp)
