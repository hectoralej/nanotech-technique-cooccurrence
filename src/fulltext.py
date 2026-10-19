"""Descarga permitida (Europe PMC fullTextXML, solo OA con licencia) y parseo JATS por secciones.

No se redistribuye texto completo: el XML crudo queda en data/cache (ignorado por git) y de el solo
se derivan banderas y fragmentos de evidencia de <= 25 palabras.
"""
from __future__ import annotations

import re
import threading
from concurrent.futures import ThreadPoolExecutor

from lxml import etree

from .common import CACHE, EPMC, log_event, make_client, now_iso

FT_DIR = CACHE / "fulltext"

_METHODS = re.compile(
    r"method|material|experimental|procedure|protocol|star\s*methods|key resources|resource availability|"
    r"method details|quantification and statistical|synthesis and characteri|preparation", re.I)
_RESULTS = re.compile(r"result|findings|characteri[sz]ation of|observations", re.I)
_INTRO = re.compile(r"introduction|background|^overview", re.I)
_DISC = re.compile(r"discussion", re.I)
_CONC = re.compile(r"conclusion|summary|outlook|perspective", re.I)


_SKIP_TITLE = re.compile(
    r"supplement|references?\b|acknowledg|author contrib|funding|conflicts? of interest|competing interest|"
    r"data availability|ethic|consent|abbreviations?|associated data|footnote|disclosure|credit", re.I)
_SKIP_SECTYPE = ("ref-list", "fn-group", "associated-data", "ack", "coi-statement", "data-availability", "supplementary-material",
                 "app", "author-contrib", "funding", "ethics", "notes", "glossary")


def classify_section(title: str | None, sec_type: str | None) -> str:
    t = (title or "").strip()
    st = (sec_type or "").lower()
    if st in _SKIP_SECTYPE or _SKIP_TITLE.search(t):
        return "skip"
    if "result" in t.lower() and ("method" in t.lower() or "material" in t.lower()):
        return "methods"          # raro: "Materials, Methods and Results"; se prefiere no perder el metodo
    if _RESULTS.search(t) and "characteri" not in t.lower():
        return "results"
    if _METHODS.search(t) or "method" in st or "materials" in st:
        return "methods"
    if "result" in st:
        return "results"
    if _INTRO.search(t) or "intro" in st:
        return "intro"
    if _DISC.search(t) or "discussion" in st:
        return "discussion"
    if _CONC.search(t) or "conclusion" in st:
        return "conclusion"
    if _RESULTS.search(t):
        return "results"
    return "other"


def _fetch_one(pmcid: str, client, lock: threading.Lock) -> str:
    path = FT_DIR / f"{pmcid}.xml"
    miss = FT_DIR / f"{pmcid}.404"
    if path.exists():
        return "cached"
    if miss.exists():
        return "missing"
    r = client.get(f"{EPMC}/{pmcid}/fullTextXML")
    log_event("fulltext", pmcid=pmcid, status=r.status_code)
    if r.status_code == 200 and r.content:
        path.write_bytes(r.content)
        return "ok"
    if r.status_code in (404, 403, 410):
        miss.write_text(f"{r.status_code} {now_iso()}")
        return "missing"
    r.raise_for_status()
    return "error"


def fetch_many(pmcids: list[str], workers: int = 3) -> dict[str, str]:
    FT_DIR.mkdir(parents=True, exist_ok=True)
    client = make_client()      # el limitador de tasa es compartido y con candado
    lock = threading.Lock()
    out: dict[str, str] = {}

    def run(p):
        try:
            return p, _fetch_one(p, client, lock)
        except Exception as exc:  # noqa: BLE001 - se registra y se sigue
            log_event("fulltext_error", pmcid=p, err=str(exc)[:200])
            return p, "error"

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for p, st in ex.map(run, pmcids):
            out[p] = st
    return out


# ----------------------------------------------------------------------------------------------
# Parseo JATS
# ----------------------------------------------------------------------------------------------

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _text_no_floats(el) -> str:
    """Texto de un elemento omitiendo figuras, tablas y sus pies (que se recogen aparte)."""
    parts: list[str] = []
    skip = {"fig", "table-wrap", "fig-group", "supplementary-material", "ref-list"}
    block = {"title", "p", "sec", "list-item", "label"}

    def walk(e):
        tag = etree.QName(e).localname if isinstance(e.tag, str) else None
        if tag in skip:
            return
        if tag == "xref":                           # conserva el texto de la cita (p. ej. "Fig. 2")
            parts.append("".join(e.itertext()))
            return
        if tag in block:
            parts.append(" ")
        if e.text:
            parts.append(e.text)
        for ch in e:
            if isinstance(ch.tag, str):
                walk(ch)
            if ch.tail:                             # el 'tail' del hijo pertenece al texto del padre
                parts.append(ch.tail)
        if tag in block:
            parts.append(" ")

    walk(el)
    return _clean("".join(parts))


def parse_jats(xml_bytes: bytes) -> dict:
    parser = etree.XMLParser(recover=True, resolve_entities=False, no_network=True, load_dtd=False, huge_tree=True)
    root = etree.fromstring(xml_bytes, parser=parser)
    out: dict = {"article_type": root.get("article-type"), "sections": {}, "parse_ok": False}
    sec_text: dict[str, list[str]] = {k: [] for k in ("intro", "methods", "results", "discussion", "conclusion", "other")}
    body = root.find(".//body")
    abstract = " ".join(_clean("".join(a.itertext())) for a in root.iterfind(".//front//abstract"))
    out["abstract"] = abstract
    ttl = root.find(".//front//article-title")
    out["title_xml"] = _clean("".join(ttl.itertext())) if ttl is not None else ""
    lic = root.find(".//front//permissions//license")
    if lic is not None:
        href = [v for k, v in lic.attrib.items() if k.endswith("href")]
        out["license_xml"] = href[0] if href else _clean("".join(lic.itertext()))[:200]
    else:
        out["license_xml"] = ""
    if body is not None:
        for ch in body:
            if not isinstance(ch.tag, str):
                continue
            tag = etree.QName(ch).localname
            if tag == "sec":
                t = ch.find("title")
                title = _clean("".join(t.itertext())) if t is not None else ""
                label = classify_section(title, ch.get("sec-type"))
                if label == "skip":
                    continue
                sec_text[label].append(_text_no_floats(ch))
            elif tag == "p":
                sec_text["other"].append(_text_no_floats(ch))
    captions = []
    for cap in root.iterfind(".//body//fig/caption") if body is not None else []:
        captions.append(_clean("".join(cap.itertext())))
    for tw in root.iterfind(".//body//table-wrap") if body is not None else []:
        # tabla = "dato mostrado": pie + encabezados + primera celda de cada fila (nombres de magnitudes/ensayos)
        cap = tw.find("caption")
        bits = ["".join(cap.itertext())] if cap is not None else []
        for th in tw.xpath(".//thead//*[self::th or self::td]"):
            bits.append("".join(th.itertext()))
        for tr in tw.iterfind(".//tbody//tr"):
            first = next((c for c in tr if isinstance(c.tag, str) and etree.QName(c).localname in ("th", "td")), None)
            if first is not None:
                bits.append("".join(first.itertext()))
        captions.append(_clean(" ".join(bits)))
    for cap in root.iterfind(".//body//supplementary-material/caption") if body is not None else []:
        captions.append(_clean("".join(cap.itertext())))
    out["sections"] = {k: "\n".join(v) for k, v in sec_text.items()}
    out["sections"]["caption"] = "\n".join(captions)
    out["has_methods"] = len(out["sections"]["methods"]) > 200
    out["has_results"] = len(out["sections"]["results"]) > 200
    out["n_chars"] = sum(len(v) for v in out["sections"].values())
    out["n_captions"] = len(captions)
    out["parse_ok"] = body is not None and out["n_chars"] > 2000
    return out


def load_parsed(pmcid: str) -> dict | None:
    path = FT_DIR / f"{pmcid}.xml"
    if not path.exists():
        return None
    return parse_jats(path.read_bytes())
