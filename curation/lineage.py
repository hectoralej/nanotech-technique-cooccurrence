"""Duplicados, clusters de laboratorio y linaje metodologico.

- Duplicados reales: titulo casi identico (>= 92) o >= 3 valores numericos de DLS/zeta identicos compartidos entre articulos distintos (datos reutilizados).
  Se conserva UNA version (la de licencia mas permisiva y luego la mas reciente) y las otras se registran con la razon. Mismo laboratorio con datos distintos NO se elimina.
- Clusters de laboratorio (lab_cluster_id): componentes conexas por mismo ultimo autor (senior) o >= 3 autores en comun.
- Linaje: referencias citadas en parrafos de Metodos con frases de protocolo ("as described", "according to", "previously reported"...).
  Dos articulos que citan la misma referencia de protocolo quedan en el mismo grupo de linaje (grafo en lineage_graph.graphml).
"""
from __future__ import annotations

import json
import re

import networkx as nx
import pandas as pd
from lxml import etree
from rapidfuzz import fuzz

from src.common import ROOT
from src.fulltext import FT_DIR, _clean
from curation import textprep

CUR = ROOT / "curation"
PROTO = re.compile(r"as described|as previously|previously (?:reported|described|published|established)|according to|following the (?:method|protocol|procedure)|"
                   r"based on (?:the )?(?:method|protocol)|modified from|adapted from|method (?:of|by|described)|protocol (?:of|by|described)|as reported", re.I)
LIC_RANK = {"verde": 0, "amarillo": 1, "rojo": 2}


def _norm_name(n: str) -> str:
    return re.sub(r"[^a-z ]", "", (n or "").lower()).strip()


def protocol_refs(pmcid: str) -> list[str]:
    root = etree.fromstring((FT_DIR / f"{pmcid}.xml").read_bytes(), parser=etree.XMLParser(recover=True, huge_tree=True, resolve_entities=False, no_network=True))
    refs = {}
    for ref in root.xpath(".//ref-list/ref"):
        doi = ref.xpath(".//pub-id[@pub-id-type='doi']/text()")
        pmid = ref.xpath(".//pub-id[@pub-id-type='pmid']/text()")
        title = _clean("".join(ref.xpath(".//article-title//text()")))[:120].lower()
        refs[ref.get("id")] = ("doi:" + doi[0].lower()) if doi else (("pmid:" + pmid[0]) if pmid else ("title:" + re.sub(r"\W+", " ", title).strip()))
    out = set()
    for sec in root.xpath(".//body/sec"):
        t = sec.find("title")
        title = _clean("".join(t.itertext())).lower() if t is not None else ""
        if not re.search(r"method|material|experimental|procedure", title):
            continue
        for p in sec.xpath(".//p"):
            txt = " ".join(p.itertext())
            if PROTO.search(txt):
                for x in p.xpath(".//xref[@ref-type='bibr']"):
                    for rid in (x.get("rid") or "").split():
                        if rid in refs and refs[rid] != "title:":
                            out.add(refs[rid])
    return sorted(out)


def value_fingerprint(rec: dict) -> set:
    vals = set()
    for m in rec.get("measurements", []):
        v = m.get("values") or {}
        for k in ("size_nm", "zeta_mV"):
            try:
                x = float(v.get(k))
                vals.add((k, round(x, 2)))
            except (TypeError, ValueError):
                pass
    return vals


def build(final_ids: list[str], recs: dict, meta: pd.DataFrame, lic_color: dict[str, str] | None = None):
    meta = meta.set_index("pmcid")
    G = nx.Graph()
    G.add_nodes_from(final_ids)
    authors = {}
    for p in final_ids:
        a = json.loads(meta.loc[p, "authors_json"]) if p in meta.index and isinstance(meta.loc[p, "authors_json"], str) else []
        authors[p] = [_norm_name(x["name"]) for x in a]
    last = {p: (authors[p][-1] if authors[p] else "") for p in final_ids}
    for i, p in enumerate(final_ids):
        for q in final_ids[i + 1:]:
            shared = set(authors[p]) & set(authors[q])
            if (last[p] and last[p] == last[q]) or len(shared) >= 3:
                G.add_edge(p, q, kind="lab")
    comps = sorted(nx.connected_components(G), key=lambda c: (-len(c), sorted(c)[0]))
    cluster = {}
    for k, comp in enumerate(comps, 1):
        for p in comp:
            cluster[p] = f"LC{k:04d}"
    size = {p: len(next(c for c in comps if p in c)) for p in final_ids}
    # duplicados
    dups = []
    titles = {p: (meta.loc[p, "title"] if p in meta.index else "") for p in final_ids}
    vf = {p: value_fingerprint(recs[p]) for p in final_ids}
    for i, p in enumerate(final_ids):
        for q in final_ids[i + 1:]:
            r = fuzz.ratio(str(titles[p]).lower(), str(titles[q]).lower())
            shared_vals = len(vf[p] & vf[q])
            if r >= 92 or shared_vals >= 3:
                dups.append(dict(a=p, b=q, title_similarity=round(r, 1), shared_numeric_values=shared_vals,
                                 reason="titulo casi identico" if r >= 92 else "valores de DLS/zeta compartidos (posible reutilizacion de datos)"))
    # linaje
    L = nx.Graph()
    edges = []
    for p in final_ids:
        for ref in protocol_refs(p):
            L.add_edge(p, ref)
            edges.append(dict(article=p, protocol_ref=ref))
    lineage_group = {}
    for k, comp in enumerate([c for c in nx.connected_components(L) if sum(1 for n in c if n.startswith("PMC")) >= 2], 1):
        for n in comp:
            if n.startswith("PMC"):
                lineage_group[n] = f"LG{k:03d}"
    nx.write_graphml(L, CUR / "lineage_graph.graphml")
    return cluster, size, pd.DataFrame(dups), pd.DataFrame(edges), lineage_group
