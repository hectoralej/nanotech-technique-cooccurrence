"""Genera un paquete de ejemplos para la presentacion: figuras originales con sus cajas dibujadas (2 por destino) y una rejilla de recortes por clase de portador.
Salida: entrega/ejemplos_presentacion/ (no va a Git) con JPG, creditos.csv (artículo, DOI, licencia) y LEEME.txt.
Uso: python modelos/flujo_figuras/segmentacion/ejemplos_presentacion.py
"""
import json
import random
import sys
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[3]
SAL = RAIZ / "entrega" / "ejemplos_presentacion"; SAL.mkdir(parents=True, exist_ok=True)
fig = pd.read_csv(RAIZ / "modelos/flujo_figuras/figuras_vision.csv", encoding="utf-8-sig", dtype=str)
cajas = pd.read_csv(RAIZ / "modelos/flujo_figuras/segmentacion/cajas/indice_recortes.csv", encoding="utf-8-sig", dtype=str)
meta = {x["fig_id"]: x for x in json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))} if len(sys.argv) > 1 else {}
COL = {"micro": (30, 160, 70), "espectro": (30, 90, 200), "otro": (230, 130, 20)}
rnd = random.Random(7); cred = []
try:
    fnt = ImageFont.truetype("arial.ttf", 22)
except Exception:
    fnt = ImageFont.load_default()

def licencia_ok(fid):
    m = meta.get(fid, {}); return (not meta) or (m.get("license_allows_image") is True)

for destino in ("simple", "pareja", "compuesta", "superpuesto", "excluir"):
    ok = fig[(fig.destino_vision == destino) & fig.estado.str.startswith("aceptada")]
    if destino == "compuesta": ok = ok[ok.paneles.astype(int).between(4, 9)]
    ok = ok[ok.fig_id.map(licencia_ok) & ok.imagen.map(lambda p: (RAIZ / p).exists() and (RAIZ / p).stat().st_size > 5000)]
    elegidos = ok.sample(min(2, len(ok)), random_state=3)
    for k, r in enumerate(elegidos.itertuples(), 1):
        im = Image.open(RAIZ / r.imagen).convert("RGB"); im.thumbnail((1100, 1100)); W, H = im.size; dr = ImageDraw.Draw(im)
        for b in cajas[cajas.fig_id == r.fig_id].itertuples():
            c = COL.get(b.tipo, (200, 0, 0)); x0, y0, x1, y1 = float(b.x0) * W, float(b.y0) * H, float(b.x1) * W, float(b.y1) * H
            dr.rectangle([x0, y0, x1, y1], outline=c, width=3); dr.text((x0 + 4, y0 + 2), f"{b.panel}:{b.tipo}", fill=c, font=fnt)
        nom = f"ejemplo_{destino}_{k}.jpg"; im.save(SAL / nom, quality=88)
        m = meta.get(r.fig_id, {}); cred.append({"archivo": nom, "destino": destino, "fig_id": r.fig_id, "paneles": r.paneles, "titulo": m.get("title", ""), "doi": m.get("doi_link", ""), "licencia": m.get("license", "")})

# rejilla de recortes por clase de portador (3 por clase), solo micrografias de particulas elegibles
el = cajas[cajas.padre.isna() & (cajas.elegible_morfologia == "True") & cajas.clase.notna()]
cl = sorted(el.clase.unique()); T = 220; G = Image.new("RGB", (T * 3, (T + 30) * len(cl)), "white"); dg = ImageDraw.Draw(G)
for j, c in enumerate(cl):
    sub = el[(el.clase == c) & el.fig_id.map(licencia_ok) & el.recorte.map(lambda p: (RAIZ / p).exists())]
    for i, b in enumerate(sub.sample(3, random_state=5).itertuples()):
        t = Image.open(RAIZ / b.recorte).convert("RGB"); t.thumbnail((T, T)); G.paste(t, (i * T, j * (T + 30) + 30))
        m = meta.get(b.fig_id, {}); cred.append({"archivo": "recortes_por_clase.jpg", "destino": f"recorte:{c}", "fig_id": b.fig_id, "paneles": b.panel, "titulo": m.get("title", ""), "doi": m.get("doi_link", ""), "licencia": m.get("license", "")})
    dg.text((6, j * (T + 30) + 4), f"clase del artículo: {c}", fill=(0, 0, 0), font=fnt)
G.save(SAL / "recortes_por_clase.jpg", quality=88)
pd.DataFrame(cred).to_csv(SAL / "creditos.csv", index=False, encoding="utf-8-sig")
(SAL / "LEEME.txt").write_text("Figuras originales con cajas dibujadas (verde = micrografia, azul = espectro, naranja = otro) y rejilla de recortes por clase del articulo.\n"
    "Las imagenes son de articulos CC BY de Europe PMC: mostrar siempre el credito (articulo y DOI) de creditos.csv. Las cajas dibujadas vienen de la revision visual con IA (Claude/Haiku/Codex) y se consolidaron por reglas.\n", encoding="utf-8")
print(len(cred), "ejemplos ->", SAL)
