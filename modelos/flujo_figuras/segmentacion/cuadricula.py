"""Piloto de separación de figuras compuestas con un modelo de visión.

`cuadricula.py preparar <fig_id>...`: copia la figura (lado máx. 1200 px) con una cuadrícula etiquetada cada 10 % para que el modelo lea coordenadas normalizadas.
`cuadricula.py cajas <cajas.json>`: dibuja las cajas propuestas sobre la figura original y guarda cada recorte (para comprobar a ojo).
cajas.json = {"<fig_id>": [{"tipo": "micro|espectro|otro", "caja": [x0, y0, x1, y1]}, ...]} con coordenadas en 0–1 sobre la figura completa.
Salida en modelos/flujo_figuras/segmentacion/piloto/ (no va a Git).
"""
import json
import sys
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "piloto"
plan = pd.read_csv(RAIZ / "modelos/flujo_figuras/plan_lotes.csv", dtype=str, encoding="utf-8-sig").set_index("fig_id")
COL = {"micro": "#d81b60", "espectro": "#1e88e5", "otro": "#43a047"}


def fuente(n):
    for f in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(f, n)
        except OSError:
            pass
    return ImageFont.load_default()


def nombre(fig_id):
    return fig_id.replace("|", "_").replace(" ", "").replace(".", "")


def preparar(ids):
    OUT.mkdir(parents=True, exist_ok=True)
    for fid in ids:
        im = Image.open(RAIZ / plan.loc[fid, "imagen"]).convert("RGB")
        im.thumbnail((1200, 1200))
        d = ImageDraw.Draw(im, "RGBA")
        f = fuente(max(12, im.width // 60))
        for k in range(1, 10):
            x, y = int(im.width * k / 10), int(im.height * k / 10)
            d.line([(x, 0), (x, im.height)], fill=(255, 0, 0, 90), width=1)
            d.line([(0, y), (im.width, y)], fill=(255, 0, 0, 90), width=1)
            d.text((x + 2, 2), f"{k/10:.1f}", fill=(200, 0, 0, 255), font=f)
            d.text((2, y + 2), f"{k/10:.1f}", fill=(200, 0, 0, 255), font=f)
        im.save(OUT / f"grid_{nombre(fid)}.jpg", quality=85)
        print(fid, im.size, OUT / f"grid_{nombre(fid)}.jpg")


def cajas(ruta):
    OUT.mkdir(parents=True, exist_ok=True)
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    for fid, paneles in datos.items():
        im = Image.open(RAIZ / plan.loc[fid, "imagen"]).convert("RGB")
        W, H = im.size
        vis = im.copy(); vis.thumbnail((1200, 1200)); sx, sy = vis.width / W, vis.height / H
        d = ImageDraw.Draw(vis)
        f = fuente(max(14, vis.width // 40))
        for k, p in enumerate(paneles, 1):
            x0, y0, x1, y1 = p["caja"]
            px = [int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)]
            im.crop(px).save(OUT / f"crop_{nombre(fid)}_{k:02d}_{p['tipo']}.png")
            d.rectangle([px[0] * sx, px[1] * sy, px[2] * sx, px[3] * sy], outline=COL[p["tipo"]], width=3)
            d.text((px[0] * sx + 4, px[1] * sy + 2), str(k), fill=COL[p["tipo"]], font=f)
        vis.save(OUT / f"overlay_{nombre(fid)}.jpg", quality=85)
        print(fid, len(paneles), "recortes")


if __name__ == "__main__":
    if sys.argv[1] == "preparar":
        preparar(sys.argv[2:])
    else:
        cajas(sys.argv[2])
