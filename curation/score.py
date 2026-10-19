"""Puntuacion determinista (curation/SCORING.md, fijada antes de ver resultados). Entrada: work/final.jsonl. Salida: work/scored.csv."""
from __future__ import annotations

import json

import pandas as pd

from src.common import ROOT
from curation import equivalence as eq

CUR = ROOT / "curation"
PREP_DECLARED = {"cryoTEM", "TEM_negstain", "TEM_posstain", "TEM_dried_unstained", "cryoSEM", "ESEM", "HRTEM", "STEM"}
COMPLEMENTARY = {"UVVis", "FTIR", "XRD", "EDS", "DSC", "TGA", "Raman", "NMR", "XPS", "NTA"}
FAMILY_COMPL = {"EDS": {"inorganic"}, "DSC": {"polymeric", "SLN_NLC"}, "TGA": {"polymeric", "SLN_NLC"}}
LINK_RANK = {"explicit": 2, "inferred": 1, "paper_level": 0}


def _has(x) -> bool:
    return x is not None and str(x).strip().lower() not in ("", "not_declared", "no_declarado", "nd", "null", "none", "unspecified")


def tier(score: float, gate: bool) -> str:
    if not gate:
        return "fuera"
    return "S" if score >= 85 else "A" if score >= 70 else "B" if score >= 60 else "fuera"


def score_record(r: dict) -> dict:
    samples = {s["id"]: s for s in r.get("samples", []) or []}
    ms = r.get("measurements", []) or []
    g = r["gate"]
    micro = [m for m in ms if eq.is_micro_useful(m, samples)]
    dls = [m for m in ms if eq.is_dls_useful(m, samples)[0]]
    zeta = [m for m in ms if eq.is_zeta_useful(m, samples)[0]]
    s_micro = s_dls = s_zeta = s_link = s_batch = s_comp = 0
    if g["micro"] and micro:
        s_micro = 10
        if any(m.get("variant") in PREP_DECLARED or _has((m.get("conditions") or {}).get("prep_state")) and m.get("variant") != "TEM_prep_not_declared" for m in micro):
            s_micro += 5
        if any(eq._num((m.get("values") or {}).get("n_particles_measured")) for m in micro):
            s_micro += 5
    if g["dls"] and dls:
        s_dls = 10
        if any(eq.medium_class((m.get("conditions") or {}).get("medium")) != "nd" and any(_has((m.get("conditions") or {}).get(k)) for k in ("temperature_C", "angle_deg", "dilution")) for m in dls):
            s_dls += 5
        if any(eq._num(m.get("n_replicates")) or eq._num((m.get("values") or {}).get("size_sd_nm")) is not None for m in dls):
            s_dls += 5
    if g["zeta"] and zeta:
        s_zeta = 10
        if any(eq.medium_class((m.get("conditions") or {}).get("medium")) != "nd" or _has((m.get("conditions") or {}).get("pH")) for m in zeta):
            s_zeta += 5
        if any(eq._num(m.get("n_replicates")) or eq._num((m.get("values") or {}).get("zeta_sd_mV")) is not None for m in zeta):
            s_zeta += 5
    core_rows = (micro[:1] + dls[:1] + zeta[:1]) if g["gate"] else []
    if core_rows:
        weakest = min(LINK_RANK.get((m.get("formulation_link") or {}).get("confidence"), 0) for m in core_rows)
        defined = all(((samples.get(m.get("sample_id")) or {}).get("formulation_defined_in") not in (None, "not_defined")) and _has((samples.get(m.get("sample_id")) or {}).get("composition")) for m in core_rows)
        s_link = {2: 15, 1: 8, 0: 0}[weakest] if defined else 0
    batch_ids = {m.get("sample_id") for m in dls + zeta}
    n_batches = len(batch_ids)
    s_batch = 10 if n_batches >= 4 else 5 if n_batches >= 2 else 0
    comp_pts, comp_used = 0, []
    for m in ms:
        t = m.get("technique")
        if t not in COMPLEMENTARY or t not in r.get("complementary_confirmed", []):
            continue
        if t in FAMILY_COMPL and r["family"] not in FAMILY_COMPL[t]:
            continue
        if eq.identity_of(m, samples) not in eq.USEFUL_IDENTITY:
            continue
        if t == "UVVis" and m.get("variant") != "a_intrinsic":
            continue
        pts = 3 if m.get("shown_as") in ("raw_curve", "figure_panel") else 1
        comp_pts += pts; comp_used.append(f"{t}({pts})")
    s_comp = min(15, comp_pts)
    total = s_micro + s_dls + s_zeta + s_link + s_batch + s_comp
    # una MISMA muestra (por nombre) debe tener micrografia, DLS y zeta utiles: si no, los tres datos no describen el mismo nanoportador
    nm = lambda m: (samples.get(m.get("sample_id"), {}).get("name") or str(m.get("sample_id"))).strip().lower()  # noqa: E731
    same_sample = bool({nm(m) for m in micro} & {nm(m) for m in dls} & {nm(m) for m in zeta})
    gate_ok = bool(g["gate"]) and not r.get("disputed") and same_sample
    return dict(pmcid=r["pmcid"], family=r["family"], gate=gate_ok, same_sample=same_sample, score=total, tier=tier(total, gate_ok), s_micro=s_micro, s_dls=s_dls, s_zeta=s_zeta, s_link=s_link,
                s_batches=s_batch, n_formulations=n_batches, s_complementary=s_comp, complementary="|".join(comp_used),
                micro_kind="SEM" if any(m.get("variant") in ("SEM", "cryoSEM", "ESEM") for m in micro) else ("cryo" if any("cryo" in (m.get("variant") or "") for m in micro) else "TEM" if micro else ""),
                micro_variants="|".join(sorted({m.get("variant") for m in micro})))


def run() -> pd.DataFrame:
    recs = [json.loads(l) for l in open(CUR / "work" / "final.jsonl", encoding="utf-8")]
    df = pd.DataFrame([score_record(r) for r in recs])
    df.to_csv(CUR / "work" / "scored.csv", index=False)
    print(df.groupby(["tier"]).size().to_string())
    return df


if __name__ == "__main__":
    run()
