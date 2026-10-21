"""Registro final por articulo: base = pasada B, con las decisiones de arbitraje (citas verificadas) aplicadas; lo no resuelto queda 'disputado'.

Salida: curation/work/final.jsonl (un registro por articulo con A y B) y curation/work/final_gate.csv.
"""
from __future__ import annotations

import json
import sys

import pandas as pd

from src.common import ROOT
from curation import equivalence as eq, merge, textprep

CUR = ROOT / "curation"
TECH_OF = {"micro": "micrograph", "dls": "DLS", "zeta": "zeta"}


def load_arbitration() -> dict:
    """issue -> decision (con cita verificada por codigo)."""
    out = {}
    for f in sorted((CUR / "work" / "llm" / "C").glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8-sig"))
        except Exception:  # noqa: BLE001
            continue
        for a in d.get("articles", []):
            for dec in a.get("decisions", []):
                q = dec.get("quote") or ""
                ok, score = (textprep.quote_found(q, a["pmcid"]) if q else (False, 0))
                dec["quote_verified"], dec["quote_score"], dec["pmcid"] = ok, score, a["pmcid"]
                if dec.get("decision") != "unresolved" and not ok:
                    dec["decision"] = "unresolved"; dec["reason"] = (dec.get("reason") or "") + " [cita del arbitraje no verificada]"
                out[dec["issue"]] = dec
    return out


def _adopt_rows(base: dict, src: dict, tech: str) -> None:
    """Sustituye en `base` las filas de `tech` por las de `src`; las muestras de `src` se anaden con prefijo 'A_'."""
    have = {s["id"] for s in base.get("samples", []) or []}
    for s in src.get("samples", []) or []:
        if "A_" + s["id"] not in have:
            base.setdefault("samples", []).append({**s, "id": "A_" + s["id"]})
    rows = []
    for m in src.get("measurements", []):
        if m.get("technique") == tech:
            m2 = json.loads(json.dumps(m)); m2["sample_id"] = "A_" + str(m.get("sample_id")); rows.append(m2)
    base["measurements"] = [m for m in base["measurements"] if m["technique"] != tech] + rows


def load_overlay() -> dict:
    f = CUR / "work" / "rescue" / "overlay.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def _apply_overlay(base: dict, ov: dict) -> None:
    """Medio rescatado (cita verificada por codigo): se escribe en las filas de DLS/zeta con valor, identidad util y medio no declarado."""
    S = {s["id"]: s for s in base.get("samples", []) or []}
    for m in base.get("measurements", []):
        t = m.get("technique")
        if t not in ov or eq.identity_of(m, S) not in eq.USEFUL_IDENTITY:
            continue
        c = m.setdefault("conditions", {})
        if eq.medium_class(c.get("medium")) != "nd":
            continue
        c["medium"] = ov[t]["medium"]
        m["quality_flags"] = sorted(set((m.get("quality_flags") or []) + ["medio_rescatado"]) - {"medio_no_declarado"})
        m.setdefault("evidence", {})["rescue_quote"] = ov[t]["quote"]


def finalize(which: str = "all") -> pd.DataFrame:
    A, B = merge.load("A"), merge.load("B")
    arb = load_arbitration()
    cmp_ = merge.compare(which).set_index("pmcid")
    man = pd.read_csv(CUR / "work" / "manifest.csv", dtype={"pmcid": str}).set_index("pmcid")
    finals, rows = [], []
    overlay = load_overlay()
    for pm in cmp_.index:
        a, b, c = A[pm], B[pm], cmp_.loc[pm]
        base = json.loads(json.dumps(b))
        ga, gb = eq.gate(a), eq.gate(b)
        gate = dict(gb)
        disputed, notes = [], []
        # 1) campos de la puerta
        for f in ("micro", "dls", "zeta", "object", "research", "viral_pcr"):
            if ga[f] != gb[f]:
                d = arb.get(f"{pm}:gate:{f}")
                if d is None:
                    if bool(c["arbitrate"]):             # debia arbitrarse y aun no se hizo (p. ej. limite de uso): pendiente
                        disputed.append(f"gate:{f}:pendiente_arbitraje")
                    else:                                  # la resolucion no podia cambiar el resultado: se conserva el valor de B
                        notes.append(f"{f}: A y B discrepan, sin efecto en la puerta")
                elif d["decision"] == "unresolved":
                    disputed.append(f"gate:{f}")
                else:
                    gate[f] = bool((d.get("final") or {}).get("value"))
                    notes.append(f"{f} arbitrado -> {gate[f]}")
                    if f in TECH_OF and gate[f] and not gb[f] and ga[f]:
                        # el arbitro da la razon a A: las filas de esa tecnica salen de A (con sus muestras, prefijadas para no chocar con los ids de B)
                        _adopt_rows(base, a, TECH_OF[f])
                        notes.append(f"{f}: filas de A adoptadas")
        # 2) grupos y valores: reemplazar filas de la tecnica por las de la pasada elegida
        for t in merge.TECHS_KEYED:
            issue = f"{pm}:keys:{t}"
            vissue = f"{pm}:values:{t}"
            for iss in (issue, vissue):
                if iss in arb:
                    d = arb[iss]
                    if d["decision"] in ("A", "B"):
                        src = a if d["decision"] == "A" else b
                        base["measurements"] = [m for m in base["measurements"] if m["technique"] != t] + [m for m in src["measurements"] if m["technique"] == t]
                        base["samples"] = src["samples"] if d["decision"] == "A" else base["samples"]
                        notes.append(f"{t}: filas de {d['decision']}")
                    elif d["decision"] == "unresolved":
                        disputed.append(f"{iss}")
                    else:
                        disputed.append(f"{iss}:neither")
        samples = {s["id"]: s for s in base.get("samples", []) or []}
        # recomputar puerta base con filas finales y aplicar overrides arbitrados
        g2 = eq.gate(base)
        for f in ("micro", "dls", "zeta", "object", "research", "viral_pcr"):
            if f"{pm}:gate:{f}" not in arb or arb[f"{pm}:gate:{f}"]["decision"] == "unresolved":
                gate[f] = g2[f] if ga[f] == gb[f] else gate[f]
        ov = overlay.get(pm)
        if ov:
            _apply_overlay(base, ov)
            g3 = eq.gate(base)
            for f in ("dls", "zeta"):
                gate[f] = bool(gate[f] or g3[f])
            gate["dls_dudoso"], gate["zeta_dudoso"] = bool(g3["dls_dudoso"] and not gate["dls"]), bool(g3["zeta_dudoso"] and not gate["zeta"])
            notes.append("medio rescatado: " + ",".join(sorted(ov)))
        gate["gate"] = bool(gate["micro"] and gate["dls"] and gate["zeta"] and gate["research"] and gate["object"] and not gate["viral_pcr"])
        # complementarias confirmadas por ambas pasadas (tecnica + clase de identidad)
        confirmed = set()
        sa = {s["id"]: s for s in a.get("samples", []) or []}
        for m in a.get("measurements", []):
            confirmed.add((m["technique"], eq.identity_of(m, sa)))
        sb = samples
        base["complementary_confirmed"] = sorted({m["technique"] for m in base["measurements"] if (m["technique"], eq.identity_of(m, sb)) in confirmed
                                                  and m["technique"] not in ("micrograph", "DLS", "zeta")})
        base["gate"], base["disputed"], base["arbitration_notes"] = gate, disputed, notes
        base["family"], base["set"] = man.loc[pm, "family"], man.loc[pm, "set"]
        finals.append(base)
        rows.append(dict(pmcid=pm, family=base["family"], set=base["set"], gate=gate["gate"], disputed=bool(disputed), disputed_why="|".join(disputed),
                         micro=gate["micro"], dls=gate["dls"], zeta=gate["zeta"], dls_dudoso=gate["dls_dudoso"], zeta_dudoso=gate["zeta_dudoso"],
                         object=gate["object"], research=gate["research"], viral_pcr=gate["viral_pcr"], arbitrated=bool(notes)))
    # articulos con UNA sola pasada que ganan el medio por el rescate: entran como finales, marcados 'una_pasada'
    for pm, ov in overlay.items():
        if pm in cmp_.index or pm not in (set(A) | set(B)) or pm not in man.index:
            continue
        base = json.loads(json.dumps(B.get(pm) or A[pm]))
        gate = dict(eq.gate(base))
        _apply_overlay(base, ov)
        g3 = eq.gate(base)
        gate = dict(g3)
        base["complementary_confirmed"] = []
        base["gate"], base["disputed"], base["arbitration_notes"] = gate, [], ["una sola pasada", "medio rescatado: " + ",".join(sorted(ov))]
        base["family"], base["set"] = man.loc[pm, "family"], man.loc[pm, "set"]
        finals.append(base)
        rows.append(dict(pmcid=pm, family=base["family"], set=base["set"], gate=gate["gate"], disputed=False, disputed_why="", micro=gate["micro"], dls=gate["dls"], zeta=gate["zeta"],
                         dls_dudoso=gate["dls_dudoso"], zeta_dudoso=gate["zeta_dudoso"], object=gate["object"], research=gate["research"], viral_pcr=gate["viral_pcr"], arbitrated=True))
    with open(CUR / "work" / "final.jsonl", "w", encoding="utf-8") as fh:
        for r in finals:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    df = pd.DataFrame(rows)
    df.to_csv(CUR / "work" / "final_gate.csv", index=False)
    print(f"{len(df)} articulos finales; pasan la puerta: {int((df.gate & ~df.disputed).sum())}; disputados: {int(df.disputed.sum())}")
    return df


if __name__ == "__main__":
    finalize(sys.argv[1] if len(sys.argv) > 1 else "all")
