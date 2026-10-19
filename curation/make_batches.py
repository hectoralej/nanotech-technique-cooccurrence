"""Escribe un archivo JSON por lote (curation/work/batches/<id>.json) con rutas absolutas de paquetes y salidas por pasada."""
from __future__ import annotations

import json

import pandas as pd

from src.common import ROOT

CUR = ROOT / "curation"
ABS = r"C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence\curation"


def main() -> None:
    man = pd.read_csv(CUR / "work" / "manifest.csv", dtype={"pmcid": str})
    (CUR / "work" / "batches").mkdir(parents=True, exist_ok=True)
    for p in ("A", "B", "C"):
        (CUR / "work" / "llm" / p).mkdir(parents=True, exist_ok=True)
    for b, g in man.groupby("batch"):
        d = {"batch": b, "articles": [{"pmcid": r.pmcid, "packet": f"{ABS}\\work\\packets\\{r.pmcid}.txt"} for r in g.itertuples()],
             "output_A": f"{ABS}\\work\\llm\\A\\{b}.json", "output_B": f"{ABS}\\work\\llm\\B\\{b}.json"}
        (CUR / "work" / "batches" / f"{b}.json").write_text(json.dumps(d, indent=1), encoding="utf-8")
    print(man.batch.nunique(), "lotes")


if __name__ == "__main__":
    main()
