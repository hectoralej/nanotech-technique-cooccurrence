"""Define el conjunto de revision humana (60), el piloto (100) y los lotes de extraccion; escribe los paquetes de texto.

Semilla fija. El conjunto humano y el piloto son disjuntos (el piloto sirve para ajustar prompts; el humano, para validar).
Salida: curation/work/manifest.csv (pmcid, family, set, batch) y curation/data/human_set.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common import ROOT
from curation import textprep

SEED = 20261010
BATCH = 4
CUR = ROOT / "curation"


def main() -> None:
    rng = np.random.default_rng(SEED)
    cand = pd.read_csv(CUR / "data" / "candidates.csv", dtype={"pmcid": str})
    near = pd.read_csv(CUR / "data" / "prefilter_near_miss.csv", dtype={"pmcid": str})
    fams = ["LNP", "liposome", "SLN_NLC", "PLN", "polymeric", "inorganic"]
    human = []
    for f in fams:
        c = cand[cand.primary_family == f]
        n = near[near.primary_family == f]
        n_near = min(2, len(n))
        pick_n = n.iloc[rng.permutation(len(n))[:n_near]].assign(kind="near_miss_prefilter")
        pick_c = c.iloc[rng.permutation(len(c))[:10 - n_near]].assign(kind="candidate")
        human += [pick_c[["pmcid", "primary_family", "title", "kind"]], pick_n[["pmcid", "primary_family", "title", "kind"]]]
    human = pd.concat(human, ignore_index=True)
    human.to_csv(CUR / "data" / "human_set.csv", index=False)
    rest = cand[~cand.pmcid.isin(human.pmcid)]
    pilot = []
    per = 100 // len(fams)
    for f in fams:
        c = rest[rest.primary_family == f]
        pilot.append(c.iloc[rng.permutation(len(c))[: per + (1 if f in ("polymeric", "SLN_NLC", "LNP", "liposome") else 0)]])
    pilot = pd.concat(pilot)
    pilot = pilot.iloc[:100]
    main_ = rest[~rest.pmcid.isin(pilot.pmcid)]
    rows = []
    for name, df, prefix in (("human", human, "H"), ("pilot", pilot, "P"), ("main", main_, "M")):
        ids = df.sample(frac=1, random_state=SEED)
        for i, (_, r) in enumerate(ids.iterrows()):
            rows.append(dict(pmcid=r.pmcid, family=r.primary_family, set=name, batch=f"{prefix}{i // BATCH + 1:03d}"))
    man = pd.DataFrame(rows)
    (CUR / "work").mkdir(exist_ok=True)
    man.to_csv(CUR / "work" / "manifest.csv", index=False)
    textprep.write_packets(man.pmcid.tolist())
    print(man.groupby(["set", "family"]).size().unstack(0).fillna(0).astype(int))
    print("batches:", man.groupby("set").batch.nunique().to_dict())


if __name__ == "__main__":
    main()
