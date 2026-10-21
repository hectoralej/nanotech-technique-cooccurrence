"""Segunda tanda de candidatos para la lista de verificacion humana (completar ~80 tras quitar los no pertinentes).
Cryo-EM del pool ya descargado (sin exigir espectroscopia) y SAXS extra de la busqueda dirigida. Solo licencia verde."""
from __future__ import annotations

import json

import pandas as pd

from src.common import DATA, ROOT
from curation import build_outputs as bo, meta, textprep

CUR = ROOT / "curation"
ABS = r"C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence\curation"
SAXS_EXTRA = {"PMC12590531": "LNP", "PMC10160449": "SLN_NLC", "PMC11728762": "liposome", "PMC10295105": "liposome", "PMC9032237": "liposome",
              "PMC12319434": "liposome", "PMC9316859": "liposome", "PMC13468646": "inorganic"}


def main() -> None:
    man = pd.read_csv(CUR / "work" / "manifest.csv", dtype={"pmcid": str})
    gap = pd.read_csv(CUR / "data" / "gap_candidates.csv", dtype={"pmcid": str})
    new = gap[gap.pmcid.isin(SAXS_EXTRA) & ~gap.pmcid.isin(man.pmcid)]
    man = pd.concat([man, pd.DataFrame(dict(pmcid=new.pmcid, family=new.pmcid.map(SAXS_EXTRA), set="gap", batch="G001"))], ignore_index=True)
    man.to_csv(CUR / "work" / "manifest.csv", index=False)
    meta.build()
    textprep.write_packets(new.pmcid.tolist())
    prev = pd.read_csv(CUR / "work" / "verif_candidates_all.csv", dtype={"pmcid": str})
    a = pd.read_csv(DATA / "articles_all.csv", dtype={"pmcid": str}, low_memory=False)
    cs = pd.read_csv(CUR / "data" / "cheap_scores_main.csv", dtype={"pmcid": str})
    done = set(pd.read_csv(CUR / "work" / "expand_rounds.csv", dtype={"pmcid": str}).pmcid) | set(man[man.set.isin(["human", "pilot"])].pmcid) | set(prev.pmcid)
    mt = pd.read_csv(CUR / "data" / "article_meta.csv", dtype={"pmcid": str})[["pmcid", "license_epmc"]]
    pool = cs[~cs.pmcid.isin(done)].merge(mt, on="pmcid").merge(a[["pmcid"] + [c for c in a.columns if c.endswith(("__m", "__r", "__c"))]], on="pmcid")
    pool = pool[pool.license_epmc.astype(str).str.lower().eq("cc by") & ~pool.review_title.astype(bool) & ~pool.virus_text.astype(bool)]
    cryo = pool["cryoEM__m"].astype(bool) | pool["cryoEM__r"].astype(bool) | pool["cryoEM__c"].astype(bool)
    g = pool[cryo & (pool.micro_cap > 0) & ((pool.dls_val_sent > 0) | pool.size_table.astype(bool)) & ((pool.zeta_val_sent > 0) | pool.zeta_table.astype(bool))
             & pool.family.isin(["LNP", "liposome", "PLN", "polymeric", "SLN_NLC"])].sort_values(["both_table", "priority"], ascending=False).head(5)
    cands = pd.concat([pd.DataFrame(dict(pmcid=list(SAXS_EXTRA), family=list(SAXS_EXTRA.values()), source="vacio: SAXS (busqueda dirigida)")),
                       g[["pmcid", "family"]].assign(source="pool: cryo")], ignore_index=True)
    mt2 = pd.read_csv(CUR / "data" / "article_meta.csv", dtype={"pmcid": str})
    cands = cands.merge(mt2[["pmcid", "doi", "title", "year", "journal", "license_epmc"]], on="pmcid", how="left")
    lic = bo.license_check(cands)
    cands = cands.merge(lic[["pmcid", "license_xml", "license_color", "license_note"]], on="pmcid")
    print(cands.groupby(["source", "license_color"]).size())
    ok = cands[(cands.license_color == "verde") & cands.doi.notna()]
    textprep.write_packets(ok.pmcid.tolist())
    existing = len(list((CUR / "work" / "batches").glob("VB*.json")))
    ids = ok.pmcid.tolist()
    for i in range(0, len(ids), 4):
        bid = f"VB{existing + i // 4 + 1:02d}"
        gg = ids[i:i + 4]
        (CUR / "work" / "batches" / f"{bid}.json").write_text(json.dumps({"batch": bid, "articles": [{"pmcid": p, "packet": f"{ABS}\\work\\packets\\{p}.txt"} for p in gg],
                                                                         "output_B": f"{ABS}\\work\\llm\\B\\{bid}.json"}, indent=1), encoding="utf-8")
        print(bid, gg)
    pd.concat([pd.read_csv(CUR / "work" / "verif_candidates.csv", dtype={"pmcid": str}), ok]).to_csv(CUR / "work" / "verif_candidates.csv", index=False)
    print("anadidos:", len(ok))


if __name__ == "__main__":
    main()
