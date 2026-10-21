"""Busqueda dirigida a vacios de tecnica (SAXS) en Europe PMC: solo acceso abierto, licencia CC BY, sin virus/AAV.

Guarda las paginas crudas en data/cache/search/gap_saxs/ (asi curation.meta las encuentra), descarga el texto completo de los candidatos nuevos,
calcula las banderas baratas de curation.cheap_filter y escribe curation/data/gap_candidates.csv.

  python -m curation.gap_search
"""
from __future__ import annotations

import json
import re

import pandas as pd

from src.common import CACHE, DATA, EPMC, load_yaml, log_event, make_client
from src.fulltext import FT_DIR, fetch_many
from curation import cheap_filter as cf

CUR = DATA.parent / "curation"
CARRIERS = ('liposom* OR "lipid nanoparticle*" OR "solid lipid nanoparticle*" OR "nanostructured lipid carrier*" OR "polymeric nanoparticle*" OR PLGA OR "lipid-polymer" '
            'OR "mesoporous silica" OR "gold nanoparticle*" OR "iron oxide" OR "silica nanoparticle*" OR nanocarrier*')
QUERY = ('("small-angle X-ray scattering" OR "small angle X-ray scattering" OR SAXS) AND ("zeta potential" OR "zeta-potential") '
         'AND ("transmission electron microscopy" OR "cryo-TEM" OR "cryo-electron microscopy" OR "scanning electron microscopy") '
         f'AND ({CARRIERS}) AND OPEN_ACCESS:y AND (FIRST_PDATE:[2018-01-01 TO 2026-10-18]) AND NOT PUB_TYPE:"review" '
         'AND NOT (AAV OR "adeno-associated" OR lentivir* OR bacteriophage OR "virus-like" OR "viral vector*")')


def family_of(title: str, abstract: str, fams: dict) -> str:
    txt = f"{title} {abstract}"
    counts = {f: len(re.findall(c["count_regex"], txt, flags=re.I)) for f, c in fams.items() if f != "AAV"}
    best = max(counts, key=counts.get)
    return best if counts[best] else "otra"


def main(max_pages: int = 3) -> None:
    client = make_client()
    fams = load_yaml("families.yaml")["families"]
    qdir = CACHE / "search" / "gap_saxs"
    qdir.mkdir(parents=True, exist_ok=True)
    rows, cursor = [], "*"
    for page in range(max_pages):
        r = client.get(f"{EPMC}/search", params={"query": QUERY, "format": "json", "resultType": "core", "pageSize": 100, "cursorMark": cursor})
        r.raise_for_status()
        payload = r.json()
        (qdir / f"page_{page:04d}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        log_event("gap_search", page=page, hitCount=payload.get("hitCount"), query=QUERY)
        for x in payload.get("resultList", {}).get("result", []):
            rows.append(dict(pmcid=x.get("pmcid"), doi=x.get("doi"), title=x.get("title"), abstract=x.get("abstractText") or "", year=x.get("pubYear"),
                             license=x.get("license"), pub_types="|".join((x.get("pubTypeList") or {}).get("pubType", []) or [])))
        nxt = payload.get("nextCursorMark")
        if not payload.get("resultList", {}).get("result") or not nxt or nxt == cursor:
            break
        cursor = nxt
    df = pd.DataFrame(rows)
    print("hitCount:", payload.get("hitCount"), "| descargados:", len(df))
    df = df[df.pmcid.notna() & df.doi.notna()].drop_duplicates("pmcid")
    df = df[df.license.astype(str).str.lower().eq("cc by")]
    seen = set(pd.read_csv(DATA / "articles_all.csv", dtype={"pmcid": str}, low_memory=False, usecols=["pmcid"]).pmcid)
    df = df[~df.pmcid.isin(seen)]
    print("CC BY, con DOI y nuevos para el corpus:", len(df))
    st = fetch_many(df.pmcid.tolist())
    df = df[df.pmcid.map(lambda p: (FT_DIR / f"{p}.xml").exists())].copy()
    feats = []
    for p in df.pmcid:
        try:
            feats.append(cf.features(p))
        except Exception as exc:  # noqa: BLE001
            feats.append(dict(pmcid=p, error=str(exc)[:80]))
    f = pd.DataFrame(feats).drop(columns=["title"], errors="ignore")
    out = df.merge(f, on="pmcid", how="left")
    out["family"] = [family_of(t or "", a or "", fams) for t, a in zip(out.title, out.abstract)]
    out.drop(columns=["abstract"]).to_csv(CUR / "data" / "gap_candidates.csv", index=False)
    ok = out[(out.saxs > 0) & (out.micro_cap > 0) & ~out.review_title.fillna(True).astype(bool) & ~out.virus_text.fillna(True).astype(bool)]
    print("con SAXS en el texto + micrografia en figura, sin virus ni revision:", len(ok))
    print(ok.family.value_counts().to_dict())


if __name__ == "__main__":
    main()
