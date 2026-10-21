"""Paso 5-8: licencias, duplicados/clusters, tablas finales, grupos de equivalencia, Word APA 7, graficos e INFORME.md. Reanudable (caches en curation/work).

Todo se calcula sobre los articulos con extraccion completa (hoy: piloto); lo no procesado se lista en pending.csv. Las cifras de validacion son PROVISIONALES.
"""
from __future__ import annotations

import json
import re
import time
from collections import Counter

import matplotlib
import pandas as pd
import requests
import yaml

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src.common import ROOT, load_yaml
from curation import equivalence as eq, lineage, merge
from src.fulltext import load_parsed

CUR = ROOT / "curation"
UA = load_yaml("families.yaml")["search"]["user_agent"]
LIC_RE = re.compile(r"creativecommons\.org/(?:licenses|publicdomain)/([a-z\-]+(?:/[0-9.]+)?|zero/1\.0)", re.I)
COLOR_OF = {"by": "verde", "cc0": "verde", "zero": "verde", "by-nc": "amarillo", "by-nc-nd": "amarillo", "by-nc-sa": "amarillo", "by-sa": "amarillo", "by-nd": "amarillo"}
INK, INK2, BLUE, ORANGE, GREEN, YELLOW = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834", "#1baf7a", "#eda100"


LOCKED: list[tuple[str, str]] = []


def save_csv(df: pd.DataFrame, name: str) -> None:
    """Escribe un CSV; si el archivo esta abierto en Excel (PermissionError) lo guarda como <nombre>_nuevo.csv y lo avisa."""
    try:
        df.to_csv(CUR / name, index=False)
    except PermissionError:
        alt = name.replace(".csv", "_nuevo.csv")
        df.to_csv(CUR / alt, index=False)
        LOCKED.append((name, alt))
        print(f"AVISO: {name} esta abierto en otro programa; se guardo como {alt}")

def lic_class(text: str | None) -> str | None:
    """verde / amarillo / rojo a partir de una cadena de licencia (texto, URL o codigo)."""
    if not text or not isinstance(text, str):
        return None
    t = text.lower().replace("_", "-")
    m = re.search(r"creativecommons\.org/(?:licenses|publicdomain)/([a-z\-]+)", t)
    code = m.group(1) if m else None
    if code is None:                                  # texto de licencia sin URL (p. ej. "Creative Commons Attribution License")
        flat = re.sub(r"[\s\-]+", " ", t)
        if re.search(r"\bnc\b", flat) and re.match(r"\s*cc\b", flat):           # codigos cortos de Europe PMC: "cc by-nc", "cc by-nc-nd", "cc by-nc-sa"
            code = "by-nc-nd" if re.search(r"\bnd\b", flat) else ("by-nc-sa" if re.search(r"\bsa\b", flat) else "by-nc")
        elif re.match(r"\s*cc\b", flat) and re.search(r"\bnd\b", flat):
            code = "by-nd"
        elif re.match(r"\s*cc\b", flat) and re.search(r"\bsa\b", flat):
            code = "by-sa"
        elif "noncommercial" in flat or "non commercial" in flat:
            code = "by-nc-nd" if ("noderiv" in flat or "no deriv" in flat) else ("by-nc-sa" if "sharealike" in flat else "by-nc")
        elif "sharealike" in flat or "share alike" in flat:
            code = "by-sa"
        elif "noderiv" in flat or "no deriv" in flat:
            code = "by-nd"
        elif re.search(r"cc0|public domain dedication|cc zero", flat):
            code = "cc0"
        elif re.search(r"creative commons attribution|cc by|cc-by", flat):
            code = "by"
    if code is None:
        t2 = re.sub(r"^cc[\s-]*", "", t.strip())
        if t2.startswith("zero") or t2 == "0":
            code = "cc0"
        else:
            code = re.sub(r"[\s]+", "-", t2.split("/")[0].strip()) if t.strip().startswith("cc") else None
    if code is None:
        return "rojo"
    return COLOR_OF.get(code, "rojo")


def license_check(df: pd.DataFrame) -> pd.DataFrame:
    cache_f = CUR / "work" / "license_cache.json"
    cache = json.loads(cache_f.read_text(encoding="utf-8")) if cache_f.exists() else {}
    rows = []
    for r in df.itertuples():
        c = cache.get(r.pmcid)
        if c is None:
            parsed = load_parsed(r.pmcid) or {}
            c = {"xml": parsed.get("license_xml"), "publisher": None, "publisher_status": None, "checked": time.strftime("%Y-%m-%d")}
            if isinstance(r.doi, str) and r.doi:
                try:
                    resp = requests.get(f"https://doi.org/{r.doi}", headers={"User-Agent": UA}, timeout=30, allow_redirects=True)
                    c["publisher_status"] = resp.status_code
                    if resp.status_code == 200:
                        m = LIC_RE.search(resp.text)
                        c["publisher"] = ("https://creativecommons.org/licenses/" + m.group(1)) if m else "no_encontrada_en_pagina"
                    time.sleep(1.0)
                except Exception as exc:  # noqa: BLE001
                    c["publisher_status"] = f"error:{type(exc).__name__}"
            cache[r.pmcid] = c
            cache_f.write_text(json.dumps(cache, indent=1), encoding="utf-8")
        col_epmc, col_xml, col_pub = lic_class(r.license_epmc), lic_class(c["xml"]), lic_class(c["publisher"]) if c["publisher"] and c["publisher"] != "no_encontrada_en_pagina" else None
        avail = [x for x in (col_epmc, col_xml, col_pub) if x]
        if not avail:
            final, why = "rojo", "sin licencia verificable"
        elif len(set(avail)) > 1 and col_pub:
            final, why = col_pub, f"la pagina del editor fija la licencia (fuente de mayor autoridad); discrepaban: epmc={col_epmc}, xml={col_xml}, editor={col_pub}"
        elif len(set(avail)) > 1:
            final, why = "conflicto", f"fuentes discrepan: epmc={col_epmc}, xml={col_xml}, editor={col_pub}"
        else:
            final, why = avail[0], ("verificada en 3 fuentes" if len(avail) == 3 else f"verificada en {len(avail)} fuente(s); editor: {'no obtenido (' + str(c['publisher_status']) + ')' if col_pub is None else 'ok'}")
        rows.append(dict(pmcid=r.pmcid, license_epmc=r.license_epmc, license_xml=c["xml"], license_publisher=c["publisher"], publisher_http=c["publisher_status"],
                         license_color=final, license_note=why, license_checked=c["checked"]))
    return pd.DataFrame(rows)


def crossref(doi: str) -> dict | None:
    cache_f = CUR / "work" / "crossref_cache.json"
    cache = json.loads(cache_f.read_text(encoding="utf-8")) if cache_f.exists() else {}
    if doi in cache:
        return cache[doi]
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}", headers={"User-Agent": UA}, timeout=30)
        msg = r.json()["message"] if r.status_code == 200 else None
    except Exception:  # noqa: BLE001
        msg = None
    try:
        h = requests.get(f"https://doi.org/{doi}", headers={"User-Agent": UA}, timeout=30, allow_redirects=False)
        resolves = h.status_code in (301, 302, 303, 307, 308)
    except Exception:  # noqa: BLE001
        resolves = False
    out = {"msg": msg, "resolves": resolves}
    cache[doi] = out
    cache_f.write_text(json.dumps(cache, indent=1), encoding="utf-8")
    time.sleep(0.6)
    return out


def apa_parts(row, cr: dict | None):
    """Devuelve (autores, ano, titulo, revista, volumen, numero, paginas) para APA 7."""
    msg = (cr or {}).get("msg")
    if msg:
        auths = []
        for a in msg.get("author", []) or []:
            fam, giv = a.get("family"), a.get("given", "")
            ini = " ".join(p[0] + "." for p in re.split(r"[\s\-]+", giv) if p) if giv else ""
            auths.append(f"{fam}, {ini}".strip().rstrip(","))
        year = ((msg.get("issued") or msg.get("published") or {}).get("date-parts") or [[None]])[0][0]
        import html as _html
        clean = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", _html.unescape(re.sub(r"<[^>]+>", "", str(s))))).strip()   # noqa: E731
        title = clean((msg.get("title") or [row.title])[0]).rstrip(".")
        journal = clean((msg.get("container-title") or [row.journal])[0])
        return auths, year or row.year, title, journal, msg.get("volume"), msg.get("issue"), msg.get("page") or msg.get("article-number")
    auths = [re.sub(r"^(\S+)\s+(\S+)$", lambda m: f"{m.group(1)}, {'.'.join(m.group(2))}.", a.strip()) for a in str(row.author_string or "").rstrip(".").split(", ") if a.strip()]
    return auths, row.year, str(row.title).rstrip("."), row.journal, None, None, None


def apa_author_text(auths: list[str]) -> str:
    if not auths:
        return ""
    if len(auths) == 1:
        return auths[0]
    if len(auths) <= 20:
        return ", ".join(auths[:-1]) + ", & " + auths[-1]
    return ", ".join(auths[:19]) + ", ... " + auths[-1]


def add_hyperlink(par, url, text):
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    r_id = par.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), r_id)
    run = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    col = OxmlElement("w:color"); col.set(qn("w:val"), "0563C1"); rpr.append(col)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    run.append(rpr)
    t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve"); run.append(t)
    h.append(run); par._p.append(h)


def build_docx(repo: pd.DataFrame, meta: pd.DataFrame) -> list[str]:
    from docx import Document
    from docx.shared import Pt, Cm
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
    doc.add_heading("Repositorio de artículos curados", level=1)
    doc.add_paragraph("Artículos de acceso abierto con micrografía útil, DLS útil y potencial zeta útil para el mismo nanoportador. Ordenados por nivel y luego por familia. "
                      "Cifras provisionales: validación humana pendiente; solo incluye los artículos procesados hasta ahora.")
    bad = []
    m = meta.set_index("pmcid")
    for tier in ("S", "A", "B"):
        sub = repo[repo.tier == tier].sort_values(["family", "score"], ascending=[True, False])
        if sub.empty:
            continue
        doc.add_heading(f"Nivel {tier}" + {"S": " (≥ 85)", "A": " (70–84)", "B": " (60–69)"}[tier], level=2)
        for fam, g in sub.groupby("family", sort=True):
            doc.add_heading(str(fam), level=3)
            for r in g.itertuples():
                row = m.loc[r.pmcid]
                cr = crossref(row.doi) if isinstance(row.doi, str) else None
                if cr is not None and not cr["resolves"]:
                    bad.append(f"{row.doi} ({r.pmcid})")
                auths, year, title, journal, vol, iss, pages = apa_parts(row, cr)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(1.27); p.paragraph_format.first_line_indent = Cm(-1.27); p.paragraph_format.space_after = Pt(0)
                p.add_run(f"{apa_author_text(auths)} ({year}). {title}. ")
                jr = p.add_run(str(journal)); jr.italic = True
                if vol:
                    p.add_run(", "); vr = p.add_run(str(vol)); vr.italic = True
                    if iss:
                        p.add_run(f"({iss})")
                if pages:
                    p.add_run(f", {pages}")
                p.add_run(". ")
                add_hyperlink(p, f"https://doi.org/{row.doi}", f"https://doi.org/{row.doi}")
                q = doc.add_paragraph()
                q.paragraph_format.left_indent = Cm(1.27); q.paragraph_format.space_after = Pt(8)
                run = q.add_run(f"Nivel {r.tier} · {r.score:.0f} puntos · técnicas útiles: {r.techniques} · licencia: {r.license_color}")
                run.font.size = Pt(10); run.italic = False
    doc.add_heading("DOI que no resuelven", level=2)
    doc.add_paragraph("Ninguno." if not bad else "; ".join(bad))
    try:
        doc.save(CUR / "Repositorio_articulos.docx")
    except PermissionError:
        doc.save(CUR / "Repositorio_articulos_nuevo.docx"); LOCKED.append(("Repositorio_articulos.docx", "Repositorio_articulos_nuevo.docx"))
    return bad


def _reason(g: dict) -> str:
    if not g["research"]:
        return "no es investigacion primaria"
    if not g["object"]:
        return "el nanoportador es una herramienta, no el objeto de estudio"
    if g["viral_pcr"]:
        return "portador viral o caracterizacion dependiente de PCR"
    if not g["micro"]:
        return "sin micrografia util"
    if not g["dls"]:
        return "DLS sin valor numerico con medio declarado" + (" (valor con medio no declarado: dato dudoso)" if g["dls_dudoso"] else "")
    if not g["zeta"]:
        return "zeta sin valor numerico con medio o pH declarado" + (" (valor con medio no declarado: dato dudoso)" if g["zeta_dudoso"] else "")
    return "no pasa la puerta"


def _group(pm: str, man: pd.DataFrame, rounds: dict) -> str:
    return "piloto (azar)" if man.loc[pm, "set"] == "pilot" else rounds.get(pm, "verificación humana (azar y vacíos)")


def singles_table(final: dict, man: pd.DataFrame, meta: pd.DataFrame, rounds: dict) -> pd.DataFrame:
    """Articulos con UNA sola pasada (descartados en la primera prueba: no se gasta una segunda lectura en ellos)."""
    A_all, B_all = merge.load("A"), merge.load("B")
    mm = meta.set_index("pmcid")
    rows = []
    for pm in sorted((set(A_all) | set(B_all)) - set(final)):
        rec = B_all.get(pm) or A_all[pm]
        g = eq.gate(rec)
        has2 = int(g["micro"]) + int(g["dls"] or g["dls_dudoso"]) + int(g["zeta"] or g["zeta_dudoso"])
        rows.append(dict(pmcid=pm, doi=mm.loc[pm, "doi"], title=mm.loc[pm, "title"], family=man.loc[pm, "family"], grupo=_group(pm, man, rounds),
                         stage="una sola pasada (" + ("Sonnet, paquete completo" if pm in B_all else "Haiku, paquete corto") + ")", reason=_reason(g),
                         near=bool(g["research"] and g["object"] and not g["viral_pcr"] and has2 >= 2), dls_dudoso=g["dls_dudoso"], zeta_dudoso=g["zeta_dudoso"],
                         **{k: g[k] for k in ("research", "object", "viral_pcr", "micro", "dls", "zeta")}))
    return pd.DataFrame(rows)


def consumption() -> dict:
    c = pd.read_csv(CUR / "consumption_log.csv")
    c["subagent_tokens"] = pd.to_numeric(c["subagent_tokens"], errors="coerce")
    c = c.dropna(subset=["subagent_tokens"])
    return dict(total=int(c.subagent_tokens.sum()), by_model=c.groupby("model").subagent_tokens.sum().astype(int).to_dict(),
                per_article={m: int(g.subagent_tokens.sum() / g.articles.sum()) for m, g in c.groupby("model") if g.articles.sum()})


def main() -> None:
    final = {}
    for l in open(CUR / "work" / "final.jsonl", encoding="utf-8"):
        r = json.loads(l); final[r["pmcid"]] = r
    sc = pd.read_csv(CUR / "work" / "scored.csv").set_index("pmcid")
    fg = pd.read_csv(CUR / "work" / "final_gate.csv").set_index("pmcid")
    meta = pd.read_csv(CUR / "data" / "article_meta.csv", dtype={"pmcid": str})
    man = pd.read_csv(CUR / "work" / "manifest.csv", dtype={"pmcid": str}).set_index("pmcid")
    ids = list(final)
    rl = pd.read_csv(CUR / "work" / "expand_rounds.csv", dtype={"pmcid": str})
    rounds = dict(zip(rl.pmcid, "ronda " + rl["round"].str[1:]))
    SG = singles_table(final, man, meta, rounds)
    cluster, size, dups, edges, lgroup = lineage.build(ids, final, meta)
    save_csv(dups, "duplicates.csv")
    save_csv(edges, "lineage_edges.csv")
    mm = meta.set_index("pmcid")
    # --- tabla por articulo
    rows = []
    for pm in ids:
        r, s, g = final[pm], sc.loc[pm], fg.loc[pm]
        ctx = r["context"]
        reason = ""
        if not g["research"]:
            reason = "no es investigacion primaria"
        elif not g["object"]:
            reason = "el nanoportador es una herramienta, no el objeto de estudio"
        elif g["viral_pcr"]:
            reason = "portador viral o caracterizacion dependiente de PCR"
        elif g["disputed"]:
            reason = "desacuerdo no resuelto (" + str(g["disputed_why"]) + ")"
        elif not g["micro"]:
            reason = "sin micrografia util"
        elif not g["dls"]:
            reason = "DLS sin valor numerico con medio declarado" + (" (valor con medio no declarado: dato dudoso)" if g["dls_dudoso"] else "")
        elif not g["zeta"]:
            reason = "zeta sin valor numerico con medio o pH declarado" + (" (valor con medio no declarado: dato dudoso)" if g["zeta_dudoso"] else "")
        elif not s["same_sample"]:
            reason = "micrografia y DLS/zeta son de muestras distintas (no hay una muestra con las tres tecnicas)"
        elif s["tier"] == "fuera":
            reason = f"puntuacion {s['score']:.0f} < 60"
        has2 = int(bool(g["micro"])) + int(bool(g["dls"] or g["dls_dudoso"])) + int(bool(g["zeta"] or g["zeta_dudoso"]))
        base_ok = bool(g["research"] and g["object"] and not g["viral_pcr"])
        status = "repositorio" if s["tier"] in ("S", "A", "B") else ("near_miss" if base_ok and has2 >= 2 else "excluido")
        si_flag = any((m.get("shown_as") == "SI_only") or ("valores_solo_en_SI" in (m.get("quality_flags") or [])) for m in r["measurements"])
        rows.append(dict(pmcid=pm, doi=mm.loc[pm, "doi"], title=mm.loc[pm, "title"], journal=mm.loc[pm, "journal"], year=mm.loc[pm, "year"], author_string=mm.loc[pm, "author_string"],
                         license_epmc=mm.loc[pm, "license_epmc"], family=r["family"], carrier_type=ctx.get("carrier_type"), tier=s["tier"], score=s["score"], status=status,
                         reason=reason if status != "repositorio" else "", s_micro=s["s_micro"], s_dls=s["s_dls"], s_zeta=s["s_zeta"], s_link=s["s_link"],
                         s_batches=s["s_batches"], s_complementary=s["s_complementary"], n_formulations=s["n_formulations"], micro_kind=s["micro_kind"],
                         micro_variants=s["micro_variants"], complementary=s["complementary"], lab_cluster_id=cluster[pm], lab_cluster_size=size[pm],
                         lineage_group=lgroup.get(pm, ""), hasSuppl=mm.loc[pm, "hasSuppl"], has_SI_dependence=si_flag, dls_dudoso=bool(g["dls_dudoso"]), zeta_dudoso=bool(g["zeta_dudoso"]),
                         arbitrated=bool(g["arbitrated"]), disputed=bool(g["disputed"]), set=man.loc[pm, "set"], grupo=_group(pm, man, rounds)))
    A = pd.DataFrame(rows)
    # revision manual (auditoria de Claude sobre lo que agregaron los agentes; a confirmar por la revision humana)
    mf = CUR / "manual_review.csv"
    if mf.exists():
        for m in pd.read_csv(mf, dtype={"pmcid": str}).itertuples():
            if m.decision == "excluir" and m.pmcid in set(A.pmcid):
                A.loc[A.pmcid == m.pmcid, ["status", "reason"]] = ["excluido", f"revision manual: {m.reason}"]
    # retractados (marca de Europe PMC): nunca entran al repositorio
    retracted = set(meta[meta.pub_types.fillna("").str.contains("retract", case=False)].pmcid)
    hit = A.pmcid.isin(retracted)
    A.loc[hit, ["status", "reason"]] = ["excluido", "articulo retractado (marca 'Retracted Publication' de Europe PMC)"]
    # duplicados: conservar uno
    drop = {}
    for d in dups.itertuples():
        ra, rb = A[A.pmcid == d.a].iloc[0], A[A.pmcid == d.b].iloc[0]
        if ra.status != "repositorio" or rb.status != "repositorio":
            continue                      # solo compiten por el repositorio los que hoy estan en el
        keep, out = (ra, rb) if (ra.score, str(ra.year)) >= (rb.score, str(rb.year)) else (rb, ra)
        drop[out.pmcid] = f"duplicado de {keep.pmcid}: {d.reason}"
    A["duplicate_of"] = A.pmcid.map(drop).fillna("")
    A.loc[(A.duplicate_of != "") & (A.status == "repositorio"), "status"] = "excluido"
    A.loc[A.duplicate_of != "", "reason"] = A.duplicate_of
    # licencias del repositorio
    repo = A[A.status == "repositorio"].copy()
    lic = license_check(repo)
    A = A.merge(lic[["pmcid", "license_color", "license_publisher", "license_note", "license_checked"]], on="pmcid", how="left")
    def _techs(r):
        if r.status != "repositorio":
            return ""
        comp = list(dict.fromkeys(c.split("(")[0] for c in str(r.complementary).split("|") if c and c != "nan"))
        return "+".join(([r.micro_kind] if r.micro_kind else []) + ["DLS", "zeta"] + comp)
    A["techniques"] = A.apply(_techs, axis=1)
    repo = A[A.status == "repositorio"].copy()
    repo["doi_link"] = [("https://doi.org/" + d) if isinstance(d, str) and d else ("https://pmc.ncbi.nlm.nih.gov/articles/" + p + "/") for d, p in zip(repo.doi, repo.pmcid)]   # sin DOI: enlace de PMC
    cols = ["pmcid", "doi", "doi_link", "title", "journal", "year", "family", "carrier_type", "tier", "score", "s_micro", "s_dls", "s_zeta", "s_link", "s_batches", "s_complementary", "n_formulations",
            "micro_kind", "micro_variants", "complementary", "techniques", "license_epmc", "license_color", "license_note", "lab_cluster_id", "lab_cluster_size", "lineage_group",
            "duplicate_of", "hasSuppl", "has_SI_dependence"]
    save_csv(repo.sort_values(["tier", "family", "score"], ascending=[True, True, False])[cols], "articles_curated.csv")
    nm = pd.concat([A[A.status == "near_miss"][["pmcid", "doi", "title", "family", "score", "reason", "dls_dudoso", "zeta_dudoso", "license_epmc"]],
                    SG[SG.near][["pmcid", "doi", "title", "family", "reason", "dls_dudoso", "zeta_dudoso"]].assign(score=float("nan"), license_epmc="")], ignore_index=True)
    save_csv(nm, "near_miss.csv")
    pre = pd.read_csv(CUR / "data" / "prefilter_excluded.csv", dtype={"pmcid": str})
    ex = pd.concat([pre.rename(columns={"primary_family": "family", "motivo": "reason"})[["pmcid", "family", "title", "reason"]].assign(stage="prefiltro"),
                    A[A.status == "excluido"][["pmcid", "family", "title", "reason"]].assign(stage="extraccion LLM (dos pasadas)"),
                    SG[~SG.near][["pmcid", "family", "title", "reason", "stage"]]], ignore_index=True)
    save_csv(ex, "excluded.csv")
    # pendientes
    cand = pd.read_csv(CUR / "data" / "candidates.csv", dtype={"pmcid": str})
    save_csv(cand[~cand.pmcid.isin(set(A.pmcid) | set(SG.pmcid) | retracted)][["pmcid", "primary_family", "title"]].assign(motivo="candidato aun sin extraccion (no seleccionado por el filtro barato)"), "pending.csv")
    # --- mediciones
    mrows = []
    for pm in ids:
        r = final[pm]; S = {s["id"]: s for s in r["samples"]}
        for m in r["measurements"]:
            mrows.append(dict(pmcid=pm, doi=mm.loc[pm, "doi"], family=r["family"], status=A.set_index("pmcid").loc[pm, "status"], technique=m["technique"], variant=m.get("variant"), measurand=m.get("measurand"),
                              assay_purpose=m.get("assay_purpose"), sample_id=m.get("sample_id"), sample_name=(S.get(m.get("sample_id")) or {}).get("name"), sample_identity=eq.identity_of(m, S),
                              formulation_defined_in=(S.get(m.get("sample_id")) or {}).get("formulation_defined_in"), formulation_link=(m.get("formulation_link") or {}).get("confidence"),
                              link_where=(m.get("formulation_link") or {}).get("where"), shown_as=m.get("shown_as"), values=json.dumps(m.get("values"), ensure_ascii=False),
                              conditions=json.dumps(m.get("conditions"), ensure_ascii=False), n_replicates=m.get("n_replicates"), quality_flags="|".join(m.get("quality_flags") or []),
                              equivalence_group=eq.equivalence_group(m, S), evidence_quote=(m.get("evidence") or {}).get("quote"), evidence_location=(m.get("evidence") or {}).get("location"),
                              evidence_verified=(m.get("evidence") or {}).get("verified"), confidence=m.get("confidence")))
    M = pd.DataFrame(mrows)
    save_csv(M, "measurements.csv")
    grp = M.groupby("equivalence_group").agg(n_measurements=("pmcid", "size"), n_articles=("pmcid", "nunique")).reset_index().sort_values("n_measurements", ascending=False)
    (CUR / "equivalence_groups.yaml").write_text(yaml.safe_dump({"rules": eq.RULES, "n_groups": int(len(grp)),
                                                                  "groups": grp.set_index("equivalence_group").to_dict("index")}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    md = ["# Grupos de equivalencia", "", "Regla: dos mediciones son del mismo grupo solo si coinciden en tecnica, variante, magnitud, identidad de la muestra y en las condiciones que cambian su interpretacion; "
          "una condicion no declarada (`nd`) **separa** el grupo. Si hay duda, se separa.", ""] + [f"- **{k}**: {v}" for k, v in eq.RULES.items()]
    md += ["", f"Grupos observados: {len(grp)}. Los 25 mayores:", "", "| Grupo | Mediciones | Articulos |", "|---|---|---|"]
    md += [f"| `{r.equivalence_group}` | {r.n_measurements} | {r.n_articles} |" for r in grp.head(25).itertuples()]
    (CUR / "equivalence_groups.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    # lab clusters
    save_csv(A[["pmcid", "lab_cluster_id", "lab_cluster_size", "lineage_group", "family", "status"]].sort_values("lab_cluster_id"), "lab_clusters.csv")
    bad = build_docx(repo, meta)
    make_charts(A, repo, SG)
    write_report(A, repo, M, bad, man, final, SG)
    print(A.status.value_counts().to_dict(), "| DOI que no resuelven:", len(bad))


def _universe(A: pd.DataFrame, SG: pd.DataFrame) -> pd.DataFrame:
    """Todos los articulos con extraccion LLM (dos pasadas o una sola) y sus campos de puerta."""
    fg = pd.read_csv(CUR / "work" / "final_gate.csv").set_index("pmcid").loc[A.pmcid].reset_index()
    fg["grupo"] = A.grupo.values
    fg["repo"] = (A.status == "repositorio").values
    fg["disputed"] = fg["disputed"].astype(bool)
    s = SG.assign(disputed=False, repo=False)
    cols = ["pmcid", "grupo", "research", "object", "viral_pcr", "micro", "dls", "zeta", "disputed", "repo"]
    return pd.concat([fg[cols], s[cols]], ignore_index=True)


def make_charts(A: pd.DataFrame, repo: pd.DataFrame, SG: pd.DataFrame) -> None:
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "DejaVu Sans"], "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})
    U = _universe(A, SG)
    n = len(U)
    base = U.research & U.object & ~U.viral_pcr
    s_micro = int((base & U.micro).sum()); s_dls = int((base & U.micro & U.dls).sum()); s_gate = int((base & U.micro & U.dls & U.zeta & ~U.disputed).sum())
    stages = [("Con extracción LLM", n), ("Con micrografía útil", s_micro), ("… y DLS útil (valor + medio)", s_dls), ("… y zeta útil: pasan la puerta", s_gate),
              ("En el repositorio (≥ 60 puntos, tras auditoría)", len(repo))]
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.barh(range(len(stages)), [s[1] for s in stages], color=[BLUE, BLUE, BLUE, GREEN, GREEN], height=.62)
    for i, (_, v) in enumerate(stages):
        ax.text(v + n * .012, i, f"{v}  ({100 * v / n:.0f} %)", va="center", fontsize=11, color=INK)
    ax.set_yticks(range(len(stages))); ax.set_yticklabels([s[0] for s in stages], fontsize=10.5)
    ax.invert_yaxis(); ax.set_xlim(0, n * 1.22)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0); ax.set_xlabel(f"Artículos con extracción LLM (de 766 candidatos tras el prefiltro)")
    fig.suptitle(f"De {n} artículos extraídos, {len(repo)} llegan al repositorio; el DLS con medio declarado es el filtro que más descarta", x=0.02, ha="left", fontsize=11.5)
    fig.tight_layout(rect=(0, 0, 1, .93)); fig.savefig(CUR / "grafico_embudo.png", dpi=170); plt.close(fig)
    t = A[A.tier.isin(["S", "A", "B"]) & (A.status == "repositorio")].groupby(["family", "tier"]).size().unstack(fill_value=0).reindex(columns=["S", "A", "B"], fill_value=0)
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    left = None
    for tier, col in (("S", GREEN), ("A", BLUE), ("B", YELLOW)):
        ax.barh(t.index, t[tier], left=left if left is not None else 0, color=col, label=f"Nivel {tier}", height=.6)
        left = t[tier] if left is None else left + t[tier]
    ax.legend(frameon=False, loc="lower right"); ax.invert_yaxis()
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0); ax.set_xlabel("Artículos en el repositorio")
    fig.suptitle(f"Niveles por familia ({len(repo)} artículos)", x=0.02, ha="left", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, .93)); fig.savefig(CUR / "grafico_niveles_por_familia.png", dpi=170); plt.close(fig)
    g = U.groupby("grupo").agg(n=("pmcid", "size"), repo=("repo", "sum"))
    order = [x for x in ("piloto (azar)", "ronda 1", "ronda 2", "verificación humana (azar y vacíos)") if x in g.index]
    g = g.loc[order]
    fig, ax = plt.subplots(figsize=(8.5, 3.4))
    y = range(len(g))
    ax.barh(y, g.n, color="#d9dde5", height=.6, label="Extraídos")
    ax.barh(y, g.repo, color=GREEN, height=.6, label="En el repositorio")
    for i, r in enumerate(g.itertuples()):
        ax.text(r.n + .8, i, f"{int(r.repo)} de {int(r.n)}  ({100 * r.repo / r.n:.0f} %)", va="center", fontsize=11, color=INK)
    ax.set_yticks(list(y)); ax.set_yticklabels(g.index, fontsize=11); ax.invert_yaxis(); ax.set_xlim(0, g.n.max() * 1.35)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0); ax.legend(frameon=False, loc="lower right", fontsize=9)
    fig.suptitle("Rendimiento: elegir antes con el filtro barato duplica el porcentaje que llega al repositorio", x=0.02, ha="left", fontsize=11.5)
    fig.tight_layout(rect=(0, 0, 1, .92)); fig.savefig(CUR / "grafico_rendimiento_por_ronda.png", dpi=170); plt.close(fig)


def write_report(A, repo, M, bad, man, final, SG) -> None:
    U = _universe(A, SG)
    n = len(U)
    f = pd.read_csv(CUR / "data" / "funnel.csv").set_index("step")["quedan"]
    cand = int(f["candidatos para extraccion con LLM"])
    base = U.research & U.object & ~U.viral_pcr
    gate_n = int((base & U.micro & U.dls & U.zeta & ~U.disputed).sum())
    tiers = repo.tier.value_counts().reindex(["S", "A", "B"], fill_value=0)
    fam_tab = repo.groupby("family").size().to_dict()
    mk = repo.micro_kind.value_counts().to_dict()
    kinds = Counter()
    for pm in repo.pmcid:
        for m in final[pm]["measurements"]:
            if m["technique"] == "micrograph" and m.get("variant") in eq.MICRO_VARIANTS:
                kinds[m["variant"]] += 1
    combos = Counter(repo.techniques)
    lic = repo.license_color.value_counts().to_dict()
    sev = {k: int(v) for k, v in repo.groupby("n_formulations").size().to_dict().items()}
    saxs_all = int(((M.technique == "SAXS")).sum()); saxs_repo = int(((M.technique == "SAXS") & (M.status == "repositorio")).sum())
    saxs_art = int(M[(M.technique == "SAXS") & (M.status == "repositorio")].pmcid.nunique())
    si_any = int(A.has_SI_dependence.sum())
    allx = pd.concat([A[A.status != "repositorio"][["reason"]], SG[["reason"]]])
    reasons = allx.reason.fillna("").str.replace(r"\s*\(.*\)", "", regex=True).value_counts().head(7)
    grp = U.groupby("grupo").agg(n=("pmcid", "size"), repo=("repo", "sum"))
    pct = lambda a, b: f"{100 * a / b:.0f} %" if b else "n.d."   # noqa: E731
    cons = consumption()
    n_manual = len(pd.read_csv(CUR / "manual_review.csv")) if (CUR / "manual_review.csv").exists() else 0
    n_single = len(SG)
    sem = pct(mk.get("SEM", 0), len(repo))
    yield_rows = "".join(f"| {k} | {int(v.n)} | {int(v.repo)} | {pct(v.repo, v.n)} |\n" for k, v in grp.iterrows())
    L = ["# Informe de curación de calidad (fase 2) — PROVISIONAL", "",
         f"> **Alcance de estas cifras:** {n} de los {cand} candidatos leídos con modelos (100 al azar como piloto y {n - 100} elegidos con un filtro barato por código), "
         f"{len(repo)} artículos en el repositorio. La validación humana (Bryan y Carlos) **no está hecha**: todas las métricas son provisionales.", "", "## 1. Embudo", "",
         f"- Procesados antes: 2.396 → sin AAV/virus/fuera de alcance → **{cand} candidatos** con señal de micrografía + DLS + zeta (prefiltro, `data/funnel.csv`).",
         f"- Con extracción LLM: **{n}**. Pasan la puerta estricta: **{gate_n}**. En el repositorio (≥ 60 puntos y auditoría): **{len(repo)}**. "
         f"{n_single} artículos se descartaron tras una sola lectura (no se gasta una segunda en ellos).",
         "- Principales motivos de salida: " + "; ".join(f"{k} ({v})" for k, v in reasons.items()) + ".", "",
         "![Embudo](grafico_embudo.png)", "", "### Rendimiento por grupo", "", "| Grupo | Extraídos | En el repositorio | % |", "|---|---|---|---|", yield_rows.rstrip(),
         "", "El piloto se eligió al azar; las rondas 1 y 2 se eligieron con un filtro por código (tabla con tamaño y zeta, y medio declarado junto a DLS y zeta), por eso rinden más. "
         "No son comparables como una tasa de la población: la tasa del azar (piloto) es la que describe a los 766 candidatos.", "",
         "![Rendimiento](grafico_rendimiento_por_ronda.png)", "", "## 2. Niveles y familias", "",
         f"Niveles: S {tiers['S']}, A {tiers['A']}, B {tiers['B']}. Por familia: " + ", ".join(f"{k} {v}" for k, v in sorted(fam_tab.items())) + ".",
         f"Micrografía del repositorio: {', '.join(f'{k} {v}' for k, v in mk.items())} artículos (proporción SEM {sem}); variantes registradas: "
         + ", ".join(f"{k} {v}" for k, v in kinds.most_common()) + ".", "",
         "![Niveles](grafico_niveles_por_familia.png)", "",
         "## 3. Técnicas, lotes y licencias", "",
         "- Combinaciones de técnicas útiles (repositorio): " + "; ".join(f"`{k}` ×{v}" for k, v in combos.most_common(6)) + ".",
         "- Cobertura de lotes (formulaciones con DLS o zeta medidos por artículo): " + ", ".join(f"{k}: {v}" for k, v in sorted(sev.items())) + " (clave: nº de formulaciones: artículos).",
         "- Licencia (verificada contra Europe PMC, XML del artículo y página del editor cuando fue accesible): " + ", ".join(f"{k} {v}" for k, v in lic.items()) + ". "
         "Solo `verde` permite redistribuir figuras.",
         f"- DOI que no resuelven: {len(bad)}.", "",
         "## 4. Pistas secundarias y expansión", "",
         f"- **SAXS:** {saxs_all} mediciones de SAXS entre los artículos extraídos; {saxs_repo} en {saxs_art} artículos del repositorio: **sigue sin haber muestra para evaluar un subconjunto de calidad**; "
         "con la prevalencia observada en el análisis previo (≈ 1 % de los artículos) se necesita una búsqueda dirigida de SAXS (no iniciada).",
         "- **Inorgánicas:** el repositorio tiene " + str(fam_tab.get("inorganic", 0)) + " artículos de esta familia. Es el vacío más claro; se necesita una búsqueda dirigida (no iniciada).",
         "- **Expansión dirigida (paso 7):** no iniciada. Las rondas 1 y 2 salieron de los artículos ya descargados; no se buscaron artículos nuevos.", "",
         "## 5. Efecto del material suplementario", "",
         f"- Europe PMC marca material suplementario en el {pct(int((pd.read_csv(CUR / 'data' / 'article_meta.csv').hasSuppl == 'Y').sum()), 778)} de los candidatos. El texto completo de Europe PMC **no incluye** ese material.",
         f"- {si_any} de {len(A)} artículos con dos pasadas ({pct(si_any, len(A))}) tienen mediciones cuyos valores solo están en el suplemento o en figuras sin cifras: se marcan `valores_solo_en_SI` y **no cumplen la puerta**. "
         "No se descargó el suplemento; es una limitación clave y subestima el repositorio.", "",
         "## 6. Cómo se trabajó y qué costó", "",
         "- Filtro barato por código (0 tokens): tabla con tamaño y zeta, y medio declarado junto a DLS y zeta. En el piloto, ese criterio dejaba pasar a 19 de 23 artículos que luego aprobaron la puerta (83 %).",
         "- Ronda 1: Haiku sobre un paquete corto (solo frases clave, pies de figura y tablas), luego Sonnet sobre el paquete completo en los que pasaban o casi. "
         "Haiku descartó por error a 8 de los 23 que Sonnet aprobó (recall 65 %), así que la ronda 2 fue directo a Sonnet y Haiku se usó como segunda lectura de los aprobados.",
         f"- Tokens de subagentes: {cons['total'] / 1e6:.1f} millones en total ({', '.join(f'{k} {v / 1e6:.1f} M' for k, v in cons['by_model'].items())}). "
         f"Por artículo leído: " + ", ".join(f"{k} ≈ {v // 1000} mil" for k, v in cons['per_article'].items()) + ".",
         f"- Auditoría de Claude sobre lo que agregaron los agentes: {n_manual} artículos excluidos a mano (`manual_review.csv`; Bryan y Carlos pueden revertirlos) y una regla nueva por código: "
         "la micrografía, el DLS y el zeta deben ser de una misma muestra.", "",
         "## 7. Limitaciones y qué falta validar", "",
         "- Falta la revisión humana de los 60 artículos (`hoja_revision_humana.csv`) y con ella los umbrales de precisión de la puerta (≥ 0,95), kappa de variante/grupo (≥ 0,80) y licencia (100 %). "
         "Mi auditoría no es independiente de los modelos.",
         "- Las rondas 1 y 2 usaron una pasada sobre un extracto corto (Haiku) o una sola pasada completa (Sonnet) según el caso, y arbitraje solo de la puerta y los valores; los grupos de equivalencia salen de la pasada de Sonnet.",
         "- Dos pasadas con modelos de la misma familia comparten sesgos; el arbitraje usó Sonnet (no un modelo más fuerte).",
         "- Solo se procesaron los artículos ya descargados (2.396).",
         "- Los DOI se comprobaron con la respuesta de `doi.org` (redirección), no con la página final del editor."]
    (CUR / "INFORME.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
