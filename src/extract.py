"""Descarga + parseo + deteccion para una lista de articulos; muestreo adaptativo con criterio de parada.

Salidas (acumulativas, idempotentes por PMCID):
  data/articles_all.csv   una fila por articulo procesado (incluye los fuera de alcance, con motivo)
  data/evidence.csv       una fila por (articulo, tecnica) detectada: seccion y fragmento <= 25 palabras
"""
from __future__ import annotations

import argparse
import sys

import pandas as pd

from .common import DATA, load_yaml, log_event, now_iso
from .detect import DEFINITIONS, SECTION_ORDER, definition, detect, load_techniques, technique_names
from .fulltext import fetch_many, load_parsed
from .prec import median_halfwidth

ARTICLES = DATA / "articles_all.csv"
EVIDENCE = DATA / "evidence.csv"
IN_SCOPE_TYPES = {"research-article", "brief-report", "rapid-communication", "other", "report", None, ""}

HEADLINE = load_yaml("sampling.yaml")["headline_definition"]
MICRO = ["cryoEM", "TEM", "STEM", "SEM", "AFM"]
SPECTRA = ["UVVis", "FTIR", "XRD", "NMR", "EDS", "SAXS", "Raman_SERS", "XPS"]


def figure_level_pairs(captions: str) -> list[str]:
    """Tecnicas espectrales que aparecen en el *mismo* pie de figura que una tecnica de microscopia (proxy H9)."""
    found: set[str] = set()
    for cap in captions.split("\n"):
        if len(cap) < 20:
            continue
        r = detect({"caption": cap})
        if any(r[m]["caption"] for m in MICRO):
            found.update(s for s in SPECTRA if r[s]["caption"])
    return sorted(found)


def process_article(pmcid: str, meta: dict) -> tuple[dict, list[dict]]:
    row = {k: meta.get(k) for k in ("pmcid", "pmid", "doi", "year", "journal", "license", "license_group", "period",
                                   "primary_family", "subtype", "families_matched", "analysis_set", "stratum",
                                   "N_stratum", "rank_in_family", "title")}
    parsed = load_parsed(pmcid)
    row["retrieved"] = now_iso()
    if parsed is None:
        row.update(fulltext_status="missing", in_scope=False, exclusion="no_fulltext")
        return row, []
    row["fulltext_status"] = "ok"
    row.update(article_type=parsed["article_type"], parse_ok=parsed["parse_ok"], has_methods=parsed["has_methods"],
               has_results=parsed["has_results"], n_chars=parsed["n_chars"], n_captions=parsed["n_captions"])
    reason = ""
    if parsed["article_type"] not in IN_SCOPE_TYPES:
        reason = f"type:{parsed['article_type']}"
    elif not parsed["parse_ok"]:
        reason = "unparsable_or_short"
    row["in_scope"] = reason == ""
    row["exclusion"] = reason
    secs = dict(parsed["sections"])
    secs["abstract"] = parsed["abstract"] or ""
    res = detect(secs)
    evid = []
    for t, rec in res.items():
        row[t] = definition(rec, HEADLINE)
        for s, short in (("methods", "m"), ("results", "r"), ("caption", "c"), ("other", "o"), ("abstract", "a")):
            row[f"{t}__{short}"] = rec[s]
        row[f"{t}__n"] = rec["n_mentions"]
        for sub, v in rec["subflags"].items():
            row[f"sub__{sub}"] = v
        if rec["evidence"]:
            evid.append({"pmcid": pmcid, "technique": t, "evidence_section": rec["evidence_section"],
                         "evidence": rec["evidence"]})
    pairs = figure_level_pairs(parsed["sections"].get("caption", ""))
    row["figms_techs"] = "|".join(pairs)
    row["figms_any"] = bool(pairs)
    return row, evid


def _load(path):
    return pd.read_csv(path, dtype={"pmcid": str}, low_memory=False) if path.exists() else pd.DataFrame()


def process_batch(order: pd.DataFrame, workers: int = 3) -> pd.DataFrame:
    """Procesa los PMCID de `order` que aun no estan en articles_all.csv. Devuelve las filas nuevas."""
    done = _load(ARTICLES)
    seen = set(done["pmcid"]) if len(done) else set()
    todo = order[~order["pmcid"].isin(seen)]
    if todo.empty:
        return pd.DataFrame()
    status = fetch_many(todo["pmcid"].tolist(), workers=workers)
    rows, evs = [], []
    for _, r in todo.iterrows():
        row, ev = process_article(r["pmcid"], r.to_dict())
        row["fetch_status"] = status.get(r["pmcid"])
        rows.append(row)
        evs.extend(ev)
    new = pd.DataFrame(rows)
    out = pd.concat([done, new], ignore_index=True) if len(done) else new
    out.to_csv(ARTICLES, index=False)
    ev_old = _load(EVIDENCE)
    ev_new = pd.DataFrame(evs)
    pd.concat([ev_old, ev_new], ignore_index=True).to_csv(EVIDENCE, index=False)
    return new


def reprocess_all() -> None:
    """Recalcula detecciones de todo lo ya procesado (tras cambiar diccionarios) sin volver a descargar."""
    done = _load(ARTICLES)
    if done.empty:
        return
    meta_cols = [c for c in done.columns if c in ("pmcid", "pmid", "doi", "year", "journal", "license", "license_group", "period",
                                                  "primary_family", "subtype", "families_matched", "analysis_set", "stratum",
                                                  "N_stratum", "rank_in_family", "title")]
    order = done[meta_cols]
    bak_a, bak_e = ARTICLES.with_suffix(".bak"), EVIDENCE.with_suffix(".bak")
    bak_a.unlink(missing_ok=True)
    bak_e.unlink(missing_ok=True)
    ARTICLES.rename(bak_a)
    if EVIDENCE.exists():
        EVIDENCE.rename(bak_e)
    try:
        process_batch(order)
    except BaseException:                                  # restaura lo anterior si algo falla
        ARTICLES.unlink(missing_ok=True)
        EVIDENCE.unlink(missing_ok=True)
        bak_a.rename(ARTICLES)
        if bak_e.exists():
            bak_e.rename(EVIDENCE)
        raise
    bak_a.unlink(missing_ok=True)
    bak_e.unlink(missing_ok=True)


def adaptive_sampling(max_total: int | None = None) -> None:
    samp = load_yaml("sampling.yaml")
    order = pd.read_csv(DATA / "ids" / "sample_order.csv", dtype={"pmcid": str})
    main = order[order["analysis_set"] == "main"]
    core = technique_names("core")
    cap = max_total or samp["cap_total"]
    targets = samp["targets"]
    batch = samp["batch_size"]
    state = {f: {"taken": 0, "done": False} for f in targets}
    # el piloto (primeros pilot_per_family) ya se proceso; continuamos desde ahi
    while True:
        progressed = False
        done_all = _load(ARTICLES)
        n_total = int(len(done_all[done_all["analysis_set"] == "main"])) if len(done_all) else 0
        if n_total >= cap:
            print(f"tope total alcanzado: {n_total}")
            break
        for fam in targets:
            if state[fam]["done"]:
                continue
            fo = main[main["primary_family"] == fam]
            done_f = done_all[(done_all["primary_family"] == fam) & (done_all["analysis_set"] == "main")] if len(done_all) else pd.DataFrame()
            n_scope = int(done_f["in_scope"].sum()) if len(done_f) else 0
            hw, ncell = (float("nan"), 0)
            if n_scope:
                hw, ncell = median_halfwidth(done_f[done_f["in_scope"].astype(bool)], core, samp["stop_min_nA"])
            reached = n_scope >= targets[fam] and (hw == hw and hw <= samp["stop_halfwidth_median"])
            pending = fo[~fo["pmcid"].isin(set(done_f["pmcid"]) if len(done_f) else set())].sort_values("rank_in_family")
            exhausted = pending.empty
            print(f"[{fam}] procesados={len(done_f)} en_alcance={n_scope} objetivo={targets[fam]} "
                  f"halfwidth_mediana={hw:.3f} celdas={ncell} N_pob={len(fo)}", flush=True)
            if reached or exhausted:
                state[fam]["done"] = True
                log_event("sampling_stop", family=fam, n_scope=n_scope, halfwidth=hw, reached=bool(reached), exhausted=bool(exhausted))
                continue
            # siguientes sin procesar en orden de rango (el piloto y el conjunto de validacion pueden estar intercalados)
            process_batch(pending.head(batch))
            progressed = True
        if not progressed:
            break


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--trend", action="store_true", help="procesa la submuestra 2015-2017 (solo tendencia)")
    ap.add_argument("--scale", action="store_true")
    ap.add_argument("--reprocess", action="store_true")
    ap.add_argument("--cap", type=int, default=None)
    a = ap.parse_args()
    samp = load_yaml("sampling.yaml")
    order = pd.read_csv(DATA / "ids" / "sample_order.csv", dtype={"pmcid": str})
    if a.pilot:
        pil = order[(order["analysis_set"] == "main") & (order["rank_in_family"] <= samp["pilot_per_family"])]
        new = process_batch(pil)
        print(f"piloto: {len(new)} articulos nuevos")
    if a.trend:
        new = process_batch(order[order["analysis_set"] == "trend_only"])
        print(f"tendencia: {len(new)} articulos nuevos")
    if a.scale:
        adaptive_sampling(a.cap)
    if a.reprocess:
        reprocess_all()


if __name__ == "__main__":
    main()
