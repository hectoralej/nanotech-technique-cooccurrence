"""Compara las pasadas A y B (verificadas), deriva la puerta por codigo y lista los desacuerdos para el arbitraje.

  python -m curation.merge compare [--set pilot|human|main|all]   -> work/compare_<set>.csv + resumen de acuerdo
  python -m curation.merge conflicts <set>                          -> work/conflicts/<set>_NNN.json (para los subagentes de arbitraje)
"""
from __future__ import annotations

import json
import sys

import pandas as pd

from src.common import ROOT
from curation import equivalence as eq

CUR = ROOT / "curation"
GATE_FIELDS = ["micro", "dls", "zeta", "research", "object", "viral_pcr"]
TECHS_KEYED = ["micrograph", "DLS", "zeta"]


def load(p: str) -> dict:
    f = CUR / "work" / "verified" / f"{p}.jsonl"
    return {json.loads(l)["pmcid"]: json.loads(l) for l in open(f, encoding="utf-8")} if f.exists() else {}


def coarse_keys(rec: dict) -> dict[str, set]:
    """Claves GRUESAS (lo que decide la puerta y el grupo principal): identidad + medio (DLS/zeta) o variante (micrografia).
    Los detalles finos (temperatura, angulo, dilucion, pH, fuerza ionica, escala) no disparan arbitraje: si las pasadas discrepan se marcan 'disputado'
    y el grupo se separa (ver fine_disagreements)."""
    samples = {s["id"]: s for s in rec.get("samples", []) or []}
    out = {t: set() for t in TECHS_KEYED}
    for m in rec.get("measurements", []) or []:
        t, c = m.get("technique"), m.get("conditions") or {}
        if t not in out:
            continue
        ident = eq.identity_of(m, samples)
        if t == "micrograph":
            out[t].add(f"{m.get('variant')}|{ident}")
        elif t == "DLS":
            if (m.get("values") or {}).get("size_nm") is not None:
                out[t].add(f"{ident}|{eq.medium_class(c.get('medium'))}")
        else:
            if (m.get("values") or {}).get("zeta_mV") is not None:
                out[t].add(f"{ident}|{eq.medium_class(c.get('medium'))}|pH{'y' if c.get('pH') is not None else 'n'}")
    return out


def value_sets(rec: dict) -> dict[str, set]:
    out = {"DLS": set(), "zeta": set()}
    for m in rec.get("measurements", []) or []:
        v = m.get("values") or {}
        if m.get("technique") == "DLS" and eq._num(v.get("size_nm")) is not None:
            out["DLS"].add(round(eq._num(v["size_nm"])))
        if m.get("technique") == "zeta" and eq._num(v.get("zeta_mV")) is not None:
            out["zeta"].add(round(eq._num(v["zeta_mV"]), 1))
    return out


def compare_one(a: dict, b: dict) -> dict:
    ga, gb = eq.gate(a), eq.gate(b)
    ka, kb = coarse_keys(a), coarse_keys(b)
    va, vb = value_sets(a), value_sets(b)
    row = {"pmcid": a["pmcid"], "gate_A": ga["gate"], "gate_B": gb["gate"]}
    for f in GATE_FIELDS:
        row[f"{f}_A"], row[f"{f}_B"] = ga[f], gb[f]
        row[f"{f}_agree"] = ga[f] == gb[f]
    for t in TECHS_KEYED:
        row[f"{t}_keys_agree"] = ka[t] == kb[t]
        row[f"{t}_only_A"] = "|".join(sorted(ka[t] - kb[t]))
        row[f"{t}_only_B"] = "|".join(sorted(kb[t] - ka[t]))
    for t in ("DLS", "zeta"):
        both = va[t] & vb[t]; uni = va[t] | vb[t]
        row[f"{t}_values_jaccard"] = len(both) / len(uni) if uni else 1.0
        row[f"{t}_values_conflict"] = bool(va[t] and vb[t] and not both)       # ambas pasadas dan valores pero ninguno coincide
    row["dls_dudoso_A"], row["dls_dudoso_B"] = ga["dls_dudoso"], gb["dls_dudoso"]
    row["zeta_dudoso_A"], row["zeta_dudoso_B"] = ga["zeta_dudoso"], gb["zeta_dudoso"]
    gate_disp = (not all(row[f"{f}_agree"] for f in GATE_FIELDS))
    key_disp = (not all(row[f"{t}_keys_agree"] for t in TECHS_KEYED))
    val_disp = row["DLS_values_conflict"] or row["zeta_values_conflict"]
    row["needs_arbitration"] = bool(gate_disp or key_disp or val_disp)
    row["gate_conflict"] = ga["gate"] != gb["gate"]
    # relevancia: solo se arbitra si el desacuerdo puede cambiar la puerta o el grupo principal de un articulo que ALGUNA pasada dejo pasar o casi pasar
    # Se arbitra solo si la resolucion puede cambiar el resultado: (a) alguna combinacion de las decisiones de A y B haria pasar la puerta y hay
    # desacuerdo en un campo de la puerta, o (b) el articulo pasa (en alguna pasada) y hay discrepancias de grupo o de valores.
    could_pass = all((ga[f] or gb[f]) for f in ("micro", "dls", "zeta", "research", "object")) and not (ga["viral_pcr"] and gb["viral_pcr"])
    passes = ga["gate"] or gb["gate"]
    row["could_pass"] = bool(could_pass)
    row["arbitrate"] = bool((could_pass and gate_disp) or (passes and (key_disp or val_disp or row["gate_conflict"])))
    return row


def compare(which: str = "all") -> pd.DataFrame:
    A, B = load("A"), load("B")
    man = pd.read_csv(CUR / "work" / "manifest.csv", dtype={"pmcid": str})
    ids = [p for p in A if p in B and (which == "all" or man.set_index("pmcid").loc[p, "set"] == which)]
    rows = [compare_one(A[p], B[p]) for p in ids]
    df = pd.DataFrame(rows)
    df.to_csv(CUR / "work" / f"compare_{which}.csv", index=False)
    if df.empty:
        print("sin articulos con ambas pasadas"); return df
    print(f"articulos con A y B ({which}): {len(df)}")
    print(f"puerta: A pasa {int(df.gate_A.sum())}, B pasa {int(df.gate_B.sum())}, ambas {int((df.gate_A & df.gate_B).sum())}, desacuerdo de puerta {int(df.gate_conflict.sum())}")
    for f in GATE_FIELDS:
        print(f"  acuerdo {f}: {df[f'{f}_agree'].mean():.2f}")
    for t in TECHS_KEYED:
        print(f"  mismos grupos de equivalencia en {t}: {df[f'{t}_keys_agree'].mean():.2f}")
    print(f"necesitan arbitraje (cualquier desacuerdo): {int(df.needs_arbitration.sum())} de {len(df)}")
    return df


ABS = r"C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence\curation"


def _rows(rec: dict, tech: str, cap: int = 6) -> list[dict]:
    samples = {s["id"]: s for s in rec.get("samples", []) or []}
    out = []
    for m in rec.get("measurements", []) or []:
        if m.get("technique") != tech:
            continue
        out.append({"variant": m.get("variant"), "sample": (samples.get(m.get("sample_id")) or {}).get("name"), "identity": eq.identity_of(m, samples),
                    "shown_as": m.get("shown_as"), "link": (m.get("formulation_link") or {}).get("confidence"), "values": m.get("values"),
                    "conditions": m.get("conditions"), "quote": (m.get("evidence") or {}).get("quote"), "location": (m.get("evidence") or {}).get("location")})
    return out[:cap]


def build_conflicts(which: str = "pilot", per_file: int = 3, gate_only: bool = False) -> int:
    """gate_only (rondas de ampliacion): la pasada A leyo un extracto, asi que sus claves de grupo no son comparables con las de B (paquete completo).
    Solo se arbitran los campos de la puerta y los valores; los grupos de equivalencia salen de B."""
    A, B = load("A"), load("B")
    cmp_ = compare(which)
    if gate_only:
        gate_disp = ~cmp_[[f"{f}_agree" for f in GATE_FIELDS]].all(axis=1)
        vals = cmp_.DLS_values_conflict | cmp_.zeta_values_conflict
        todo = cmp_[(cmp_.could_pass & gate_disp) | (cmp_.gate_A | cmp_.gate_B) & vals]
    else:
        todo = cmp_[cmp_.arbitrate]
    # no repetir articulos ya arbitrados (decisiones existentes en work/llm/C)
    done = set()
    existing = sorted((CUR / "work" / "llm" / "C").glob("*.json"))
    for f in existing:
        try:
            for a in json.loads(f.read_text(encoding="utf-8-sig")).get("articles", []):
                done.add(a["pmcid"])
        except Exception:  # noqa: BLE001
            pass
    todo = todo[~todo.pmcid.isin(done)]
    start = len(list((CUR / "work" / "conflicts").glob("*.json"))) if (CUR / "work" / "conflicts").exists() else 0
    items = []
    tech_of = {"micro": "micrograph", "dls": "DLS", "zeta": "zeta"}
    for r in todo.itertuples():
        a, b = A[r.pmcid], B[r.pmcid]
        issues = []
        for f in GATE_FIELDS:
            if getattr(r, f"{f}_agree") is False or not getattr(r, f"{f}_agree"):
                it = {"issue": f"{r.pmcid}:gate:{f}", "A_says": bool(getattr(r, f"{f}_A")), "B_says": bool(getattr(r, f"{f}_B"))}
                if f in tech_of:
                    it["A_rows"], it["B_rows"] = _rows(a, tech_of[f]), _rows(b, tech_of[f])
                else:
                    it["A_context"], it["B_context"] = a.get("context"), b.get("context")
                issues.append(it)
        for t in TECHS_KEYED:
            if not gate_only and not getattr(r, f"{t}_keys_agree") and (r.gate_A or r.gate_B):
                issues.append({"issue": f"{r.pmcid}:keys:{t}", "only_in_A": getattr(r, f"{t}_only_A"), "only_in_B": getattr(r, f"{t}_only_B"),
                               "A_rows": _rows(a, t), "B_rows": _rows(b, t)})
        for t in ("DLS", "zeta"):
            if getattr(r, f"{t}_values_conflict"):
                issues.append({"issue": f"{r.pmcid}:values:{t}", "A_rows": _rows(a, t), "B_rows": _rows(b, t)})
        items.append({"pmcid": r.pmcid, "packet": f"{ABS}\\work\\packets\\{r.pmcid}.txt", "issues": issues})
    out = CUR / "work" / "conflicts"
    out.mkdir(exist_ok=True)
    n = 0
    for i in range(0, len(items), per_file):
        cid = f"{which[:1].upper()}C{start + i // per_file + 1:03d}"
        (out / f"{cid}.json").write_text(json.dumps({"batch": cid, "output": f"{ABS}\\work\\llm\\C\\{cid}.json", "articles": items[i:i + per_file]}, indent=1, ensure_ascii=False), encoding="utf-8")
        n += 1
    print(f"{len(items)} articulos a arbitrar en {n} archivos de conflicto")
    return n


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "compare":
        compare(sys.argv[2] if len(sys.argv) > 2 else "all")
    elif cmd == "conflicts":
        build_conflicts(sys.argv[2] if len(sys.argv) > 2 else "pilot", gate_only="--gate-only" in sys.argv)
