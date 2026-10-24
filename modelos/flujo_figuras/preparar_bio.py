"""Crea lotes B001… para una pasada específica de CONTENIDO BIOLÓGICO sobre las imágenes que entrenan el modelo de clase (prioridad 1 del plan).
Pregunta por figura: ¿hay TEM/SEM de bacterias, células, orgánulos o tejido, o nanopartículas dentro/sobre células? (regla de contenido, opción C).
Resultado: resultados/<revisor>/Bxxx.jsonl con {n, n_bio, contenido, confianza, nota}; se consolida con consolidar_bio.py (no toca figuras_vision.csv).
Uso: python modelos/flujo_figuras/preparar_bio.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preparar_lotes import POR_HOJA, RAIZ, hoja  # noqa: E402

OUT = Path(__file__).resolve().parent
POR_LOTE = 30
plan = pd.read_csv(OUT / "plan_lotes.csv", dtype=str, encoding="utf-8-sig")
p1 = plan[(plan.prioridad == "1") & plan.lote.str.startswith("L")].drop_duplicates("fig_id").sort_values("fig_id").reset_index(drop=True)
p1["lote_b"] = [f"B{i // POR_LOTE + 1:03d}" for i in range(len(p1))]
p1["n_b"] = p1.groupby("lote_b").cumcount() + 1
p1[["lote_b", "n_b", "fig_id", "imagen"]].to_csv(OUT / "bio_plan.csv", index=False, encoding="utf-8-sig")
(OUT / "lotes").mkdir(exist_ok=True); (OUT / "miniaturas").mkdir(exist_ok=True)
for lote, g in p1.groupby("lote_b"):
    hojas = []
    for h in range(0, len(g), POR_HOJA):
        sub = g.iloc[h:h + POR_HOJA]
        nombre = f"{lote}_h{h // POR_HOJA + 1}.jpg"
        destino = OUT / "miniaturas" / nombre
        if not destino.exists():
            hoja([(int(n), RAIZ / im) for n, im in zip(sub.n_b, sub.imagen)], destino)
        hojas.append({"hoja": f"modelos/flujo_figuras/miniaturas/{nombre}", "numeros": [int(n) for n in sub.n_b]})
    (OUT / "lotes" / f"{lote}.json").write_text(json.dumps(
        {"lote": lote, "asignado": "codex", "tipo": "contenido_biologico", "figuras": [{"n": int(r.n_b), "fig_id": r.fig_id} for r in g.itertuples()], "hojas": hojas},
        ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(p1)} figuras en {p1.lote_b.nunique()} lotes B")
