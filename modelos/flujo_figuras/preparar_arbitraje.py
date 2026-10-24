"""Crea lotes de ARBITRAJE (A001…) para las figuras de la cola donde la imagen y el pie discrepan de forma relevante, o con confianza 1.

Selección (ver el informe de la cola): imagen «excluir» con pie útil; imagen «superpuesto» con pie distinto; imagen «pareja»/«simple» con pie más complejo; confianza 1.
No se arbitran los casos en que la imagen es MÁS compleja que el pie (el pie suele subestimar los paneles) ni el pie «revisar_multiple» (ambiguo).
Cada lote lleva, por figura: imagen original, pie (texto), veredicto previo de la imagen y tipología del pie. El árbitro decide mirando la imagen.
Las filas de un lote A reemplazan a las anteriores en figuras_vision.csv (consolidar.py da prioridad A > R > L).
Uso: python modelos/flujo_figuras/preparar_arbitraje.py
"""
import json
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent
RAIZ = OUT.parents[1]
POR_LOTE = 20
v = pd.read_csv(OUT / "figuras_vision.csv", dtype=str, encoding="utf-8-sig")
v["confianza"] = v.confianza.astype(int)
inv = pd.read_csv(RAIZ / "modelos/imagenes_v02/inventario_figuras.csv", dtype=str, encoding="utf-8-sig").drop_duplicates(["pmcid", "figura"]).set_index(["pmcid", "figura"])
c = v[v.estado == "cola_revision"]
d = c[c.acuerdo_con_pie != "True"]
m = ((d.destino_vision == "excluir") & (d.destino_pie != "excluir")) | ((d.destino_vision == "superpuesto") & (d.destino_pie != "superpuesto")) \
    | ((d.destino_vision == "pareja") & (d.destino_pie == "compuesta")) | ((d.destino_vision == "simple") & (d.destino_pie != "simple"))
sel = pd.concat([d[m], c[c.confianza == 1]]).drop_duplicates("fig_id").sort_values("fig_id")
plan = pd.read_csv(OUT / "plan_lotes.csv", dtype=str, encoding="utf-8-sig")
ya = set(plan[plan.lote.str.startswith("A")].fig_id)
sel = sel[~sel.fig_id.isin(ya)]
if sel.empty:
    print("nada nuevo que arbitrar"); raise SystemExit
base = int(plan[plan.lote.str.startswith("A")].lote.str[1:].astype(int).max()) if plan.lote.str.startswith("A").any() else 0
filas = []
for i, r in enumerate(sel.itertuples()):
    filas.append(dict(fig_id=r.fig_id, pmcid=r.pmcid, figura=r.figura, prioridad="0", imagen=r.imagen, tipologia_pie=r.tipologia_pie, destino_pie=r.destino_pie, clase_modelo=r.clase_modelo,
                      fold=r.fold, lote=f"A{base + i // POR_LOTE + 1:03d}", n=str(i % POR_LOTE + 1), asignado="claude"))
nuevo = pd.DataFrame(filas)
pd.concat([plan, nuevo], ignore_index=True).to_csv(OUT / "plan_lotes.csv", index=False, encoding="utf-8-sig")
vs = v.set_index("fig_id")
for lote, g in nuevo.groupby("lote"):
    figs = []
    for r in g.itertuples():
        x = vs.loc[r.fig_id]
        pie = str(inv.loc[(r.pmcid, r.figura), "pie"]) if (r.pmcid, r.figura) in inv.index else ""
        figs.append({"n": int(r.n), "fig_id": r.fig_id, "imagen": r.imagen, "pie": pie[:700],
                     "imagen_dijo": {"paneles": int(x.paneles), "n_micro": int(x.n_micro), "n_espectro": int(x.n_espectro), "n_otro": int(x.n_otro), "curvas_superpuestas": x.curvas_superpuestas,
                                     "destino": x.destino_vision, "nota": str(x.nota)},
                     "pie_dijo": {"tipologia": r.tipologia_pie, "destino": r.destino_pie}})
    (OUT / "lotes" / f"{lote}.json").write_text(json.dumps({"lote": lote, "asignado": "claude", "tipo": "arbitraje", "figuras": figs, "hojas": []}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(nuevo)} figuras en {nuevo.lote.nunique()} lotes A")
