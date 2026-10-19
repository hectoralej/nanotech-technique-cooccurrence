"""Texto estructurado de un articulo (secciones, figuras, tablas completas), paquetes para los subagentes y texto normalizado para verificar citas.

El XML crudo esta en data/cache/fulltext (no se redistribuye). Los paquetes se escriben en curation/work/packets (ignorados por git).
"""
from __future__ import annotations

import re
from functools import lru_cache

from lxml import etree

from src.common import ROOT
from src.fulltext import FT_DIR, _clean, classify_section

PACKETS = ROOT / "curation" / "work" / "packets"
SKIP_PARENTS = {"ref-list", "back"}
CHAR = re.compile(
    r"DLS|dynamic light|zeta|zetasizer|Malvern|particle size|hydrodynamic|PDI|polydispers|\bTEM\b|\bSEM\b|microscop|micrograph|FTIR|FT-IR|infrared|XRD|diffraction|"
    r"\bUV\b|spectr|absorbance|\bEDS\b|\bEDX\b|\bDSC\b|\bTGA\b|calorim|thermogravim|SAXS|scattering|Raman|NMR|XPS|\bNTA\b|nanoparticle tracking|"
    r"prepared|preparation|synthes|formulat|fabricat|lipid film|thin[- ]film|nanoprecipitation|emulsi|sonicat|extrusion|microfluidic|medium|buffer|PBS|dilut|"
    r"characteri[sz]|size|charge|morpholog|mV\b|\bnm\b", re.I)
NOISE = re.compile(r"\bmice\b|\brats?\b|animal|cell culture|cultured|Western|antibod|flow cytometry|statistic|ELISA|MTT|qPCR|RT-PCR|ethic|histolog|immunohisto", re.I)


def _txt(el) -> str:
    from src.fulltext import _text_no_floats
    return _text_no_floats(el)


def _walk(sec, path, out):
    t = sec.find("title")
    title = _clean("".join(t.itertext())) if t is not None else ""
    here = path + ([title] if title else [])
    for ch in sec:
        if not isinstance(ch.tag, str):
            continue
        tag = etree.QName(ch).localname
        if tag == "p":
            out.append((" > ".join(here), _txt(ch)))
        elif tag == "sec":
            _walk(ch, here, out)
        elif tag in ("list", "disp-quote"):
            out.append((" > ".join(here), _txt(ch)))


@lru_cache(maxsize=64)
def article_text(pmcid: str) -> dict:
    root = etree.fromstring((FT_DIR / f"{pmcid}.xml").read_bytes(),
                            parser=etree.XMLParser(recover=True, resolve_entities=False, no_network=True, load_dtd=False, huge_tree=True))
    ttl = root.find(".//front//article-title")
    d = {"pmcid": pmcid, "title": _clean("".join(ttl.itertext())) if ttl is not None else "",
         "abstract": " ".join(_clean("".join(a.itertext())) for a in root.iterfind(".//front//abstract")),
         "methods": [], "results": [], "other": []}
    body = root.find(".//body")
    if body is not None:
        for sec in body.iterfind("sec"):
            t = sec.find("title")
            title = _clean("".join(t.itertext())) if t is not None else ""
            label = classify_section(title, sec.get("sec-type"))
            if label == "skip":
                continue
            bucket = d["methods"] if label == "methods" else d["results"] if label == "results" else d["other"]
            _walk(sec, [], bucket)
        for p in body.iterfind("p"):
            d["other"].append(("", _txt(p)))
    d["figures"], d["tables"] = [], []
    for fig in root.xpath(".//fig[not(ancestor::ref-list)]"):
        lab = fig.find("label"); cap = fig.find("caption")
        d["figures"].append((_clean("".join(lab.itertext())) if lab is not None else (fig.get("id") or "Fig"),
                             _clean("".join(cap.itertext())) if cap is not None else ""))
    for tw in root.xpath(".//table-wrap[not(ancestor::ref-list)]"):
        lab = tw.find("label"); cap = tw.find("caption")
        rows = []
        for tr in tw.iterfind(".//tr"):
            cells = [_clean("".join(c.itertext())) for c in tr if isinstance(c.tag, str) and etree.QName(c).localname in ("th", "td")]
            if any(cells):
                rows.append(" | ".join(cells))
        foot = tw.find(".//table-wrap-foot")
        d["tables"].append((_clean("".join(lab.itertext())) if lab is not None else (tw.get("id") or "Table"),
                            _clean("".join(cap.itertext())) if cap is not None else "", rows,
                            _clean("".join(foot.itertext())) if foot is not None else ""))
    return d


def full_text(pmcid: str) -> str:
    """Todo el texto citable (para verificar citas)."""
    d = article_text(pmcid)
    parts = [d["title"], d["abstract"]]
    for k in ("methods", "results", "other"):
        parts += [f"{h} {p}" for h, p in d[k]]
    parts += [f"{a} {b}" for a, b in d["figures"]]
    for lab, cap, rows, foot in d["tables"]:
        parts += [lab, cap] + rows + [foot]
    return "\n".join(parts)


def _select(paras, budget):
    keep, used = [], 0
    scored = []
    for i, (h, p) in enumerate(paras):
        s = (2 if CHAR.search(p) else 0) + (1 if CHAR.search(h) else 0) - (2 if NOISE.search(p) and not CHAR.search(p) else 0)
        scored.append((s, i, h, p))
    total = sum(len(p) + len(h) + 5 for _, _, h, p in scored)
    if total <= budget:
        return [(h, p) for _, _, h, p in scored]
    for s, i, h, p in sorted(scored, key=lambda x: (-x[0], x[1])):
        if s <= 0:
            continue
        if used + len(p) > budget:
            continue
        keep.append((i, h, p)); used += len(p) + len(h) + 5
    return [(h, p) for i, h, p in sorted(keep)]


def packet(pmcid: str, budgets=(14000, 14000, 10000, 14000)) -> str:
    d = article_text(pmcid)
    L = [f"PMCID: {pmcid}", f"TITLE: {d['title']}", f"ABSTRACT: {d['abstract']}", "", "=== METHODS ==="]
    L += [f"[{h or 'Methods'}] {p}" for h, p in _select(d["methods"], budgets[0])]
    L += ["", "=== RESULTS (and discussion) ==="]
    L += [f"[{h or 'Results'}] {p}" for h, p in _select(d["results"] + [x for x in d["other"] if CHAR.search(x[1])], budgets[1])]
    L += ["", "=== FIGURE CAPTIONS ==="]
    used = 0
    for lab, cap in d["figures"]:
        if used + len(cap) > budgets[2]:
            break
        L.append(f"[{lab}] {cap}"); used += len(cap)
    L += ["", "=== TABLES ==="]
    used = 0
    for lab, cap, rows, foot in d["tables"]:
        block = f"[{lab}] {cap}\n" + "\n".join(rows[:40]) + (f"\n(note) {foot}" if foot else "")
        if used + len(block) > budgets[3]:
            L.append(f"[{lab}] {cap} (table omitted: packet size limit)"); continue
        L.append(block); used += len(block)
    return "\n".join(L)


def write_packets(pmcids, force=False):
    PACKETS.mkdir(parents=True, exist_ok=True)
    for p in pmcids:
        f = PACKETS / f"{p}.txt"
        if f.exists() and not force:
            continue
        f.write_text(packet(p), encoding="utf-8")


# ------------------------------------------------------------------ verificacion de citas
_NORM_DASH = dict.fromkeys(map(ord, "‐‑‒–—―−­"), "-")


def norm(s: str) -> str:
    s = s.translate(_NORM_DASH).lower()
    return re.sub(r"[^a-z0-9%.+\-=<>/°±µμ]+", " ", s).strip()


def quote_found(quote: str, pmcid: str, threshold: int = 90) -> tuple[bool, int]:
    if not quote or len(quote.split()) < 3:
        return False, 0
    q = norm(quote)
    t = _norm_full(pmcid)
    if q in t:
        return True, 100
    from rapidfuzz import fuzz
    score = int(fuzz.partial_ratio(q, t))
    return score >= threshold, score


@lru_cache(maxsize=256)
def _norm_full(pmcid: str) -> str:
    return norm(full_text(pmcid))
