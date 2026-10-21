"""Conjunto AMPLIADO para imagenes: regla flexible = minimo micrografia + algun descriptor nanometrico o espectro (FTIR, XRD, UV-Vis, SAXS, EDS/EDX, Raman).

Embudo (solo la etapa 3 gasta tokens):
  1. rank    (gratis)  titulo + resumen de los CC BY del universo: tema (nanoportador) + micrografia + descriptor/espectro -> work/ext/rank.csv
  2. fetch   (red)     descarga el texto completo de los N mejores (Europe PMC, <= 3 peticiones/s, reanudable)
  3. screen  (gratis)  sobre el texto completo: pie de figura con micrografia + (tamano/zeta/PDI numerico o espectro) -> work/ext/screen.csv
  4. Haiku             lee solo un paquete corto de evidencia (pies de figura y frases clave), no el articulo entero

  python -m curation.extended rank [N]      python -m curation.extended fetch [N]      python -m curation.extended screen
"""
from __future__ import annotations

import re
import sys

import pandas as pd

from src.common import CACHE, DATA, ROOT
from src.fulltext import FT_DIR, fetch_many
from curation import cheap_filter as cf, textprep

CUR = ROOT / "curation"
EXT = CUR / "work" / "ext"

CARRIER = re.compile(r"deliver|nanocarrier|\bcarriers?\b|encapsulat|entrap|\bloaded\b|\bloading\b|formulat|liposom|niosom|ethosom|transfersom|bilosom|cubosom|hexosom|micelle|nanogel|dendrimer|"
                     r"nanoemulsion|lipid nanoparticle|\bLNPs?\b|\bSLNs?\b|\bNLCs?\b|PLGA|chitosan|mesoporous silica|siRNA|mRNA|vaccine|controlled release|sustained release|bioavailab|"
                     r"targeted therapy|\bdrug\b|therapeutic", re.I)
NEG = re.compile(r"catalys|photocatal|biosensor|\bsensor\b|electrochem|batter|supercapacitor|wastewater|dye degradation|pollut|solar cell|corrosion|water treatment", re.I)
MICRO_A = re.compile(r"\bTEM\b|\bSEM\b|\bSTEM\b|transmission electron|scanning electron|cryo-?\s?(?:TEM|EM|electron)|micrograph|electron microscop|morpholog", re.I)
DESC_A = re.compile(r"particle size|\bPDI\b|polydispers|zeta|\bDLS\b|dynamic light|hydrodynamic|mean (?:size|diameter)|\bnm\b", re.I)
SPEC_A = re.compile(r"\bFTIR\b|FT-IR|infrared|\bXRD\b|X-ray diffraction|UV[- ]?Vis|absorption spectr|\bSAXS\b|small[- ]angle|\bEDS\b|\bEDX\b|energy[- ]dispersive|\bRaman\b|\bSERS\b", re.I)
SPEC_CAP = re.compile(r"\bFTIR\b|FT-IR|infrared|\bXRD\b|X-ray diffraction|diffractogram|UV[- ]?Vis|absorption spectr|\bSAXS\b|small[- ]angle|\bEDS\b|\bEDX\b|energy[- ]dispersive|\bRaman\b|\bSERS\b|\bspectr(?:um|a)\b", re.I)
SPEC_TYPES = {"FTIR": re.compile(r"\bFTIR\b|FT-IR|infrared", re.I), "XRD": re.compile(r"\bXRD\b|X-ray diffraction|diffractogram", re.I), "UVVis": re.compile(r"UV[- ]?Vis|absorption spectr", re.I),
              "SAXS": re.compile(r"\bSAXS\b|small[- ]angle", re.I), "EDS": re.compile(r"\bEDS\b|\bEDX\b|energy[- ]dispersive", re.I), "Raman": re.compile(r"\bRaman\b|\bSERS\b", re.I)}


def rank(top: int = 4000) -> None:
    EXT.mkdir(parents=True, exist_ok=True)
    u = pd.read_csv(DATA / "ids" / "universe.csv", dtype=str, low_memory=False)
    ab = pd.read_csv(CACHE / "abstracts.csv", dtype=str)
    u = u.merge(ab, on="pmcid", how="left")
    meta = pd.read_csv(CUR / "data" / "article_meta.csv", dtype=str)
    retr = set(meta[meta.pub_types.fillna("").str.contains("retract", case=False)].pmcid)
    u = u[u.license.str.lower().isin(["cc by", "cc0"]) & (u.primary_family != "AAV") & ~u.pmcid.isin(retr)
          & ~u.pub_types.fillna("").str.contains("review|retract", case=False) & (u.year.astype(float) >= 2016)].copy()
    txt = (u.title.fillna("") + " . " + u.abstract.fillna(""))
    u["carrier"] = txt.str.count(CARRIER) > 0
    u["neg"] = txt.str.count(NEG) > 0
    u["micro_a"] = txt.str.count(MICRO_A) > 0
    u["desc_a"] = txt.str.count(DESC_A) > 0
    u["spec_a"] = txt.str.count(SPEC_A) > 0
    u["score"] = 3 * u.micro_a + 2 * u.desc_a + 3 * u.spec_a + u.carrier - 2 * u.neg
    ok = u[u.carrier & u.micro_a & (u.desc_a | u.spec_a) & ~(u.neg & ~u.carrier)].copy()
    downloaded = set(p.stem for p in FT_DIR.glob("*.xml"))
    ok["descargado"] = ok.pmcid.isin(downloaded)
    ok = ok.sort_values(["score", "year"], ascending=False)
    sel = pd.concat([ok[ok.descargado], ok[~ok.descargado].head(top)])
    sel[["pmcid", "doi", "title", "year", "primary_family", "license", "score", "micro_a", "desc_a", "spec_a", "descargado"]].to_csv(EXT / "rank.csv", index=False)
    print(f"CC BY en el universo (sin AAV, sin revisiones, desde 2016): {len(u)}")
    print(f"pasan el filtro de titulo+resumen (tema + micrografia + descriptor/espectro): {len(ok)} | ya descargados: {int(ok.descargado.sum())} | por descargar (top {top}): {min(top, int((~ok.descargado).sum()))}")
    print("con espectro en el resumen:", int(ok.spec_a.sum()), "| por familia:", ok.primary_family.value_counts().to_dict())


def fetch(n: int | None = None) -> None:
    r = pd.read_csv(EXT / "rank.csv", dtype=str)
    todo = r[r.descargado == "False"].pmcid.tolist()
    if n:
        todo = todo[:n]
    print(f"descargando {len(todo)} textos completos (reanudable)...", flush=True)
    for i in range(0, len(todo), 200):
        res = fetch_many(todo[i:i + 200], workers=3)
        ok = sum(1 for v in res.values() if v in ("ok", "cached"))
        print(f"  {min(i + 200, len(todo))}/{len(todo)}: {ok} ok", flush=True)


def screen() -> None:
    """Incremental: solo revisa los textos descargados que aun no estan en screen.csv y agrega las filas nuevas."""
    r = pd.read_csv(EXT / "rank.csv", dtype=str)
    prev = pd.read_csv(EXT / "screen.csv", dtype=str, low_memory=False) if (EXT / "screen.csv").exists() else pd.DataFrame()
    seen = set(prev.pmcid) if len(prev) else set()
    rows = []
    for p in r.pmcid:
        if p in seen or not (FT_DIR / f"{p}.xml").exists():
            continue
        try:
            f = cf.features(p)
            d = textprep.article_text(p)
            caps = [c for _, c in d["figures"]]
            spec_caps = [c for c in caps if SPEC_CAP.search(c)]
            types = sorted({k for k, rx in SPEC_TYPES.items() if any(rx.search(c) for c in caps)})
            meth = " ".join(t for _, t in d["methods"])
            mtypes = sorted({k for k, rx in SPEC_TYPES.items() if rx.search(meth)})
            f.update(spec_cap=len(spec_caps), spec_types_fig="|".join(types), spec_types_methods="|".join(mtypes))
        except Exception as exc:  # noqa: BLE001
            f = dict(pmcid=p, error=str(exc)[:80])
        rows.append(f)
    s = pd.DataFrame(rows)
    if s.empty:
        print("no hay textos nuevos para revisar")
        return
    s["desc"] =((s.dls_val_sent.fillna(0) > 0) | (s.zeta_val_sent.fillna(0) > 0) | s.size_table.fillna(False).astype(bool) | s.zeta_table.fillna(False).astype(bool))
    s["micro"] = s.micro_cap.fillna(0) > 0
    s["spec"] = s.spec_types_fig.fillna("").ne("") | s.spec_types_methods.fillna("").ne("")     # solo FTIR, XRD, UV-Vis, SAXS, EDS/EDX
    s["tier"] = "no"
    s.loc[s.micro & (s.desc | s.spec), "tier"] = "E2"
    s.loc[s.micro & s.desc & s.spec_types_fig.fillna("").ne(""), "tier"] = "E1"
    s = s.merge(r[["pmcid", "doi", "title", "year", "primary_family", "license"]], on="pmcid", how="left")
    new_n = len(s)
    s = pd.concat([prev, s], ignore_index=True) if len(prev) else s
    s.to_csv(EXT / "screen.csv", index=False)
    print(f"{new_n} textos nuevos | acumulado {len(s)} | E1 (micrografia + descriptor + espectro en figura): {int((s.tier == 'E1').sum())} | E2 (micrografia + descriptor o espectro): {int((s.tier == 'E2').sum())} | no: {int((s.tier == 'no').sum())}")
    print(s[s.tier != "no"].groupby(["primary_family", "tier"]).size().unstack(fill_value=0))


# ----------------------------------------------------------------------------- etapa 3: paquete de evidencia para Haiku
ABS = r"C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence\curation"
XLINK = "http://www.w3.org/1999/xlink"


def fig_graphics(pmcid: str) -> dict:
    """Etiqueta de figura -> archivo de imagen (href del JATS). Sirve para que la descarga de paneles sepa que archivo bajar."""
    from lxml import etree
    root = etree.fromstring((FT_DIR / f"{pmcid}.xml").read_bytes(), parser=etree.XMLParser(recover=True, huge_tree=True, resolve_entities=False, no_network=True))
    out = {}
    for fig in root.xpath(".//fig[not(ancestor::ref-list)]"):
        lab = fig.find("label")
        href = fig.xpath(".//graphic/@xlink:href", namespaces={"xlink": XLINK})
        if lab is not None and href:
            out["".join(lab.itertext()).strip()] = href[0]
    return out


def _fignum(label: str) -> str:
    m = re.search(r"(\d+)", label or "")
    return m.group(1) if m else (label or "").strip().lower()


def evidence_packet(pmcid: str) -> str:
    d = textprep.article_text(pmcid)
    L = [f"PMCID: {pmcid}", f"TITLE: {d['title']}", f"ABSTRACT: {d['abstract'][:700]}", "", "=== FIGURE CAPTIONS (microscopy and spectra) ==="]
    k = 0
    for lab, cap in d["figures"]:
        if (cf.MICRO_T.search(cap) or SPEC_CAP.search(cap)) and k < 12:
            L.append(f"[{lab}] {cap[:650]}")
            k += 1
    L += ["", "=== KEY SENTENCES (size, PDI, zeta, microscopy, spectra) ==="]
    seen, used = set(), 0
    for origin, p in [("M", p) for _, p in d["methods"]] + [("R", p) for _, p in d["results"]]:
        for s in cf.SENT.split(p or ""):
            if (cf.DLS_T.search(s) or cf.ZETA_T.search(s) or cf.MICRO_T.search(s) or cf.COMP_T.search(s)) and s not in seen and used < 3600:
                s2 = s.strip()[:320]
                seen.add(s)
                L.append(f"[{origin}] {s2}")
                used += len(s2)
    L += ["", "=== TABLES (size / zeta) ==="]
    t = 0
    for lab, cap, rows, foot in d["tables"]:
        head = (cap + " " + (rows[0] if rows else "")).lower()
        if re.search(r"size|diameter|\bpdi\b|zeta|\bmv\b|\bnm\b", head):
            block = f"[{lab}] {cap[:200]}\n" + "\n".join(rows[:22])
            if t + len(block) < 2800:
                L.append(block)
                t += len(block)
    return "\n".join(L)


def _assign(tiers, n_batches: int, per_batch: int) -> list[tuple[str, list[str]]]:
    """Asigna articulos nuevos a lotes con numeracion global (EX001, EX002...). Una sola fuente de verdad: work/ext/exportados.csv.
    Prioridad: mas tipos de espectro en figura primero y familias alternadas (para no llenar todo de inorganicas)."""
    log = EXT / "exportados.csv"
    prev = pd.read_csv(log, dtype=str) if log.exists() else pd.DataFrame(columns=["pmcid", "batch"])
    s = pd.read_csv(EXT / "screen.csv", dtype=str, low_memory=False)
    s = s[s.tier.isin(tiers) & ~s.pmcid.isin(set(prev.pmcid))].copy()
    s["n_spec"] = s.spec_types_fig.fillna("").map(lambda x: len([t for t in x.split("|") if t]))
    s = s.sort_values("n_spec", ascending=False)
    queues = {f: list(g.pmcid) for f, g in s.groupby("primary_family")}
    order = []
    while any(queues.values()) and len(order) < n_batches * per_batch:
        for f in sorted(queues, key=lambda k: -len(queues[k])):
            if queues[f]:
                order.append(queues[f].pop(0))
    order = order[:n_batches * per_batch]
    last = max([int(b[2:]) for b in prev.batch] or [0])
    new = []
    for i in range(0, len(order), per_batch):
        new.append((f"EX{last + i // per_batch + 1:03d}", order[i:i + per_batch]))
    rows = [dict(pmcid=p, batch=b) for b, ids in new for p in ids]
    pd.concat([prev, pd.DataFrame(rows)], ignore_index=True).to_csv(log, index=False)
    return new


def materialize_local() -> int:
    """Escribe paquetes (work/ext/packets) y lotes con rutas (work/ext/batches) para todo lote asignado que aun no los tenga."""
    import json
    log = EXT / "exportados.csv"
    if not log.exists():
        return 0
    prev = pd.read_csv(log, dtype=str)
    (EXT / "packets").mkdir(parents=True, exist_ok=True)
    (EXT / "batches").mkdir(parents=True, exist_ok=True)
    (CUR / "work" / "llm" / "E").mkdir(parents=True, exist_ok=True)
    n = 0
    for bid, g in prev.groupby("batch"):
        f = EXT / "batches" / f"{bid}.json"
        if f.exists():
            continue
        ids = g.pmcid.tolist()
        for p in ids:
            if not (EXT / "packets" / f"{p}.txt").exists():
                (EXT / "packets" / f"{p}.txt").write_text(evidence_packet(p), encoding="utf-8")
        f.write_text(json.dumps({"batch": bid, "output": f"{ABS}\\work\\llm\\E\\{bid}.json",
                                 "articles": [{"pmcid": p, "packet": f"{ABS}\\work\\ext\\packets\\{p}.txt"} for p in ids]}, indent=1), encoding="utf-8")
        n += 1
    return n


def packets(tiers=("E1",), per_batch: int = 10, limit: int | None = None) -> None:
    """Crea paquetes y lotes (con rutas) para los articulos revisados por codigo que aun no tienen lote. `limit` = maximo de articulos nuevos."""
    new = _assign(tiers, n_batches=(-(-limit // per_batch) if limit else 10_000), per_batch=per_batch)
    n = materialize_local()
    tot = sum(len(ids) for _, ids in new)
    print(f"{tot} articulos nuevos asignados en {len(new)} lotes; {n} lotes escritos en work/ext/batches (con sus paquetes en work/ext/packets)")


# ----------------------------------------------------------------------------- entrega autocontenida (para un extractor sin acceso a archivos)
def export(tiers=("E1",), n_batches: int = 10, per_batch: int = 10) -> None:
    """Lotes AUTOCONTENIDOS (el texto del paquete va dentro del JSON) en work/ext/entrega/, mas un zip con esquema e instrucciones.
    Usa la misma numeracion que `packets`: un lote EX### tiene los mismos articulos en los dos formatos."""
    import json
    import zipfile
    out = EXT / "entrega"
    out.mkdir(parents=True, exist_ok=True)
    new = _assign(tiers, n_batches, per_batch)
    materialize_local()
    files = []
    for bid, ids in new:
        f = out / f"{bid}.json"
        f.write_text(json.dumps({"batch": bid, "articles": [{"pmcid": p, "packet": evidence_packet(p)} for p in ids]}, ensure_ascii=False, indent=1), encoding="utf-8")
        files.append(f)
    if not files:
        print("no hay articulos nuevos para exportar")
        return
    readme = ("# Entrega de lotes\n\nCada archivo `EX###.json` trae 10 articulos con su paquete de evidencia (el texto va dentro). Para cada lote:\n"
              "1. Lee los 10 paquetes.\n2. Extrae segun `extended_schema.md` (el esquema y las reglas estan ahi; manda ese archivo).\n"
              "3. Devuelve **un solo JSON** `{\"batch\": \"EX###\", \"articles\": [...]}` con un registro por articulo, en el mismo orden, y nombralo `EX###.json`.\n"
              "No necesitas acceso a archivos: todo el texto que necesitas esta dentro de cada lote.\n")
    z = out / f"ENTREGA_{files[0].stem[2:]}-{files[-1].stem[2:]}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(CUR / "prompts" / "extended_schema.md", "extended_schema.md")
        zf.writestr("LEEME_ENTREGA.md", readme)
        for f in files:
            zf.write(f, f.name)
    print(f"{sum(len(i) for _, i in new)} articulos en {len(files)} lotes -> {z}  ({z.stat().st_size // 1024} KB)")


# ----------------------------------------------------------------------------- verificacion de lo que entrega el extractor
MICRO_OK = {"TEM_negstain", "TEM_posstain", "TEM_dried_unstained", "TEM_prep_not_declared", "cryoTEM", "SEM", "STEM", "HRTEM"}
SPEC_OK = {"FTIR", "XRD", "UVVis", "SAXS", "EDS", "Raman"}


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _qfound(q: str, pm: str):
    """Cita verificable. Para citas de 3 palabras o mas: coincidencia aproximada (>= 90). Para etiquetas cortas de subfigura («XRD (B)», «EDX spectrum»):
    solo si aparecen tal cual en el articulo (subcadena exacta tras normalizar), asi una etiqueta corta no pasa por azar de la busqueda aproximada."""
    q = (q or "").strip()
    if len(q.split()) >= 3:
        return textprep.quote_found(q, pm)
    nq = textprep.norm(q)
    return (bool(nq) and len(nq) >= 3 and nq in textprep._norm_full(pm)), 100 if nq else 0


def apply() -> None:
    """Lee work/llm/E/*.json, verifica cada cita contra el texto del articulo (rapidfuzz >= 90) y escribe las tablas ext_*.csv.
    Una fila cuya cita no aparece en el articulo se descarta. La categoria (E1/E2) la calcula este codigo, no el extractor."""
    import json
    rk = pd.read_csv(EXT / "rank.csv", dtype=str).drop_duplicates("pmcid").set_index("pmcid")
    arts, pans, descs, specs = [], [], [], []
    bad_total = 0
    for f in sorted((CUR / "work" / "llm" / "E").glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            print("archivo invalido:", f.name, str(exc)[:80])
            continue
        for rec in d.get("articles", []):
            pm = rec.get("pmcid")
            if pm not in rk.index or not (FT_DIR / f"{pm}.xml").exists():
                continue
            ctx = rec.get("context") or {}
            try:
                gfx = {_fignum(k): v for k, v in fig_graphics(pm).items()}
            except Exception:  # noqa: BLE001
                gfx = {}
            bad = 0
            full_nums = {abs(float(x.replace("−", "-").replace(",", "."))) for x in re.findall(r"\d+(?:[.,]\d+)?", textprep.full_text(pm))}
            unverified = 0
            doi = rk.loc[pm, "doi"]
            link = ("https://doi.org/" + doi) if isinstance(doi, str) and doi else f"https://pmc.ncbi.nlm.nih.gov/articles/{pm}/"
            P, D, S = [], [], []
            for x in rec.get("panels") or []:
                ok, _ = _qfound(x.get("quote") or "", pm)
                if not ok:
                    bad += 1
                    continue
                if x.get("variant") in MICRO_OK and x.get("shows_nanocarrier") is True:
                    P.append(dict(pmcid=pm, doi_link=link, fig=x.get("fig"), variant=x.get("variant"), sample=x.get("sample"), scale_bar_in_caption=(True if x.get("scale_bar_in_caption") is True else None),
                                  image_file=gfx.get(_fignum(x.get("fig") or "")), quote=(x.get("quote") or "")[:200]))
            for x in rec.get("descriptors") or []:
                ok, _ = _qfound(x.get("quote") or "", pm)
                if not ok:
                    bad += 1
                    continue
                vals = {}
                for k in ("size_nm", "pdi", "zeta_mV"):
                    v = _f(x.get(k))
                    if v is not None and abs(v) not in full_nums:      # el numero no aparece en ningun lugar del articulo: se anula
                        unverified += 1
                        v = None
                    vals[k] = v
                if any(v is not None for v in vals.values()):
                    D.append(dict(pmcid=pm, doi_link=link, sample=x.get("sample"), **vals, medium=x.get("medium"), source=x.get("source"), quote=(x.get("quote") or "")[:200]))
            for x in rec.get("spectra") or []:
                ok, _ = _qfound(x.get("quote") or "", pm)
                if not ok:
                    bad += 1
                    continue
                if x.get("technique") in SPEC_OK:
                    S.append(dict(pmcid=pm, doi_link=link, technique=x.get("technique"), fig=x.get("fig"), applies_to=x.get("applies_to"), sample=x.get("sample"), quote=(x.get("quote") or "")[:200]))
            bad_total += bad
            pert = (ctx.get("article_kind") == "research" and ctx.get("nanocarrier_is_object_of_study") is True and ctx.get("carrier_type") != "not_a_nanocarrier"
                    and not ctx.get("virus_or_pcr"))
            spec_np = [s for s in S if s["applies_to"] in ("nanoparticle", "mixture")]
            tier = "no"
            if pert and P and D and spec_np:
                tier = "E1"
            elif pert and P and (D or spec_np):
                tier = "E2"
            arts.append(dict(pmcid=pm, doi=doi, doi_link=link, title=rk.loc[pm, "title"], year=rk.loc[pm, "year"], family=rk.loc[pm, "primary_family"], carrier_type=ctx.get("carrier_type"),
                             license_epmc=rk.loc[pm, "license"], license_color="verde", tier=tier, n_panels=len(P), n_descriptors=len(D), n_spectra=len(S),
                             categoria_uso=("nanomaterial" if ctx.get("carrier_type") == "nanomaterial" else "nanoportador"),
                             spectra="|".join(sorted({s["technique"] for s in spec_np})), image_files="|".join(sorted({p["image_file"] for p in P if p["image_file"]})), quotes_rejected=bad,
                             numbers_not_found=unverified))
            if tier != "no":
                pans += P
                descs += D
                specs += S
    A = pd.DataFrame(arts)
    A.to_csv(CUR / "ext_articulos.csv", index=False, encoding="utf-8-sig")
    if A.empty:
        print("sin salidas del extractor todavia")
        return
    cat = dict(zip(A.pmcid, A.categoria_uso))
    for name, rows in (("ext_paneles.csv", pans), ("ext_descriptores.csv", descs), ("ext_espectros.csv", specs)):
        df = pd.DataFrame(rows)
        if len(df):
            df.insert(1, "categoria_uso", df.pmcid.map(cat))
        df.to_csv(CUR / name, index=False, encoding="utf-8-sig")
    print(f"{len(A)} articulos leidos | E1: {int((A.tier == 'E1').sum())} | E2: {int((A.tier == 'E2').sum())} | no: {int((A.tier == 'no').sum())} | citas rechazadas: {bad_total}")
    print(f"paneles {len(pans)} | descriptores {len(descs)} | espectros {len(specs)}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    n = int(sys.argv[2]) if (len(sys.argv) > 2 and sys.argv[2].isdigit()) else None
    if cmd == "apply":
        apply()
    elif cmd == "export":
        export(tiers=tuple(sys.argv[2].split(",")) if len(sys.argv) > 2 else ("E1",), n_batches=int(sys.argv[3]) if len(sys.argv) > 3 else 10)
    elif cmd == "packets":
        packets(tiers=tuple(sys.argv[2].split(",")) if len(sys.argv) > 2 else ("E1",), limit=int(sys.argv[3]) if len(sys.argv) > 3 else None)
    else:
        {"rank": lambda: rank(n or 4000), "fetch": lambda: fetch(n), "screen": screen}[cmd]()
