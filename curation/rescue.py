"""Rescate de falsos negativos por medio no declarado (POLITICA_PUERTA.md, regla 1).

Articulos con micrografia util y filas de DLS o zeta con valor numerico pero sin medio: se buscan por codigo las frases de Metodos (o pies de tabla)
que nombran el medio junto a la medicion, y un agente barato (Haiku) decide, solo con esas frases, si el medio esta declarado para esas mediciones.
El codigo verifica la cita textual y deja una superposicion (overlay) que finalize.py aplica con la bandera `medio_rescatado`.

  python -m curation.rescue build    -> work/rescue/RB##.json (una tarea por lote de 8 articulos)
  python -m curation.rescue apply    -> work/rescue/overlay.json + curation/rescate_para_bryan.csv
"""
from __future__ import annotations

import json
import re
import sys

import pandas as pd

from src.common import ROOT
from curation import equivalence as eq, merge, textprep
from curation.recheck import MEDIUM

CUR = ROOT / "curation"
RES = CUR / "work" / "rescue"
ABS = r"C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence\curation"
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")
MEAS = {"DLS": re.compile(r"\bDLS\b|dynamic light|hydrodynamic|z-average|zetasizer|particle size|mean size|size distribution|photon correlation|\bPCS\b|NanoBrook|Nano[- ]?ZS", re.I),
        "zeta": re.compile(r"zeta|zetasizer|laser doppler|electrophoretic|\bELS\b|\bPALS\b", re.I)}
MEDIA_OK = {"water", "PBS", "buffer", "serum", "culture_medium"}


def _num(x):
    return eq._num(x)


def needs(rec: dict) -> dict:
    """Filas de DLS/zeta con valor numerico, identidad util y medio no declarado."""
    S = {s["id"]: s for s in rec.get("samples", []) or []}
    out = {"DLS": [], "zeta": []}
    for m in rec.get("measurements", []) or []:
        t = m.get("technique")
        if t not in out or eq.identity_of(m, S) not in eq.USEFUL_IDENTITY:
            continue
        v, c = m.get("values") or {}, m.get("conditions") or {}
        val = _num(v.get("size_nm")) if t == "DLS" else _num(v.get("zeta_mV"))
        if val is None or eq.medium_class(c.get("medium")) != "nd":
            continue
        if t == "zeta" and _num(c.get("pH")) is not None:
            continue
        out[t].append({"sample": (S.get(m.get("sample_id")) or {}).get("name"), "value": val})
    return {t: r for t, r in out.items() if r}


def candidate_sentences(pmcid: str, tech: str, limit: int = 8) -> list[dict]:
    d = textprep.article_text(pmcid)
    paras = ([("methods", p) for _, p in d["methods"]] + [("results", p) for _, p in d["results"]] + [("other", p) for _, p in d["other"]]
             + [("figure", c) for _, c in d["figures"]] + [("table_note", f"{cap} {foot}") for _, cap, _, foot in d["tables"]])
    out, seen = [], set()
    for origin, p in paras:
        sents = SENT.split(p or "")
        for i, s in enumerate(sents):
            if not MEAS[tech].search(s):
                continue
            text = s
            if not MEDIUM.search(s):
                if i + 1 < len(sents) and MEDIUM.search(sents[i + 1]):
                    text = s + " " + sents[i + 1]
                else:
                    continue
            text = text.strip()[:420]
            if text not in seen:
                seen.add(text)
                out.append({"where": origin, "text": text})
    out.sort(key=lambda x: 0 if x["where"] == "methods" else 1)
    return out[:limit]


def build() -> None:
    meta = pd.read_csv(CUR / "data" / "article_meta.csv", dtype=str).set_index("pmcid")
    retr = set(meta[meta.pub_types.fillna("").str.contains("retract", case=False)].index)
    cur = set(pd.read_csv(CUR / "articles_curated.csv", dtype=str).pmcid)
    fin = {}
    for line in open(CUR / "work" / "final.jsonl", encoding="utf-8"):
        r = json.loads(line)
        fin[r["pmcid"]] = r
    A, B = merge.load("A"), merge.load("B")
    items = []
    for p in sorted(set(A) | set(B)):
        if p in cur or p in retr:
            continue
        rec = fin.get(p) or B.get(p) or A.get(p)
        g = rec["gate"] if isinstance(rec.get("gate"), dict) and "gate" in rec["gate"] else eq.gate(rec)
        if not (g["research"] and g["object"] and not g["viral_pcr"] and g["micro"]) or g["gate"]:
            continue
        nd = needs(rec)
        task = {}
        for t, rows in nd.items():
            sents = candidate_sentences(p, t)
            if sents:
                task[t] = {"rows": rows[:6], "n_rows": len(rows), "sentences": sents}
        if task:
            items.append({"pmcid": p, "title": (meta.loc[p, "title"] if p in meta.index else "")[:120], "needs": task})
    RES.mkdir(parents=True, exist_ok=True)
    (CUR / "work" / "llm" / "R").mkdir(parents=True, exist_ok=True)
    n = 0
    for i in range(0, len(items), 8):
        bid = f"RB{i // 8 + 1:02d}"
        (RES / f"{bid}.json").write_text(json.dumps({"batch": bid, "output": f"{ABS}\\work\\llm\\R\\{bid}.json", "articles": items[i:i + 8]}, indent=1, ensure_ascii=False), encoding="utf-8")
        n += 1
    print(f"{len(items)} articulos con frases de medio hallables, en {n} lotes")


def apply() -> None:
    overlay, rows = {}, []
    meta = pd.read_csv(CUR / "data" / "article_meta.csv", dtype=str).set_index("pmcid")
    man = pd.read_csv(CUR / "work" / "manifest.csv", dtype={"pmcid": str}).set_index("pmcid")
    n_dec = n_bad = 0
    mf = CUR / "manual_review.csv"
    excluded_by_hand = set(pd.read_csv(mf, dtype=str).query("decision == 'excluir'").pmcid) if mf.exists() else set()
    for f in sorted((CUR / "work" / "llm" / "R").glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8-sig"))
        except Exception:  # noqa: BLE001
            continue
        for a in d.get("articles", []):
            p = a["pmcid"]
            for dec in a.get("decisions", []):
                n_dec += 1
                t, med, q = dec.get("technique"), dec.get("medium"), dec.get("quote") or ""
                if t not in ("DLS", "zeta") or med in (None, "not_found") or dec.get("applies_to") != "all_samples":
                    continue
                if str(med).split(":")[0] not in MEDIA_OK | {"other"}:
                    continue
                ok, score = textprep.quote_found(q, p)
                if not ok:
                    n_bad += 1
                    continue
                overlay.setdefault(p, {})[t] = {"medium": med, "quote": q[:200], "match": score}
                if p in excluded_by_hand:
                    continue
                rows.append(dict(pmcid=p, doi_link=("https://doi.org/" + meta.loc[p, "doi"]) if isinstance(meta.loc[p, "doi"], str) else "https://pmc.ncbi.nlm.nih.gov/articles/" + p + "/",
                                 familia=man.loc[p, "family"], licencia_europepmc=meta.loc[p, "license_epmc"], tecnica=t, medio_rescatado=med, cita=q[:200], decision_bryan="", nota_bryan=""))
    (RES / "overlay.json").write_text(json.dumps(overlay, indent=1, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(rows).to_csv(CUR / "rescate_para_bryan.csv", index=False, encoding="utf-8-sig")
    print(f"{n_dec} decisiones; {n_bad} con cita no verificada; {len(overlay)} articulos con medio rescatado")


if __name__ == "__main__":
    {"build": build, "apply": apply}[sys.argv[1]]()
