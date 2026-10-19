"""Metadatos de los articulos (desde las respuestas cacheadas de Europe PMC): autores con afiliacion/ORCID, revista, licencia, hasSuppl, hasData.

Salida: curation/data/article_meta.csv (una fila por articulo del manifiesto) y curation/data/step0_supplementary.csv (resumen del paso 0).
"""
from __future__ import annotations

import glob
import json

import pandas as pd

from src.common import CACHE, ROOT

CUR = ROOT / "curation"


def build() -> pd.DataFrame:
    man = pd.read_csv(CUR / "work" / "manifest.csv", dtype={"pmcid": str})
    want = set(man.pmcid)
    rows = {}
    for f in glob.glob(str(CACHE / "search" / "*" / "page_*.json")):
        d = json.loads(open(f, encoding="utf-8").read())
        for r in d.get("resultList", {}).get("result", []):
            pm = r.get("pmcid")
            if pm in want and pm not in rows:
                authors = []
                for a in ((r.get("authorList") or {}).get("author") or []):
                    aff = [x.get("affiliation") for x in ((a.get("authorAffiliationDetailsList") or {}).get("authorAffiliation") or [])]
                    aid = a.get("authorId") or {}
                    authors.append({"name": a.get("fullName"), "orcid": aid.get("value") if aid.get("type") == "ORCID" else None, "aff": aff[:2]})
                jt = ((r.get("journalInfo") or {}).get("journal") or {}).get("title")
                rows[pm] = dict(pmcid=pm, doi=r.get("doi"), pmid=r.get("pmid"), title=r.get("title"), journal=jt, year=r.get("pubYear"),
                                license_epmc=r.get("license"), hasSuppl=r.get("hasSuppl"), hasData=r.get("hasData"), citedBy=r.get("citedByCount"),
                                pub_types="|".join((r.get("pubTypeList") or {}).get("pubType", []) or []),
                                first_pub_date=r.get("firstPublicationDate"), authors_json=json.dumps(authors, ensure_ascii=False),
                                first_author=authors[0]["name"] if authors else None, last_author=authors[-1]["name"] if authors else None,
                                n_authors=len(authors), author_string=r.get("authorString"))
    df = pd.DataFrame(rows.values())
    df.to_csv(CUR / "data" / "article_meta.csv", index=False)
    print(len(df), "de", len(want), "articulos con metadatos")
    return df


if __name__ == "__main__":
    build()
