"""Prepara los lotes de separación de figuras compuestas/parejas (cajas de panel con un modelo de visión), reanudable e incremental.

Toma de figuras_vision.csv las figuras `pareja` y `compuesta` con 2 a MAX_PANELES paneles y crea lotes de 10 figuras: una imagen con cuadrícula por figura
(lado máx. 1200 px, líneas cada 0,1) + lotes/Cxxx.json con el nº de paneles esperado. Las «aceptada_auto» van primero.
Los lotes ya creados no cambian (se añaden lotes nuevos al final cuando Codex/Claude clasifican más figuras).
Uso: python modelos/flujo_figuras/segmentacion/preparar_cajas.py
"""
import json
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "cajas"
POR_LOTE, MAX_PANELES = 10, 16


def fuente(n):
    for f in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(f, n)
        except OSError:
            pass
    return ImageFont.load_default()


def nombre(fid):
    return fid.replace("|", "_").replace(" ", "").replace(".", "")


def cuadricula(ruta, destino):
    im = Image.open(ruta).convert("RGB")
    im.thumbnail((1200, 1200))
    d = ImageDraw.Draw(im, "RGBA")
    f = fuente(max(12, im.width // 60))
    for k in range(1, 10):
        x, y = int(im.width * k / 10), int(im.height * k / 10)
        d.line([(x, 0), (x, im.height)], fill=(255, 0, 0, 90), width=1)
        d.line([(0, y), (im.width, y)], fill=(255, 0, 0, 90), width=1)
        d.text((x + 2, 2), f"{k/10:.1f}", fill=(200, 0, 0, 255), font=f)
        d.text((2, y + 2), f"{k/10:.1f}", fill=(200, 0, 0, 255), font=f)
    im.save(destino, quality=85)


def main():
    v = pd.read_csv(RAIZ / "modelos/flujo_figuras/figuras_vision.csv", dtype=str, encoding="utf-8-sig")
    for c in ("paneles", "n_micro", "n_espectro", "n_otro"):
        v[c] = v[c].astype(int)
    v = v[v.destino_vision.isin(["pareja", "compuesta"]) & v.paneles.between(2, MAX_PANELES) & ((v.n_micro + v.n_espectro) > 0)].copy()
    v["_o"] = (v.estado != "aceptada_auto").astype(int)
    v = v.sort_values(["_o", "fig_id"], kind="stable")
    OUT.mkdir(parents=True, exist_ok=True); (OUT / "lotes").mkdir(exist_ok=True); (OUT / "grids").mkdir(exist_ok=True)
    plan_f = OUT / "plan_cajas.csv"
    viejo = pd.read_csv(plan_f, dtype=str, encoding="utf-8-sig") if plan_f.exists() else pd.DataFrame()
    nuevo = v[~v.fig_id.isin(viejo.fig_id)] if len(viejo) else v
    base = int(viejo.lote.str[1:].astype(int).max()) if len(viejo) else 0
    k0 = viejo.lote.nunique() if len(viejo) else 0
    filas = []
    for i, r in enumerate(nuevo.itertuples()):
        lote = f"C{base + i // POR_LOTE + 1:03d}"
        filas.append(dict(lote=lote, n=i % POR_LOTE + 1, fig_id=r.fig_id, imagen=r.imagen, grid=f"modelos/flujo_figuras/segmentacion/cajas/grids/{nombre(r.fig_id)}.jpg",
                          paneles=r.paneles, n_micro=r.n_micro, n_espectro=r.n_espectro, n_otro=r.n_otro, destino=r.destino_vision, estado=r.estado,
                          asignado="claude" if (k0 + i // POR_LOTE) % 2 == 0 else "codex"))
    nuevo_df = pd.DataFrame(filas)
    plan = pd.concat([viejo, nuevo_df], ignore_index=True) if len(viejo) else nuevo_df
    plan.to_csv(plan_f, index=False, encoding="utf-8-sig")
    for r in nuevo_df.itertuples():
        cuadricula(RAIZ / r.imagen, RAIZ / r.grid)
    for lote, g in nuevo_df.groupby("lote"):
        (OUT / "lotes" / f"{lote}.json").write_text(json.dumps(
            {"lote": lote, "asignado": g.asignado.iloc[0],
             "figuras": [{"fig_id": r.fig_id, "grid": r.grid, "paneles_esperados": int(r.paneles), "esperado": {"micro": int(r.n_micro), "espectro": int(r.n_espectro), "otro": int(r.n_otro)}} for r in g.itertuples()]},
            ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(plan)} figuras en {plan.lote.nunique()} lotes ({len(nuevo_df)} nuevas); por asignado: {plan.drop_duplicates('lote').asignado.value_counts().to_dict()}")


if __name__ == "__main__":
    main()
