"""Ronda de ampliacion con Sonnet directo sobre el paquete completo (sin cribado Haiku previo).

Motivo (ronda 1): el cribado con Haiku sobre el paquete corto dejaba fuera 35 % de los articulos que Sonnet luego aprobaba (recall de A = 15/23);
con el filtro barato en nivel A, ir directo a Sonnet cuesta menos por articulo aprobado. Haiku se usa despues como segunda lectura barata de los aprobados.

  python -m curation.select_direct <ronda> <familia[:T1]=n,...> [tam_lote]
Cuota 'familia' = nivel A del filtro barato; 'familia:T1' = nivel T1 (micro en pie de figura, DLS/zeta con valores y medio) que no es A (para familias agotadas).
"""
from __future__ import annotations

import json
import sys

import pandas as pd

from src.common import ROOT

CUR = ROOT / "curation"
ABS = r"C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence\curation"
LOG = CUR / "work" / "expand_rounds.csv"


def main(rnd: str, quotas: dict[str, int], size: int = 4) -> None:
    d = pd.read_csv(CUR / "data" / "cheap_scores_main.csv", dtype={"pmcid": str})
    d["tierA"] = d.both_table.astype(bool) & (d.dls_med_par > 0) & (d.zeta_med_par > 0) & ~d.review_title.astype(bool) & ~d.virus_text.astype(bool)
    done = pd.read_csv(LOG, dtype={"pmcid": str}).pmcid.tolist()
    pool = d[~d.pmcid.isin(done)].copy()
    pool["has_saxs"] = pool.saxs > 0
    pool["has_micro_cap"] = pool.micro_cap > 0
    pick = []
    for key, n in quotas.items():
        fam, _, t = key.partition(":")
        g = pool[(pool.family == fam) & (pool.tierA if not t else (pool.tier == t) & ~pool.tierA)]
        pick.append(g.sort_values(["has_saxs", "has_micro_cap", "priority"], ascending=False).head(n))
    sel = pd.concat(pick).sample(frac=1, random_state=20261013).reset_index(drop=True)
    existing = len(list((CUR / "work" / "batches").glob("QB*.json")))
    rows = []
    for i in range(0, len(sel), size):
        bid = f"QB{existing + i // size + 1:02d}"
        g = sel.iloc[i:i + size]
        b = {"batch": bid, "articles": [{"pmcid": r.pmcid, "packet": f"{ABS}\\work\\packets\\{r.pmcid}.txt"} for r in g.itertuples()],
             "output_B": f"{ABS}\\work\\llm\\B\\{bid}.json"}
        (CUR / "work" / "batches" / f"{bid}.json").write_text(json.dumps(b, indent=1), encoding="utf-8")
        rows += [dict(pmcid=r.pmcid, round=rnd, batch=bid, family=r.family, priority=r.priority, saxs=int(r.saxs)) for r in g.itertuples()]
    new = pd.DataFrame(rows)
    pd.concat([pd.read_csv(LOG, dtype={"pmcid": str}), new]).to_csv(LOG, index=False)
    print(new.groupby("family").size().to_dict(), "| lotes:", sorted(new.batch.unique()), "| con SAXS:", int((new.saxs > 0).sum()))


if __name__ == "__main__":
    q = {kv.rsplit("=", 1)[0]: int(kv.rsplit("=", 1)[1]) for kv in sys.argv[2].split(",")}
    main(sys.argv[1], q, int(sys.argv[3]) if len(sys.argv) > 3 else 4)
