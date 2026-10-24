"""Prepara la auditoría de descriptores (solo texto): lotes D001… con las filas dudosas de descriptores_v02_base.csv.
Dudosa = valor (tamaño, PDI o zeta) que no aparece en la cita; valor fuera de rango; método ambiguo; fuera_rango/duplicado de la base.
(Las etiquetas de muestra cortas como «B1» NO son dudosas: son las etiquetas que se ven en figuras y tablas.)
Uso: python modelos/descriptores_v02/auditoria/preparar_auditoria.py
"""
import json
import re
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent
RAIZ = OUT.parents[2]
POR_LOTE = 25
d = pd.read_csv(RAIZ / "modelos/descriptores_v02/descriptores_v02_base.csv", encoding="utf-8-sig", dtype={"pmcid": str})
d["id"] = [f"DESC-{i:04d}" for i in range(len(d))]


def en_cita(v, q):
    if pd.isna(v):
        return True
    q = str(q).replace(",", ".").replace("−", "-").replace("–", "-")
    for f in {f"{v:g}", f"{v:.1f}", f"{v:.2f}", f"{v:.3f}", f"{abs(v):g}", f"{abs(v):.1f}", f"{abs(v):.2f}", f"{abs(v):.3f}"}:
        if re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d])", q):
            return True
    return False


d["val_ok"] = d.apply(lambda r: all(en_cita(r[c], r.quote) for c in ("size_nm", "pdi", "zeta_mV")), axis=1)
d["rango_mal"] = ~(d.pdi.between(0, 1) | d.pdi.isna()) | ~(d.zeta_mV.between(-100, 100) | d.zeta_mV.isna()) | ~(d.size_nm.between(1, 5000) | d.size_nm.isna())
dud = d[~d.val_ok | d.rango_mal | (d.metodo_ambiguo == True) | (d.fuera_rango == True) | (d.duplicado == True)].copy()
(OUT / "lotes").mkdir(exist_ok=True); (OUT / "resultados").mkdir(exist_ok=True)
dud["lote"] = [f"D{i // POR_LOTE + 1:03d}" for i in range(len(dud))]
dud[["id", "lote", "pmcid", "sample", "size_nm", "pdi", "zeta_mV", "medium", "source", "quote"]].to_csv(OUT / "plan_auditoria.csv", index=False, encoding="utf-8-sig")
for lote, g in dud.groupby("lote"):
    filas = [{"id": r.id, "pmcid": r.pmcid, "muestra": r.sample, "tamano_nm": None if pd.isna(r.size_nm) else r.size_nm, "pdi": None if pd.isna(r.pdi) else r.pdi,
              "zeta_mV": None if pd.isna(r.zeta_mV) else r.zeta_mV, "medio": r.medium, "fuente": r.source, "cita": str(r.quote)[:900],
              "alerta": ("valor no aparece en la cita; " if not r.val_ok else "") + ("fuera de rango; " if r.rango_mal else "") + ("método ambiguo; " if r.metodo_ambiguo == True else "")
                        + ("duplicado; " if r.duplicado == True else "")} for r in g.itertuples()]
    (OUT / "lotes" / f"{lote}.json").write_text(json.dumps({"lote": lote, "filas": filas}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(d)} filas; dudosas: {len(dud)} en {dud.lote.nunique()} lotes de {POR_LOTE}")
