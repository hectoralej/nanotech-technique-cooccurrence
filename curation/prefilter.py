"""Paso 1: prefiltro barato sobre los articulos ya procesados (alto recall, sin LLM) y embudo.

Salidas en curation/data/: funnel.csv, candidates.csv, prefilter_excluded.csv (con motivo), prefilter_near_miss.csv.
Una micrografia es TEM/cryo-EM/STEM/SEM (AFM no cuenta); DLS y zeta con la definicion 'body_any' del analisis anterior.
"""
from __future__ import annotations

import re

import pandas as pd

from src.common import DATA, ROOT

CUR = ROOT / "curation" / "data"
VIRUS = re.compile(r"adeno[\s-]?associated|\bAAV\d*\b|lentivir|adenovir|retrovir|baculovir|viral vector|virus[\s-]like|\bVLPs?\b|bacteriophage|\bphage\b|oncolytic|viral capsid|rAAV", re.I)
MICRO = ["cryoEM", "TEM", "STEM", "SEM"]


def run() -> None:
    CUR.mkdir(parents=True, exist_ok=True)
    a = pd.read_csv(DATA / "articles_all.csv", dtype={"pmcid": str}, low_memory=False)
    abs_ = pd.read_csv(DATA / "cache" / "abstracts.csv", dtype={"pmcid": str})
    a = a.merge(abs_, on="pmcid", how="left")
    for t in MICRO + ["DLS", "zeta", "qPCR_ddPCR"]:
        a[f"{t}_b"] = a[f"{t}__m"].astype(bool) | a[f"{t}__r"].astype(bool) | a[f"{t}__c"].astype(bool)
    a["micro"] = a[[f"{t}_b" for t in MICRO]].any(axis=1)
    txt = (a["title"].fillna("") + " " + a["abstract"].fillna(""))
    a["virus_title_abs"] = txt.str.contains(VIRUS)
    rows, excl = [], []
    cur = a.copy()

    def step(name, mask_keep, reason):
        nonlocal cur
        out = cur[~mask_keep(cur)]
        rows.append(dict(step=name, entran=len(cur), salen=len(out), quedan=int(mask_keep(cur).sum())))
        if len(out):
            e = out[["pmcid", "primary_family", "title"]].copy(); e["motivo"] = reason; excl.append(e)
        cur = cur[mask_keep(cur)]

    rows.append(dict(step="procesados (muestra + tendencia)", entran=len(cur), salen=0, quedan=len(cur)))
    step("fuera de alcance (tipo de articulo / sin texto)", lambda d: d["in_scope"].astype(bool), "no es investigacion primaria o sin texto completo")
    step("familia AAV", lambda d: d["primary_family"] != "AAV", "AAV fuera del repositorio (decision del brief)")
    step("virus / vector viral / VLP / fago en titulo o resumen", lambda d: ~d["virus_title_abs"], "portador viral o particula viral")
    near = cur[(cur["micro"].astype(int) + cur["DLS_b"].astype(int) + cur["zeta_b"].astype(int)) == 2].copy()
    step("sin senal de micrografia (TEM/cryo/STEM/SEM)", lambda d: d["micro"], "sin senal de micrografia")
    step("sin senal de DLS", lambda d: d["DLS_b"], "sin senal de DLS")
    step("sin senal de zeta", lambda d: d["zeta_b"], "sin senal de zeta")
    cur = cur.copy()
    cur["pcr_lectura_biologica"] = cur["qPCR_ddPCR_b"]
    rows.append(dict(step="candidatos para extraccion con LLM", entran=len(cur), salen=0, quedan=len(cur)))
    rows.append(dict(step="  de ellos con senal de PCR (se marcan, no se excluyen)", entran=int(cur["pcr_lectura_biologica"].sum()), salen=0, quedan=len(cur)))
    pd.DataFrame(rows).to_csv(CUR / "funnel.csv", index=False)
    pd.concat(excl).to_csv(CUR / "prefilter_excluded.csv", index=False)
    near[["pmcid", "primary_family", "title", "micro", "DLS_b", "zeta_b"]].to_csv(CUR / "prefilter_near_miss.csv", index=False)
    keep = ["pmcid", "pmid", "doi", "year", "journal", "license", "license_group", "primary_family", "subtype", "families_matched", "title", "analysis_set",
            "pcr_lectura_biologica"] + [f"{t}_b" for t in MICRO + ["DLS", "zeta"]]
    cur[keep].to_csv(CUR / "candidates.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False))
    print(cur.groupby("primary_family").size().to_string())


if __name__ == "__main__":
    run()
