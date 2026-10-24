"""Valida las cajas de los revisores, recorta los paneles y genera las hojas de revisión visual.

Lee cajas/resultados/<revisor>/Cxxx.json ({"<fig_id>": [{"tipo", "caja": [x0,y0,x1,y1]}, ...]}). Por figura comprueba: nº de cajas = paneles esperados, cajas válidas (0–1, área ≥ 0,5 %),
solapamiento entre cajas < 30 % y tipo (micro/espectro/otro). Lo que falla va a `cajas/cola_cajas.csv`; lo válido se recorta a
producto/imagenes_recortes/paneles_v02/<pmcid>/ (no va a Git) y se registra en `cajas/paneles.csv`.
Hojas de revisión (6 superposiciones por hoja) en cajas/revision/; las superposiciones sirven para que una persona confirme a ojo.
Uso: python modelos/flujo_figuras/segmentacion/consolidar_cajas.py
"""
import json
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "cajas"
DEST = RAIZ / "producto/imagenes_recortes/paneles_v02"
COL = {"micro": "#d81b60", "espectro": "#1e88e5", "otro": "#43a047"}
TIPOS = set(COL)


def fuente(n):
    for f in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(f, n)
        except OSError:
            pass
    return ImageFont.load_default()


def solape(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    menor = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return ix * iy / menor if menor > 0 else 1.0


def validar(paneles, esperados):
    if len(paneles) != esperados:
        return f"{len(paneles)} cajas, se esperaban {esperados}"
    for p in paneles:
        if p.get("tipo") not in TIPOS:
            return "tipo inválido"
        c = p.get("caja")
        if not (isinstance(c, list) and len(c) == 4 and all(isinstance(x, (int, float)) and -0.001 <= x <= 1.001 for x in c) and c[0] < c[2] and c[1] < c[3]):
            return "caja inválida"
        if (c[2] - c[0]) * (c[3] - c[1]) < 0.005:
            return "caja demasiado pequeña"
    for i in range(len(paneles)):
        for j in range(i + 1, len(paneles)):
            if solape(paneles[i]["caja"], paneles[j]["caja"]) > 0.3:
                return f"cajas {i + 1} y {j + 1} se solapan > 30 %"
    return ""


def main():
    plan = pd.read_csv(OUT / "plan_cajas.csv", dtype=str, encoding="utf-8-sig").set_index("fig_id")
    filas, cola, vistos = [], [], {}
    for carpeta in sorted((OUT / "resultados").glob("*/")):
        for f in sorted(carpeta.glob("C*.json")):
            for fid, paneles in json.loads(f.read_text(encoding="utf-8-sig")).items():
                if fid not in plan.index:
                    cola.append((fid, carpeta.name, "figura fuera del plan")); continue
                err = validar(paneles, int(plan.loc[fid, "paneles"]))
                if err:
                    cola.append((fid, carpeta.name, err)); continue
                vistos[fid] = (carpeta.name, paneles)
    DEST.mkdir(parents=True, exist_ok=True); (OUT / "revision").mkdir(exist_ok=True)
    overlays = []
    for fid, (rev, paneles) in vistos.items():
        im = Image.open(RAIZ / plan.loc[fid, "imagen"]).convert("RGB")
        W, H = im.size
        vis = im.copy(); vis.thumbnail((520, 420)); sx, sy = vis.width / W, vis.height / H
        d = ImageDraw.Draw(vis); ft = fuente(16)
        pm = fid.split("|")[0]
        (DEST / pm).mkdir(exist_ok=True)
        for k, p in enumerate(paneles, 1):
            x0, y0, x1, y1 = p["caja"]
            px = [max(0, int(x0 * W)), max(0, int(y0 * H)), min(W, int(x1 * W)), min(H, int(y1 * H))]
            ruta = DEST / pm / f"{fid.split('|')[1].replace(' ', '').replace('.', '')}_p{k:02d}_{p['tipo']}.png"
            if not ruta.exists():
                im.crop(px).save(ruta)
            d.rectangle([px[0] * sx, px[1] * sy, px[2] * sx, px[3] * sy], outline=COL[p["tipo"]], width=2)
            d.text((px[0] * sx + 3, px[1] * sy + 1), str(k), fill=COL[p["tipo"]], font=ft)
            filas.append(dict(fig_id=fid, pmcid=pm, panel=k, tipo=p["tipo"], x0=round(x0, 4), y0=round(y0, 4), x1=round(x1, 4), y1=round(y1, 4),
                              ancho_px=px[2] - px[0], alto_px=px[3] - px[1], recorte=ruta.relative_to(RAIZ).as_posix(), revisor=rev, imagen=plan.loc[fid, "imagen"]))
        overlays.append((fid, vis))
    for h in range(0, len(overlays), 6):
        hoja = Image.new("RGB", (520 * 3, 420 * 2), "white"); d = ImageDraw.Draw(hoja); ft = fuente(14)
        for k, (fid, vis) in enumerate(overlays[h:h + 6]):
            x, y = (k % 3) * 520, (k // 3) * 420
            hoja.paste(vis, (x + (520 - vis.width) // 2, y + (420 - vis.height) // 2))
            d.text((x + 4, y + 2), fid, fill="black", font=ft)
        hoja.save(OUT / "revision" / f"R{h // 6 + 1:03d}.jpg", quality=75)
    pd.DataFrame(filas).to_csv(OUT / "paneles.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(cola, columns=["fig_id", "revisor", "motivo"]).to_csv(OUT / "cola_cajas.csv", index=False, encoding="utf-8-sig")
    px = pd.DataFrame(filas)
    print(f"figuras con cajas válidas: {len(vistos)} de {len(plan)} ({len(filas)} paneles recortados); a la cola: {len(cola)}")
    if len(px):
        print("paneles por tipo:", px.tipo.value_counts().to_dict(), "| lado menor mediano (px):", int(px[["ancho_px", "alto_px"]].min(axis=1).median()))


if __name__ == "__main__":
    main()
