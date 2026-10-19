"""Paso 2 del plan de ampliacion: filtro barato por CODIGO (0 tokens) sobre el texto ya descargado.

Para cada articulo busca evidencia de que cumple la puerta: micrografia en pie de figura, DLS con valor en nm y medio, zeta con valor en mV y medio/pH.
Calcula una puntuacion de prioridad (no es la puntuacion del repositorio) y una version corta del articulo para los agentes Haiku
(solo las frases con palabras clave, pies de figura de microscopia y tablas con tamano/zeta).

  python -m curation.cheap_filter score [pilot|main|all]   -> curation/data/cheap_scores.csv
  python -m curation.cheap_filter calibrate                -> contrasta la prioridad con lo que paso la puerta en el piloto
"""
from __future__ import annotations

import re
import sys

import pandas as pd

from src.common import ROOT
from curation import textprep

CUR = ROOT / "curation"
PACK_SHORT = CUR / "work" / "packets_short"

SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")
DLS_T = re.compile(r"\bDLS\b|dynamic light|hydrodynamic|z-average|zetasizer|laser (?:light )?scattering|photon correlation|\bPCS\b|particle size|mean size|average size|mean diameter|average diameter|\bNanoBrook|Nano[- ]?ZS|\bNTA\b", re.I)
ZETA_T = re.compile(r"zeta|\bZP\b|surface charge|electrophoretic mobility|laser doppler", re.I)
NM_VAL = re.compile(r"\d+(?:\.\d+)?\s*(?:±|\+/-|±)?\s*\d*(?:\.\d+)?\s*nm\b")
MV_VAL = re.compile(r"[-−–+]?\s?\d+(?:\.\d+)?\s*(?:±|\+/-|±)?\s*\d*(?:\.\d+)?\s*mV\b", re.I)
MEDIUM = re.compile(r"\bwater\b|\bPBS\b|phosphate[- ]buffered|saline|\bHEPES\b|\bTris\b|\bKCl\b|\bNaCl\b|\bserum\b|\bFBS\b|culture medium|\bDMEM\b|\bRPMI\b|"
                    r"citrate|acetate|\bbuffer\b|\bpH\s*\d|\bmilli-?q\b|ultrapure|deionized|deionised|\bdiluted in\b|\bdilution\b", re.I)
PHVAL = re.compile(r"\bpH\s*(?:of\s*)?\d", re.I)
MICRO_T = re.compile(r"\bTEM\b|\bSEM\b|\bSTEM\b|cryo-?\s?TEM|cryo-?\s?EM|cryo-?SEM|\bFE-?SEM\b|\bHR-?TEM\b|transmission electron|scanning electron|electron micro|micrograph|cryo-?electron", re.I)
MICRO_PREP = re.compile(r"uranyl|phosphotungstic|negative(?:ly)? stain|copper grid|carbon[- ]coated|formvar|sputter|gold[- ]coat|\bstub\b|vitrobot|vitrified|air[- ]dried|\bstained\b|osmium|grid", re.I)
SAXS_T = re.compile(r"\bSAXS\b|small[- ]angle X-ray|\bSANS\b", re.I)
XRD_T = re.compile(r"\bXRD\b|X-ray diffraction", re.I)
AAV = re.compile(r"adeno[\s-]?associated|\bAAV\d*\b|lentivir|virus[\s-]like|\bVLPs?\b|bacteriophage|\bphage\b", re.I)
COMP_T = re.compile(r"\bFTIR\b|FT-IR|infrared spectr|\bXRD\b|X-ray diffraction|\bSAXS\b|small[- ]angle|\bDSC\b|differential scanning|\bTGA\b|thermogravim|\bEDS\b|\bEDX\b|"
                    r"\bXPS\b|\bRaman\b|\bNMR\b|UV[- ]?Vis|absorption spectr|plasmon|\bNTA\b|nanoparticle tracking", re.I)
SKIP_TITLE =re.compile(r"\breview\b|\bperspective\b|\bprotocol\b|\bcommentary\b|meta-analysis|\bguidelines?\b", re.I)


def _units(pmcid: str):
    """Parrafos con su origen: (origen, texto)."""
    d = textprep.article_text(pmcid)
    out = [("methods", p) for _, p in d["methods"]] + [("results", p) for _, p in d["results"]] + [("other", p) for _, p in d["other"]]
    out += [("figure", f"{lab} {cap}") for lab, cap in d["figures"]]
    return d, out


def _table_flags(d):
    size_tab = zeta_tab = both_tab = False
    for lab, cap, rows, foot in d["tables"]:
        txt = " ".join([cap] + rows[:3] + [foot])
        head = (cap + " " + (rows[0] if rows else "")).lower()
        has_size = bool(re.search(r"size|diameter|\bpdi\b|polydisp|\bnm\b|hydrodynamic|z-?ave", head))
        has_zeta = bool(re.search(r"zeta|\bzp\b|\bmv\b|charge", head))
        body = " ".join(rows)
        numeric = len(re.findall(r"\d+(?:\.\d+)?", body)) >= 6
        size_tab |= has_size and numeric
        zeta_tab |= has_zeta and numeric
        both_tab |= has_size and has_zeta and numeric
    return size_tab, zeta_tab, both_tab


def features(pmcid: str) -> dict:
    d, units = _units(pmcid)
    f = dict(pmcid=pmcid, title=d["title"])
    f["review_title"] = bool(SKIP_TITLE.search(d["title"]))
    f["virus_text"] = len(AAV.findall(d["title"] + " " + d["abstract"])) > 0
    # DLS / zeta a nivel de frase (valor + termino) y de parrafo (metodo con medio)
    dls_val = zeta_val = dls_med_sent = zeta_med_sent = dls_med_par = zeta_med_par = 0
    micro_cap = micro_prep = micro_text = 0
    saxs = xrd = 0
    for origin, p in units:
        if origin != "figure" and not p:
            continue
        if DLS_T.search(p) and MEDIUM.search(p) and origin in ("methods", "figure"):
            dls_med_par += 1
        if ZETA_T.search(p) and (MEDIUM.search(p) or PHVAL.search(p)) and origin in ("methods", "figure"):
            zeta_med_par += 1
        for s in SENT.split(p):
            if DLS_T.search(s) and NM_VAL.search(s):
                dls_val += 1
                if MEDIUM.search(s):
                    dls_med_sent += 1
            if ZETA_T.search(s) and MV_VAL.search(s):
                zeta_val += 1
                if MEDIUM.search(s) or PHVAL.search(s):
                    zeta_med_sent += 1
        if origin == "figure" and MICRO_T.search(p):
            micro_cap += 1
        elif origin in ("methods", "results") and MICRO_T.search(p):
            micro_text += 1
            if MICRO_PREP.search(p):
                micro_prep += 1
        if SAXS_T.search(p):
            saxs += 1
        if XRD_T.search(p):
            xrd += 1
    size_tab, zeta_tab, both_tab = _table_flags(d)
    f.update(dls_val_sent=dls_val, zeta_val_sent=zeta_val, dls_med_sent=dls_med_sent, zeta_med_sent=zeta_med_sent, dls_med_par=dls_med_par, zeta_med_par=zeta_med_par,
             micro_cap=micro_cap, micro_text=micro_text, micro_prep=micro_prep, size_table=size_tab, zeta_table=zeta_tab, both_table=both_tab, saxs=saxs, xrd=xrd,
             n_figs=len(d["figures"]), n_tables=len(d["tables"]))
    dls_ok = (dls_val > 0 or size_tab)
    zeta_ok = (zeta_val > 0 or zeta_tab)
    score = 0
    score += 3 if micro_cap else (1 if micro_text else 0)
    score += 1 if micro_prep else 0
    score += 2 if dls_ok else 0
    score += 2 if zeta_ok else 0
    score += 3 if (dls_med_sent or dls_med_par) else 0
    score += 2 if (zeta_med_sent or zeta_med_par) else 0
    score += 1 if both_tab else 0
    f["priority"] = score
    f["tier"] = ("T1" if (micro_cap and dls_ok and zeta_ok and (dls_med_sent or dls_med_par) and (zeta_med_sent or zeta_med_par) and not f["review_title"] and not f["virus_text"])
                 else "T2" if (micro_cap and dls_ok and zeta_ok and (dls_med_sent or dls_med_par) and not f["review_title"] and not f["virus_text"])
                 else "T3" if (dls_ok and zeta_ok and (micro_cap or micro_text) and not f["review_title"] and not f["virus_text"])
                 else "T4")
    return f


# ---------------------------------------------------------------- paquete corto para Haiku
def short_packet(pmcid: str, cap_chars: int = 11000) -> str:
    d, units = _units(pmcid)
    L = [f"PMCID: {pmcid}", f"TITLE: {d['title']}", f"ABSTRACT: {d['abstract'][:1200]}", "", "=== KEY SENTENCES (Methods/Results; sentences about DLS, zeta, micrographs and the sample medium) ==="]
    seen, used, ncomp = set(), 0, 0
    for origin, p in units:
        if origin == "figure":
            continue
        sents = SENT.split(p)
        for i, s in enumerate(sents):
            is_comp = bool(COMP_T.search(s)) and ncomp < 10
            if (DLS_T.search(s) or ZETA_T.search(s) or MICRO_T.search(s) or is_comp) and s not in seen:
                ncomp += 1 if is_comp and not (DLS_T.search(s) or ZETA_T.search(s) or MICRO_T.search(s)) else 0
                piece = s if len(s) < 600 else s[:600]
                nxt_ok = i + 1 < len(sents) and (NM_VAL.search(sents[i + 1]) or MV_VAL.search(sents[i + 1])
                                                 or ((DLS_T.search(s) or ZETA_T.search(s)) and not MEDIUM.search(s) and (MEDIUM.search(sents[i + 1]) or PHVAL.search(sents[i + 1]))))
                if nxt_ok and sents[i + 1] not in seen:
                    piece += " " + sents[i + 1][:300]
                    seen.add(sents[i + 1])
                seen.add(s)
                tag = "M" if origin == "methods" else "R"
                if used + len(piece) > cap_chars * 0.55:
                    break
                L.append(f"[{tag}] {piece}"); used += len(piece)
    L += ["", "=== FIGURE CAPTIONS (microscopy, size, zeta) ==="]
    k = 0
    for lab, cap in d["figures"]:
        if (MICRO_T.search(cap) or DLS_T.search(cap) or ZETA_T.search(cap)) and k < 8:
            L.append(f"[{lab}] {cap[:700]}"); k += 1
    L += ["", "=== TABLES (size / zeta / composition) ==="]
    tused = 0
    for lab, cap, rows, foot in d["tables"]:
        head = (cap + " " + (rows[0] if rows else "")).lower()
        if re.search(r"size|diameter|\bpdi\b|zeta|\bmv\b|\bnm\b|charge|composition|formulation|ratio|lipid|polymer", head):
            block = f"[{lab}] {cap}\n" + "\n".join(rows[:30]) + (f"\n(note) {foot[:300]}" if foot else "")
            if tused + len(block) > cap_chars * 0.35:
                L.append(f"[{lab}] {cap[:150]} (table omitted: size limit)"); continue
            L.append(block); tused += len(block)
    return "\n".join(L)


def write_short_packets(pmcids, force=False):
    PACK_SHORT.mkdir(parents=True, exist_ok=True)
    for p in pmcids:
        f = PACK_SHORT / f"{p}.txt"
        if f.exists() and not force:
            continue
        f.write_text(short_packet(p), encoding="utf-8")


def score_all(which: str = "main") -> pd.DataFrame:
    man = pd.read_csv(CUR / "work" / "manifest.csv", dtype={"pmcid": str})
    ids = man.pmcid.tolist() if which == "all" else man[man.set == which].pmcid.tolist()
    rows = []
    for i, p in enumerate(ids):
        try:
            rows.append(features(p))
        except Exception as exc:  # noqa: BLE001
            rows.append(dict(pmcid=p, tier="T4", priority=-1, error=str(exc)[:100]))
    df = pd.DataFrame(rows).merge(man[["pmcid", "family", "set", "batch"]], on="pmcid")
    df.to_csv(CUR / "data" / f"cheap_scores_{which}.csv", index=False)
    print(df.groupby(["family", "tier"]).size().unstack(1).fillna(0).astype(int))
    return df


def calibrate() -> None:
    """Valida el filtro barato en el piloto: ¿la prioridad predice lo que paso la puerta (LLM A+B+arbitraje)?"""
    sc = score_all("pilot")
    fg = pd.read_csv(CUR / "work" / "final_gate.csv", dtype={"pmcid": str})
    sc = pd.read_csv(CUR / "data" / "cheap_scores_pilot.csv", dtype={"pmcid": str}).merge(fg[["pmcid", "gate", "micro", "dls", "zeta", "dls_dudoso", "zeta_dudoso"]], on="pmcid")
    sc["gate"] = sc["gate"].astype(bool)
    print("\nRendimiento por nivel (piloto, n=%d)" % len(sc))
    print(sc.groupby("tier").agg(n=("gate", "size"), pasan=("gate", "sum")).assign(tasa=lambda x: (x.pasan / x.n).round(2)))
    print("\nPor prioridad")
    print(sc.groupby("priority").agg(n=("gate", "size"), pasan=("gate", "sum")).assign(tasa=lambda x: (x.pasan / x.n).round(2)).to_string())
    tot = int(sc.gate.sum())
    for t in ("T1", "T2", "T3"):
        top = sc[sc.tier <= t]
        print(f"hasta {t}: {len(top)} articulos, {int(top.gate.sum())} de {tot} que pasan ({100 * top.gate.sum() / max(tot, 1):.0f} % del recall), tasa {top.gate.mean():.2f}")
    # recall de cada rasgo
    for c in ("dls_med_sent", "dls_med_par", "zeta_med_sent", "zeta_med_par", "micro_cap", "both_table"):
        v = sc[c] > 0 if sc[c].dtype != bool else sc[c]
        print(f"{c}: entre los que pasan {v[sc.gate].mean():.2f}; entre los que no pasan {v[~sc.gate].mean():.2f}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "score":
        score_all(sys.argv[2] if len(sys.argv) > 2 else "main")
    elif cmd == "calibrate":
        calibrate()
