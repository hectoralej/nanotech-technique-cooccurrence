"""Prepara el flujo de revisión visual de figuras (Claude + Codex) en lotes reanudables.

Para cada figura lógica elige la mejor imagen local, la reduce y la pone en hojas de contacto numeradas (6 figuras por hoja, 3×2) para que un
modelo con visión pueda clasificar muchas figuras con pocos tokens. No pasa el pie al revisor: la clasificación debe ser independiente del texto.
Idempotente: se puede volver a correr; no borra resultados.
Uso: python modelos/flujo_figuras/preparar_lotes.py [--lote 30] [--incluir-excluidos]
Salida: lotes/Lxxx.json, miniaturas/Lxxx_h1.jpg…, plan_lotes.csv (todo reproducible; miniaturas no van a Git).
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TILE_W, TILE_H, COLS, FILAS = 520, 420, 3, 2
POR_HOJA = COLS * FILAS


def fuente(n):
    for f in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, n)
        except OSError:
            pass
    return ImageFont.load_default()


def mejor_imagen(pmcid, archivos):
    mejores = []
    for a in archivos:
        for base in ("producto/imagenes", "producto/imagenes_v02"):
            # el descargador guarda como .jpg cuando el inventario lista un .gif (miniatura)
            for cand in (a, Path(a).stem + ".jpg", Path(a).stem + ".jpeg", Path(a).stem + ".png"):
                p = RAIZ / base / pmcid / cand
                if p.exists():
                    mejores.append((p.stat().st_size, p))
    return max(mejores)[1] if mejores else None


def hoja(items, destino):
    lienzo = Image.new("RGB", (TILE_W * COLS, TILE_H * FILAS), "white")
    d = ImageDraw.Draw(lienzo)
    for k, (num, ruta) in enumerate(items):
        x0, y0 = (k % COLS) * TILE_W, (k // COLS) * TILE_H
        try:
            im = Image.open(ruta).convert("RGB")
            im.thumbnail((TILE_W - 8, TILE_H - 8))
            lienzo.paste(im, (x0 + 4 + (TILE_W - 8 - im.width) // 2, y0 + 4 + (TILE_H - 8 - im.height) // 2))
        except Exception:
            d.text((x0 + 20, y0 + 200), "(imagen ilegible)", fill="red", font=fuente(24))
        d.rectangle([x0, y0, x0 + TILE_W - 1, y0 + TILE_H - 1], outline="#888888", width=2)
        d.rectangle([x0 + 2, y0 + 2, x0 + 58, y0 + 42], fill="#c0392b")
        d.text((x0 + 8, y0 + 5), f"{num:02d}", fill="white", font=fuente(30))
    lienzo.save(destino, quality=72)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", type=int, default=30)
    ap.add_argument("--incluir-excluidos", action="store_true")
    a = ap.parse_args()
    tip = pd.read_csv(OUT.parent / "tipologia_figuras/tipologia_figuras.csv", dtype=str, encoding="utf-8-sig")
    inv = pd.read_csv(RAIZ / "modelos/imagenes_v02/inventario_figuras.csv", dtype=str, encoding="utf-8-sig")
    variantes = inv.groupby(["pmcid", "figura"]).archivo_grafico.apply(list).to_dict()
    entrenamiento = pd.read_csv(RAIZ / "modelos/comparacion/entrada_kabre/indice_embeddings.csv", dtype=str, encoding="utf-8-sig")
    en_entreno = set(zip(entrenamiento.pmcid, entrenamiento.image_file))
    filas = []
    for r in tip.itertuples():
        ruta = mejor_imagen(r.pmcid, variantes[(r.pmcid, r.figura)])
        if ruta is None:
            continue
        prio = 1 if any((r.pmcid, v) in en_entreno for v in variantes[(r.pmcid, r.figura)]) else (3 if r.destino == "excluir" else 2)
        if prio == 3 and not a.incluir_excluidos:
            continue
        filas.append(dict(fig_id=f"{r.pmcid}|{r.figura}", pmcid=r.pmcid, figura=r.figura, prioridad=prio, imagen=ruta.relative_to(RAIZ).as_posix(),
                          tipologia_pie=r.tipologia, destino_pie=r.destino, clase_modelo=r.clase_modelo, fold=r.fold))
    nuevo = pd.DataFrame(filas).sort_values(["prioridad", "pmcid", "figura"], kind="stable").reset_index(drop=True)
    previo = OUT / "plan_lotes.csv"
    if previo.exists():
        # incremental: los lotes ya creados no cambian (hay resultados que dependen de su numeración); lo nuevo se añade al final
        viejo = pd.read_csv(previo, dtype={"n": int}, encoding="utf-8-sig")
        nuevo = nuevo[~nuevo.fig_id.isin(viejo.fig_id)].reset_index(drop=True)
        base = int(viejo.lote.str[1:].astype(int).max())
        lotes_viejos = viejo.drop_duplicates("lote").set_index("lote").asignado.to_dict()
    else:
        viejo, base, lotes_viejos = pd.DataFrame(), 0, {}
    if len(nuevo):
        nuevo["lote"] = [f"L{base + i // a.lote + 1:03d}" for i in range(len(nuevo))]
        nuevo["n"] = nuevo.groupby("lote").cumcount() + 1
        # reparto: alterna Claude/Codex; cada 8.º lote lo hacen los dos (control de acuerdo entre modelos)
        k0 = len(lotes_viejos)
        rep_nuevo = {l: ("ambos" if (k0 + i) % 8 == 7 else ("claude" if (k0 + i) % 2 == 0 else "codex")) for i, l in enumerate(sorted(nuevo.lote.unique()))}
        nuevo["asignado"] = nuevo.lote.map(rep_nuevo)
    plan = pd.concat([viejo, nuevo], ignore_index=True)
    plan.to_csv(previo, index=False, encoding="utf-8-sig")
    reparto = {**lotes_viejos, **(rep_nuevo if len(nuevo) else {})}
    lotes = sorted(plan.lote.unique())
    (OUT / "lotes").mkdir(exist_ok=True); (OUT / "miniaturas").mkdir(exist_ok=True)
    for l, g in plan.groupby("lote"):
        hojas = []
        for h in range(0, len(g), POR_HOJA):
            sub = g.iloc[h:h + POR_HOJA]
            nombre = f"{l}_h{h // POR_HOJA + 1}.jpg"
            destino = OUT / "miniaturas" / nombre
            if not destino.exists():
                hoja([(int(n), RAIZ / im) for n, im in zip(sub.n, sub.imagen)], destino)
            hojas.append({"hoja": f"modelos/flujo_figuras/miniaturas/{nombre}", "numeros": [int(n) for n in sub.n]})
        (OUT / "lotes" / f"{l}.json").write_text(json.dumps(
            {"lote": l, "asignado": reparto[l], "figuras": [{"n": int(r.n), "fig_id": r.fig_id} for r in g.itertuples()], "hojas": hojas},
            ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(plan)} figuras en {len(lotes)} lotes; prioridad 1 (entrenamiento v0.1): {(plan.prioridad == 1).sum()}, prioridad 2: {(plan.prioridad == 2).sum()}")
    print(pd.Series(reparto).value_counts().to_dict())


if __name__ == "__main__":
    main()
