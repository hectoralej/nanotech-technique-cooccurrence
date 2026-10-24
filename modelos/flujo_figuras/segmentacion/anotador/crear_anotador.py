"""Crea anotador.html: herramienta para dibujar a mano la caja de cada panel (verdad humana) sobre ~25 figuras (~100 paneles).

Muestra estratificada por nº de paneles de las figuras `aceptada_auto` del plan de cajas; siempre incluye las 10 figuras del lote C001 (ya tienen cajas de Haiku para comparar).
Uso: python modelos/flujo_figuras/segmentacion/anotador/crear_anotador.py
Luego, desde la raíz del repositorio:  python -m http.server 8000
y abrir http://localhost:8000/modelos/flujo_figuras/segmentacion/anotador/anotador.html
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
OBJETIVO_PANELES = 100

plan = pd.read_csv(RAIZ / "modelos/flujo_figuras/segmentacion/cajas/plan_cajas.csv", dtype=str, encoding="utf-8-sig")
plan["paneles"] = plan.paneles.astype(int)
base = plan[plan.lote == "C001"]
resto = plan[(plan.lote != "C001") & (plan.estado == "aceptada_auto")]
bins = {"2": (2, 2, 3), "3-4": (3, 4, 4), "5-6": (5, 6, 2), "7-9": (7, 9, 2), "10-16": (10, 16, 1)}   # (min, max, nº de figuras)
extra = pd.concat([resto[resto.paneles.between(a, b)].sample(k, random_state=20261024) for a, b, k in bins.values()])
sel = pd.concat([base, extra])
while sel.paneles.sum() < OBJETIVO_PANELES:
    sel = pd.concat([sel, resto[~resto.fig_id.isin(sel.fig_id)].sample(1, random_state=len(sel))])
sel = sel.sample(frac=1, random_state=3).reset_index(drop=True)
datos = [dict(fig_id=r.fig_id, imagen="/" + r.imagen, esperados=int(r.paneles)) for r in sel.itertuples()]
plantilla = (OUT / "anotador_plantilla.html").read_text(encoding="utf-8")
(OUT / "anotador.html").write_text(plantilla.replace("__DATOS__", json.dumps(datos, ensure_ascii=False)), encoding="utf-8")
(OUT / "figuras_anotador.csv").write_text(sel[["fig_id", "lote", "paneles"]].to_csv(index=False), encoding="utf-8")
print(len(sel), "figuras,", int(sel.paneles.sum()), "paneles esperados;", "de C001:", int(sel.lote.eq("C001").sum()))
