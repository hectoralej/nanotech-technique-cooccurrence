"""Recoleccion de IDs por familia (Europe PMC, cursorMark) con cache cruda, y consolidacion.

Salidas:
  data/ids/ids_<family>.csv      articulos devueltos por cada consulta (metadatos, sin texto completo)
  data/ids/universe.csv          union deduplicada por PMCID con familias coincidentes y familia primaria
  data/ids/strata_counts.csv     totales por estrato (familia primaria x periodo x licencia), con fecha
"""
from __future__ import annotations

import json
import re
import sys
import urllib.parse

import pandas as pd

from .common import CACHE, DATA, EPMC, load_yaml, log_event, make_client, now_iso


def build_query(fam: dict, search_cfg: dict) -> str:
    terms = []
    for p in fam["phrases"]:
        terms.append(f'TITLE:"{p}"')
        terms.append(f'ABSTRACT:"{p}"')
    q = "(" + " OR ".join(terms) + ")"
    if fam.get("and_any"):
        ctx = []
        for p in fam["and_any"]:
            ctx.append(f'TITLE:"{p}"')
            ctx.append(f'ABSTRACT:"{p}"')
        q += " AND (" + " OR ".join(ctx) + ")"
    q += " AND OPEN_ACCESS:y"
    q += f' AND (FIRST_PDATE:[{search_cfg["date_from"]} TO {search_cfg["date_to"]}])'
    for pt in search_cfg["exclude_pub_types"]:
        q += f' AND NOT PUB_TYPE:"{pt}"'
    return q


def fetch_family(name: str, fam: dict, search_cfg: dict, client, force: bool = False) -> pd.DataFrame:
    qdir = CACHE / "search" / name
    qdir.mkdir(parents=True, exist_ok=True)
    query = build_query(fam, search_cfg)
    cursor = "*"
    page = 0
    rows = []
    total = None
    while True:
        cache_file = qdir / f"page_{page:04d}.json"
        if cache_file.exists() and not force:
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
        else:
            params = {
                "query": query, "format": "json", "resultType": "core",
                "pageSize": search_cfg["page_size"], "cursorMark": cursor,
            }
            r = client.get(f"{EPMC}/search", params=params)
            r.raise_for_status()
            payload = r.json()
            cache_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            log_event("search_page", family=name, page=page, hitCount=payload.get("hitCount"), query=query)
        total = payload.get("hitCount")
        res = payload.get("resultList", {}).get("result", [])
        for r_ in res:
            jt = ((r_.get("journalInfo") or {}).get("journal") or {}).get("title")
            rows.append({
                "family_query": name,
                "id": r_.get("id"), "source": r_.get("source"),
                "pmid": r_.get("pmid"), "pmcid": r_.get("pmcid"), "doi": r_.get("doi"),
                "title": r_.get("title"), "abstract": r_.get("abstractText"),
                "year": r_.get("pubYear"), "journal": jt,
                "license": r_.get("license"),
                "pub_types": "|".join((r_.get("pubTypeList") or {}).get("pubType", []) or []),
                "first_pub_date": r_.get("firstPublicationDate"),
            })
        nxt = payload.get("nextCursorMark")
        page += 1
        if not res or not nxt or nxt == cursor:
            break
        cursor = nxt
    df = pd.DataFrame(rows)
    df.attrs["hitCount"] = total
    df.attrs["query"] = query
    return df


def count_family_mentions(text: str, fcfg: dict) -> int:
    return len(re.findall(fcfg["count_regex"], text or "", flags=re.IGNORECASE))


def license_group(lic, groups: dict) -> str | None:
    if not isinstance(lic, str) or not lic.strip():
        return None
    l = lic.strip().lower()
    return "cc_by" if l in [g.lower() for g in groups["cc_by"]] else "other"


def period_of(year, periods: dict) -> str | None:
    try:
        y = int(year)
    except (TypeError, ValueError):
        return None
    for name, (a, b) in periods.items():
        if a <= y <= b:
            return name
    return None


def consolidate(frames: dict[str, pd.DataFrame], fams: dict, samp: dict) -> pd.DataFrame:
    allrows = pd.concat(frames.values(), ignore_index=True)
    allrows = allrows[allrows["pmcid"].notna()].copy()
    matched = allrows.groupby("pmcid")["family_query"].apply(lambda s: "|".join(sorted(set(s), key=list(fams).index)))
    uni = allrows.drop_duplicates("pmcid").set_index("pmcid")
    uni["families_matched"] = matched
    uni = uni.reset_index()
    # familia primaria = mayor numero de menciones en titulo+resumen entre las familias coincidentes
    prim, subtypes = [], []
    for _, r in uni.iterrows():
        txt = f"{r['title'] or ''} {r['abstract'] or ''}"
        counts = {f: count_family_mentions(txt, fams[f]) for f in r["families_matched"].split("|")}
        order = list(fams)
        best = sorted(counts, key=lambda f: (-counts[f], order.index(f)))[0]
        prim.append(best)
        st = ""
        sr = fams[best].get("subtype_regex") or {}
        if sr:
            sc = {k: len(re.findall(v, txt, flags=re.IGNORECASE)) for k, v in sr.items()}
            sc = {k: v for k, v in sc.items() if v > 0}
            if sc:
                st = max(sc, key=sc.get)
        if best == "polymeric" and not st:
            st = ""
        # etiqueta PLGA como subfamilia aparte si aparece en cualquier articulo de polimericas
        subtypes.append(st)
    uni["primary_family"] = prim
    uni["subtype"] = subtypes
    uni["license_group"] = uni["license"].map(lambda x: license_group(x, samp["license_groups"]))
    uni["period"] = uni["year"].map(lambda y: period_of(y, samp["periods"]))
    uni["is_review_flag"] = uni["pub_types"].str.contains("review", case=False, na=False)
    return uni


def main(force_families: set[str] | None = None) -> None:
    force_families = force_families or set()
    fam_cfg = load_yaml("families.yaml")
    samp = load_yaml("sampling.yaml")
    client = make_client()
    (DATA / "ids").mkdir(parents=True, exist_ok=True)
    frames, hit_counts = {}, {}
    for name, fam in fam_cfg["families"].items():
        df = fetch_family(name, fam, fam_cfg["search"], client, force=name in force_families or "ALL" in force_families)
        hit_counts[name] = {"hitCount_api": df.attrs["hitCount"], "rows_downloaded": len(df), "query": df.attrs["query"],
                            "retrieved": now_iso()}
        frames[name] = df
        df.drop(columns=["abstract"]).to_csv(DATA / "ids" / f"ids_{name}.csv", index=False)
        print(f"{name}: api hitCount={df.attrs['hitCount']} rows={len(df)}", flush=True)
    uni = consolidate(frames, fam_cfg["families"], samp)
    n0 = len(uni)
    # elegibilidad: licencia registrada y periodo valido
    uni["eligible"] = uni["license_group"].notna() & uni["period"].notna()
    uni.drop(columns=["abstract"]).to_csv(DATA / "ids" / "universe.csv", index=False)
    uni[["pmcid", "abstract"]].to_csv(CACHE / "abstracts.csv", index=False)
    el = uni[uni["eligible"]]
    strata = (el.groupby(["primary_family", "period", "license_group"]).size().rename("N_population").reset_index())
    strata["retrieved"] = now_iso()
    strata.to_csv(DATA / "ids" / "strata_counts.csv", index=False)
    with open(DATA / "ids" / "query_totals.json", "w", encoding="utf-8") as fh:
        json.dump(hit_counts, fh, ensure_ascii=False, indent=2)
    print(f"universe={n0} eligible={len(el)}  (sin licencia o fuera de periodo: {n0 - len(el)})")
    print(strata.groupby("primary_family")["N_population"].sum())


if __name__ == "__main__":
    # uso: python -m src.search [--force ALL|FAMILIA[,FAMILIA]]
    forced = set(sys.argv[sys.argv.index("--force") + 1].split(",")) if "--force" in sys.argv else set()
    main(force_families=forced)
