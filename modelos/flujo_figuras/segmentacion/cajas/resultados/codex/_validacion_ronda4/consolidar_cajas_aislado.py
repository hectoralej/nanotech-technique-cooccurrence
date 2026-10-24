"""Valida las cajas de los revisores, recorta los paneles y genera las hojas de revisión visual (reglas v2 de INSTRUCCIONES_CAJAS.md).

Lee cajas/resultados/<revisor>/Cxxx.json ({"<fig_id>": [{"tipo", "caja": [x0,y0,x1,y1], "padre"?, "rel"?, "cascada"?}, ...]}).
Por figura comprueba: cajas válidas (0–1, área ≥ 0,5 %); cajas de nivel superior con solape < 30 %; cada hija (`padre`) dentro de su padre (≥ 80 % de su área);
y que el nº de paneles útiles de nivel superior (micro + espectro) coincida con el esperado (n_micro + n_espectro de la clasificación).
Estructura inválida o conteo distinto → `cajas/cola_cajas.csv` (con las cajas, sin recortar). Lo válido se recorta a producto/imagenes_recortes/paneles_v02/<pmcid>/
(no va a Git) y se registra en `cajas/paneles.csv`. Hojas de revisión (6 superposiciones por hoja) en cajas/revision/.
Si varios revisores cajearon la misma figura se conserva la primera válida (orden alfabético de revisor) y se anota en `revisores`.
Uso: python modelos/flujo_figuras/segmentacion/consolidar_cajas.py
"""
import json
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path('C:\\Users\\Hector\\Desktop\\Quimioinformatica Proyecto\\nanotech-technique-cooccurrence\\modelos\\flujo_figuras\\segmentacion\\cajas\\resultados\\codex\\_validacion_ronda4')
OUT = RAIZ
DEST = RAIZ / "recortes"
COL = {"micro": "#d81b60", "espectro": "#1e88e5", "otro": "#43a047"}
TIPOS = set(COL)


def fuente(n):
    for f in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(f, n)
        except OSError:
            pass
    return ImageFont.load_default()


def area(c):
    return (c[2] - c[0]) * (c[3] - c[1])


def inter(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return ix * iy


def validar(paneles, util_esperado):
    """Devuelve (error_estructural, aviso_conteo). Cadena vacía = sin problema."""
    n = len(paneles)
    if n == 0:
        return "sin cajas", ""
    for p in paneles:
        if p.get("tipo") not in TIPOS:
            return "tipo inválido", ""
        c = p.get("caja")
        if not (isinstance(c, list) and len(c) == 4 and all(isinstance(x, (int, float)) and -0.001 <= x <= 1.001 for x in c) and c[0] < c[2] and c[1] < c[3]):
            return "caja inválida", ""
        if area(c) < 0.005:
            return "caja demasiado pequeña", ""
    for k, p in enumerate(paneles, 1):
        if "padre" in p:
            q = p["padre"]
            if not (isinstance(q, int) and 1 <= q <= n and q != k and "padre" not in paneles[q - 1]):
                return f"caja {k}: padre inválido", ""
            if inter(p["caja"], paneles[q - 1]["caja"]) < 0.8 * area(p["caja"]):
                return f"caja {k} (hija) no está dentro de su padre {q}", ""
    top = [p for p in paneles if "padre" not in p]
    for i in range(len(top)):
        for j in range(i + 1, len(top)):
            m = min(area(top[i]["caja"]), area(top[j]["caja"]))
            if m > 0 and inter(top[i]["caja"], top[j]["caja"]) / m > 0.3:
                return f"cajas {i + 1} y {j + 1} de nivel superior se solapan > 30 %", ""
    util = sum(p["tipo"] in ("micro", "espectro") for p in top)
    if util != util_esperado:
        return "", f"conteo útil {util} frente al esperado {util_esperado}"
    return "", ""


def main():
    plan = pd.read_csv(OUT / "plan_cajas.csv", dtype=str, encoding="utf-8-sig").set_index("fig_id")
    # el conteo esperado es el vigente en figuras_vision.csv (incluye las re-revisiones R con las reglas nuevas), no el del momento de crear el lote
    vig = pd.read_csv(OUT / "figuras_vision.csv", dtype=str, encoding="utf-8-sig").drop_duplicates("fig_id").set_index("fig_id")
    for c in ("paneles", "n_micro", "n_espectro", "n_otro"):
        plan[c] = [vig.loc[i, c] if i in vig.index else plan.loc[i, c] for i in plan.index]
    filas, cola, vistos = [], [], {}
    for carpeta in sorted((OUT / "resultados").glob("*/")):
        for f in sorted(carpeta.glob("C*.json")):
            for fid, paneles in json.loads(f.read_text(encoding="utf-8-sig")).items():
                if fid.startswith("_"):
                    continue
                if fid not in plan.index:
                    cola.append((fid, carpeta.name, "figura fuera del plan", "")); continue
                util = int(plan.loc[fid, "n_micro"]) + int(plan.loc[fid, "n_espectro"])
                err, aviso = validar(paneles, util)
                if err or aviso:
                    cola.append((fid, carpeta.name, err or aviso, json.dumps(paneles, ensure_ascii=False))); continue
                if fid in vistos:
                    vistos[fid][2].append(carpeta.name)
                else:
                    vistos[fid] = (carpeta.name, paneles, [carpeta.name])
    DEST.mkdir(parents=True, exist_ok=True); (OUT / "revision").mkdir(exist_ok=True)
    overlays = []
    for fid, (rev, paneles, revs) in vistos.items():
        im = Image.open(RAIZ / plan.loc[fid, "imagen"]).convert("RGB")
        W, H = im.size
        vis = im.copy(); vis.thumbnail((520, 420)); sx, sy = vis.width / W, vis.height / H
        d = ImageDraw.Draw(vis); ft = fuente(16)
        pm, fg = fid.split("|")[0], fid.split("|")[1].replace(" ", "").replace(".", "")
        (DEST / pm).mkdir(exist_ok=True)
        for k, p in enumerate(paneles, 1):
            x0, y0, x1, y1 = p["caja"]
            px = [max(0, int(x0 * W)), max(0, int(y0 * H)), min(W, int(x1 * W)), min(H, int(y1 * H))]
            hija = "padre" in p
            ruta = DEST / pm / f"{fg}_p{k:02d}_{p['tipo']}{'_inset' if hija else ''}{'_cascada' if p.get('cascada') else ''}.png"
            if not ruta.exists():
                im.crop(px).save(ruta)
            d.rectangle([px[0] * sx, px[1] * sy, px[2] * sx, px[3] * sy], outline=COL[p["tipo"]], width=1 if hija else 2)
            d.text((px[0] * sx + 3, px[1] * sy + 1), str(k), fill=COL[p["tipo"]], font=ft)
            filas.append(dict(fig_id=fid, pmcid=pm, panel=k, tipo=p["tipo"], tecnica=p.get("tecnica", ""), contenido=p.get("contenido", "particulas" if p["tipo"] == "micro" else ""),
                              elegible_morfologia=p["tipo"] == "micro" and p.get("contenido", "particulas") == "particulas" and "padre" not in p,
                              padre=p.get("padre", ""), rel=p.get("rel", ""), cascada=bool(p.get("cascada", False)),
                              x0=round(x0, 4), y0=round(y0, 4), x1=round(x1, 4), y1=round(y1, 4), ancho_px=px[2] - px[0], alto_px=px[3] - px[1],
                              recorte=ruta.relative_to(RAIZ).as_posix(), revisor=rev, revisores="|".join(revs), imagen=plan.loc[fid, "imagen"]))
        overlays.append((fid, vis))
    for h in range(0, len(overlays), 6):
        hoja = Image.new("RGB", (520 * 3, 420 * 2), "white"); d = ImageDraw.Draw(hoja); ft = fuente(14)
        for k, (fid, vis) in enumerate(overlays[h:h + 6]):
            x, y = (k % 3) * 520, (k // 3) * 420
            hoja.paste(vis, (x + (520 - vis.width) // 2, y + (420 - vis.height) // 2))
            d.text((x + 4, y + 2), fid, fill="black", font=ft)
        hoja.save(OUT / "revision" / f"R{h // 6 + 1:03d}.jpg", quality=75)
    px = pd.DataFrame(filas)
    px.to_csv(OUT / "paneles.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(cola, columns=["fig_id", "revisor", "motivo", "cajas"]).to_csv(OUT / "cola_cajas.csv", index=False, encoding="utf-8-sig")
    print(f"figuras con cajas válidas: {len(vistos)} de {len(plan)} ({len(filas)} recortes); a la cola: {len(cola)}")
    if len(px):
        top = px[px.padre == ""]
        print("recortes de nivel superior por tipo:", top.tipo.value_counts().to_dict(), "| insets:", int((px.padre != "").sum()), "| cascada:", int(px.cascada.sum()),
              "| lado menor mediano (px):", int(top[["ancho_px", "alto_px"]].min(axis=1).median()))


if __name__ == "__main__":
    main()
