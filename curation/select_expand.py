"""Selecciona la siguiente ronda de articulos para la ampliacion (nivel A del filtro barato), escribe paquetes cortos y lotes Q###.

  python -m curation.select_expand <ronda> <cuotas familia=n,...> [tam_lote]

Nivel A = tabla con tamano y zeta + metodo de DLS con medio + metodo de zeta con medio/pH (en el piloto: 83 % pasaba la puerta).
Dentro de cada familia se ordena por prioridad; los articulos con SAXS se incluyen primero (vacio detectado).
"""
from __future__ import annotations

import json
import sys

import pandas as pd

from src.common import ROOT
from curation import cheap_filter

CUR = ROOT / "curation"
ABS = r"C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence\curation"
LOG = CUR / "work" / "expand_rounds.csv"


def main(rnd: str, quotas: dict[str, int], size: int = 6) -> None:
    d = pd.read_csv(CUR / "data" / "cheap_scores_main.csv", dtype={"pmcid": str})
    d["tierA"] = ((d.both_table.astype(bool)) & (d.dls_med_par > 0) & (d.zeta_med_par > 0) & ~d.review_title.astype(bool) & ~d.virus_text.astype(bool))
    done = pd.read_csv(LOG, dtype={"pmcid": str}).pmcid.tolist() if LOG.exists() else []
    pool = d[d.tierA & ~d.pmcid.isin(done)].copy()
    pool["has_saxs"] = pool.saxs > 0
    pool["has_micro_cap"] = pool.micro_cap > 0
    pick = []
    for fam, n in quotas.items():
        g = pool[pool.family == fam].sort_values(["has_saxs", "has_micro_cap", "priority"], ascending=False)
        pick.append(g.head(n))
    sel = pd.concat(pick).sample(frac=1, random_state=20261012).reset_index(drop=True)
    cheap_filter.write_short_packets(sel.pmcid.tolist())
    existing = len(list((CUR / "work" / "batches").glob("Q*.json")))
    (CUR / "work" / "batches").mkdir(exist_ok=True)
    rows = []
    for i in range(0, len(sel), size):
        bid = f"Q{existing + i // size + 1:03d}"
        g = sel.iloc[i:i + size]
        b = {"batch": bid,
             "articles": [{"pmcid": r.pmcid, "packet_short": f"{ABS}\\work\\packets_short\\{r.pmcid}.txt", "packet_full": f"{ABS}\\work\\packets\\{r.pmcid}.txt"} for r in g.itertuples()],
             "output_A": f"{ABS}\\work\\llm\\A\\{bid}.json", "output_B": f"{ABS}\\work\\llm\\B\\{bid}.json"}
        (CUR / "work" / "batches" / f"{bid}.json").write_text(json.dumps(b, indent=1), encoding="utf-8")
        rows += [dict(pmcid=r.pmcid, round=rnd, batch=bid, family=r.family, priority=r.priority, saxs=int(r.saxs)) for r in g.itertuples()]
    new = pd.DataFrame(rows)
    pd.concat([pd.read_csv(LOG, dtype={"pmcid": str}), new]).to_csv(LOG, index=False) if LOG.exists() else new.to_csv(LOG, index=False)
    print(new.groupby("family").size().to_dict(), "lotes:", new.batch.nunique(), "| con SAXS:", int(new.saxs.gt(0).sum()))
    sizes = [len(cheap_filter.short_packet(p)) for p in sel.pmcid]
    print("tamano del paquete corto (caracteres): media", int(sum(sizes) / len(sizes)), "max", max(sizes))


if __name__ == "__main__":
    q = dict((kv.split("=")[0], int(kv.split("=")[1])) for kv in sys.argv[2].split(","))
    main(sys.argv[1], q, int(sys.argv[3]) if len(sys.argv) > 3 else 6)
