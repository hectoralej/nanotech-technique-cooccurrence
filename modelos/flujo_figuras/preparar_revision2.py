"""Crea lotes de RE-REVISIÓN (R001…) para las figuras ya clasificadas que tocan las reglas nuevas del 24-oct:
 - posible fluorescencia / confocal / histología / células (ahora son «otro», no «micro»);
 - curvas superpuestas (ahora hay que distinguir cascada = un panel por curva, frente a curvas solapadas = un panel).
Las filas de un lote R reemplazan a las del lote L original en figuras_vision.csv (consolidar.py da prioridad a los lotes R).
Reutiliza las hojas de contacto de preparar_lotes.py. Idempotente: no repite figuras que ya están en un lote R.
Uso: python modelos/flujo_figuras/preparar_revision2.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preparar_lotes import POR_HOJA, RAIZ, hoja  # noqa: E402

OUT = Path(__file__).resolve().parent
POR_LOTE = 30
v = pd.read_csv(OUT / "figuras_vision.csv", dtype=str, encoding="utf-8-sig")
for c in ("n_micro", "n_espectro"):
    v[c] = v[c].astype(int)
v["nota"] = v.nota.fillna("")
fl = v.nota.str.contains(r"fluoresc|confocal|histolog|H&E|hematox|inmuno|immuno|tejido|célula|celula|cell", case=False, regex=True) | v.tecnicas.fillna("").str.contains(r"fluor|confocal|H&E|histol", case=False, regex=True)
sup = (v.curvas_superpuestas == "si") | (v.destino_vision == "superpuesto")
sel = v[fl | sup].copy()
plan = pd.read_csv(OUT / "plan_lotes.csv", dtype=str, encoding="utf-8-sig")
ya = set(plan[plan.lote.str.startswith("R")].fig_id)
sel = sel[~sel.fig_id.isin(ya)].sort_values("fig_id")
if sel.empty:
    print("nada nuevo que re-revisar"); raise SystemExit
base = int(plan[plan.lote.str.startswith("R")].lote.str[1:].astype(int).max()) if plan.lote.str.startswith("R").any() else 0
filas = []
for i, r in enumerate(sel.itertuples()):
    lote = f"R{base + i // POR_LOTE + 1:03d}"
    filas.append(dict(fig_id=r.fig_id, pmcid=r.pmcid, figura=r.figura, prioridad="0", imagen=r.imagen, tipologia_pie=r.tipologia_pie, destino_pie=r.destino_pie,
                      clase_modelo=r.clase_modelo, fold=r.fold, lote=lote, n=str(i % POR_LOTE + 1), asignado="claude" if (base + i // POR_LOTE) % 2 == 0 else "codex"))
nuevo = pd.DataFrame(filas)
pd.concat([plan, nuevo], ignore_index=True).to_csv(OUT / "plan_lotes.csv", index=False, encoding="utf-8-sig")
for lote, g in nuevo.groupby("lote"):
    hojas = []
    for h in range(0, len(g), POR_HOJA):
        sub = g.iloc[h:h + POR_HOJA]
        nombre = f"{lote}_h{h // POR_HOJA + 1}.jpg"
        hoja([(int(n), RAIZ / im) for n, im in zip(sub.n, sub.imagen)], OUT / "miniaturas" / nombre)
        hojas.append({"hoja": f"modelos/flujo_figuras/miniaturas/{nombre}", "numeros": [int(n) for n in sub.n]})
    (OUT / "lotes" / f"{lote}.json").write_text(json.dumps(
        {"lote": lote, "asignado": g.asignado.iloc[0], "figuras": [{"n": int(r.n), "fig_id": r.fig_id} for r in g.itertuples()], "hojas": hojas},
        ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(nuevo)} figuras en {nuevo.lote.nunique()} lotes R; reparto:", nuevo.drop_duplicates("lote").asignado.value_counts().to_dict())
