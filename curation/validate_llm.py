"""Valida la salida de los subagentes: JSON valido, esquema minimo y VERIFICACION AUTOMATICA DE CITAS.

Una medicion cuya cita no aparece en el texto del articulo se anula (se registra en rejected_measurements.csv). Salida por pasada:
curation/work/verified/<P>.jsonl (una linea por articulo) y curation/work/verified/<P>_log.csv.
"""
from __future__ import annotations

import json
import sys

import pandas as pd

from src.common import ROOT
from curation import textprep

CUR = ROOT / "curation"
TECH = {"micrograph", "DLS", "zeta", "UVVis", "FTIR", "XRD", "EDS", "SAXS", "DSC", "TGA", "Raman", "NMR", "XPS", "NTA"}


def load_pass(p: str):
    recs, errors = {}, []
    for f in sorted((CUR / "work" / "llm" / p).glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8-sig"))
            for r in d["articles"]:
                recs[r["pmcid"]] = {**r, "_batch": f.stem}
        except Exception as exc:  # noqa: BLE001
            errors.append((f.name, str(exc)[:150]))
    return recs, errors


def verify(rec: dict):
    """Devuelve (registro verificado, lista de mediciones anuladas)."""
    pm = rec["pmcid"]
    ok, bad = [], []
    for m in rec.get("measurements", []) or []:
        q = ((m.get("evidence") or {}).get("quote")) or ""
        found, score = textprep.quote_found(q, pm)
        m["evidence"]["verified"] = bool(found); m["evidence"]["match_score"] = score
        if m.get("technique") not in TECH or not found:
            bad.append({"pmcid": pm, "technique": m.get("technique"), "quote": q[:200], "score": score,
                        "reason": "tecnica_invalida" if m.get("technique") not in TECH else "cita_no_encontrada"})
        else:
            ok.append(m)
    si = []
    for s in rec.get("si_mentions", []) or []:
        found, _ = textprep.quote_found(s.get("quote", ""), pm)
        if found:
            si.append(s)
    out = {**rec, "measurements": ok, "si_mentions": si}
    return out, bad


def run(p: str) -> None:
    recs, errors = load_pass(p)
    (CUR / "work" / "verified").mkdir(exist_ok=True)
    kept, rejected, log = [], [], []
    for pm, r in recs.items():
        try:
            v, bad = verify(r)
        except Exception as exc:  # noqa: BLE001
            errors.append((pm, f"verificacion: {exc}")); continue
        kept.append(v); rejected += bad
        n_total = len(r.get("measurements", []) or [])
        log.append(dict(pmcid=pm, batch=r["_batch"], n_meas=n_total, n_rejected=len(bad)))
    with open(CUR / "work" / "verified" / f"{p}.jsonl", "w", encoding="utf-8") as fh:
        for v in kept:
            fh.write(json.dumps(v, ensure_ascii=False) + "\n")
    pd.DataFrame(log).to_csv(CUR / "work" / "verified" / f"{p}_log.csv", index=False)
    pd.DataFrame(rejected).to_csv(CUR / "work" / "verified" / f"{p}_rejected.csv", index=False)
    tot = sum(x["n_meas"] for x in log); rej = sum(x["n_rejected"] for x in log)
    print(f"pasada {p}: {len(kept)} articulos, {tot} mediciones, {rej} anuladas por cita no encontrada ({100 * rej / max(tot, 1):.1f} %), errores de archivo: {len(errors)}")
    for e in errors[:10]:
        print("  error:", e)


if __name__ == "__main__":
    run(sys.argv[1])
