"""Lista de ~80 articulos para la verificacion humana (version 'paso 0 ampliado').

Composicion:
  - conjunto humano original (H-set): los que tienen licencia verde verificada
  - vacios de tecnica: SAXS (busqueda dirigida, gap_candidates.csv), cryo-EM, inorganicas y espectroscopia sobre la particula (del pool ya descargado)
Solo licencia verde (CC BY / CC0) confirmada por Europe PMC y por el XML; nada de AAV ni virus.

  python -m curation.select_verification        -> work/verif_candidates.csv, filas nuevas en manifest, paquetes de texto, lotes VB##
"""
from __future__ import annotations

import json

import pandas as pd

from src.common import DATA, ROOT
from curation import build_outputs as bo, meta, textprep

CUR = ROOT / "curation"
ABS = r"C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence\curation"
# SAXS (busqueda dirigida): elegidos por titulo entre los que cumplen micrografia + tamano + zeta + medio + SAXS en el texto; la familia es la del proyecto mas cercana
SAXS_PICKS = {
    "PMC13155039": "LNP", "PMC7563888": "LNP", "PMC8855343": "polymeric", "PMC13348654": "LNP", "PMC11852004": "liposome", "PMC12547526": "liposome",
    "PMC9346610": "LNP", "PMC7696353": "LNP", "PMC11508592": "LNP", "PMC9965208": "polymeric", "PMC10933724": "liposome", "PMC9736248": "liposome",
    "PMC8617923": "polymeric", "PMC9047672": "LNP", "PMC7587581": "inorganic", "PMC5874870": "inorganic", "PMC10238907": "inorganic",
    "PMC11526376": "inorganic", "PMC10798250": "PLN", "PMC9727730": "LNP",
}
QUOTAS = {"cryo": 6, "inorganic": 9, "liposome": 4, "polymeric": 4, "LNP": 3}   # del pool ya descargado


def main() -> None:
    man = pd.read_csv(CUR / "work" / "manifest.csv", dtype={"pmcid": str})
    gap = pd.read_csv(CUR / "data" / "gap_candidates.csv", dtype={"pmcid": str})
    # 1) filas nuevas del manifiesto para los SAXS
    new = gap[gap.pmcid.isin(SAXS_PICKS) & ~gap.pmcid.isin(man.pmcid)]
    add = pd.DataFrame(dict(pmcid=new.pmcid, family=new.pmcid.map(SAXS_PICKS), set="gap", batch="G001"))
    man = pd.concat([man, add], ignore_index=True)
    man.to_csv(CUR / "work" / "manifest.csv", index=False)
    meta.build()                                                    # metadatos (DOI, revista, licencia) de todo el manifiesto
    textprep.write_packets(add.pmcid.tolist())
    # 2) pool ya descargado: cryo-EM, inorganicas y espectroscopia sobre la particula
    a = pd.read_csv(DATA / "articles_all.csv", dtype={"pmcid": str}, low_memory=False)
    cs = pd.read_csv(CUR / "data" / "cheap_scores_main.csv", dtype={"pmcid": str})
    done = set(pd.read_csv(CUR / "work" / "expand_rounds.csv", dtype={"pmcid": str}).pmcid) | set(man[man.set != "main"].pmcid)
    mt = pd.read_csv(CUR / "data" / "article_meta.csv", dtype={"pmcid": str})[["pmcid", "license_epmc"]]
    pool = cs[~cs.pmcid.isin(done)].merge(mt, on="pmcid").merge(a[["pmcid"] + [c for c in a.columns if c.endswith(("__m", "__r", "__c"))]], on="pmcid")
    pool = pool[pool.license_epmc.astype(str).str.lower().eq("cc by") & ~pool.review_title.astype(bool) & ~pool.virus_text.astype(bool)]
    anyt = lambda t: pool[f"{t}__m"].astype(bool) | pool[f"{t}__r"].astype(bool) | pool[f"{t}__c"].astype(bool)   # noqa: E731
    pool["spec"] = anyt("XRD") | anyt("FTIR") | anyt("UVVis") | anyt("Raman_SERS") | anyt("XPS") | anyt("EDS")
    pool["cryo"] = anyt("cryoEM")
    base = pool[(pool.micro_cap > 0) & (pool.dls_med_par > 0) & (pool.zeta_med_par > 0) & ((pool.dls_val_sent > 0) | pool.size_table.astype(bool))
                & ((pool.zeta_val_sent > 0) | pool.zeta_table.astype(bool)) & pool.spec]
    picks, used = [], set()
    for key, n in QUOTAS.items():
        g = base[(base.cryo & base.family.isin(["LNP", "liposome", "PLN", "polymeric", "SLN_NLC"])) if key == "cryo" else (base.family == key) & ~base.cryo]
        g = g[~g.pmcid.isin(used)].sort_values(["both_table", "priority"], ascending=False).head(n)
        used |= set(g.pmcid)
        picks.append(g.assign(source=f"pool: {key}"))
    pool_sel = pd.concat(picks)
    # 3) lista total
    hs = pd.read_csv(CUR / "data" / "human_set.csv", dtype={"pmcid": str})
    hl = pd.read_csv(CUR / "work" / "hset_license.csv", dtype={"pmcid": str})
    hs = hs.merge(hl[["pmcid", "license_color"]], on="pmcid")
    tot = pd.concat([hs[hs.license_color == "verde"][["pmcid", "primary_family"]].rename(columns={"primary_family": "family"}).assign(source="conjunto humano (aleatorio)"),
                     pd.DataFrame(dict(pmcid=list(SAXS_PICKS), family=list(SAXS_PICKS.values()), source="vacio: SAXS (busqueda dirigida)")),
                     pool_sel[["pmcid", "family", "source"]]], ignore_index=True).drop_duplicates("pmcid")
    mt2 = pd.read_csv(CUR / "data" / "article_meta.csv", dtype={"pmcid": str})
    tot = tot.merge(mt2[["pmcid", "doi", "title", "year", "journal", "license_epmc"]], on="pmcid", how="left")
    lic = bo.license_check(tot.assign(license_epmc=tot.license_epmc))
    tot = tot.merge(lic[["pmcid", "license_xml", "license_color", "license_note"]], on="pmcid")
    tot.to_csv(CUR / "work" / "verif_candidates_all.csv", index=False)
    print(tot.groupby(["source", "license_color"]).size().unstack(fill_value=0))
    ok = tot[(tot.license_color == "verde") & tot.doi.notna()].copy()
    ok.to_csv(CUR / "work" / "verif_candidates.csv", index=False)
    print("candidatos con licencia verde y DOI:", len(ok))
    # 4) lotes Sonnet (paquete completo)
    textprep.write_packets(ok.pmcid.tolist())
    existing = len(list((CUR / "work" / "batches").glob("VB*.json")))
    ids = ok.pmcid.tolist()
    plan = []
    for i in range(0, len(ids), 4):
        bid = f"VB{existing + i // 4 + 1:02d}"
        g = ids[i:i + 4]
        b = {"batch": bid, "articles": [{"pmcid": p, "packet": f"{ABS}\\work\\packets\\{p}.txt"} for p in g], "output_B": f"{ABS}\\work\\llm\\B\\{bid}.json"}
        (CUR / "work" / "batches" / f"{bid}.json").write_text(json.dumps(b, indent=1), encoding="utf-8")
        plan += [dict(pmcid=p, batch_B=bid) for p in g]
    pd.DataFrame(plan).to_csv(CUR / "work" / "verif_B_plan.csv", index=False)
    print("lotes:", len(set(x["batch_B"] for x in plan)))


if __name__ == "__main__":
    main()
