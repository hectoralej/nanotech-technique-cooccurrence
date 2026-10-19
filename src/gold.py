"""Conjunto de validacion (gold set): muestreo, paquetes de revision a ciegas, y metricas del detector.

Definicion de verdad terreno para anotar (identica a la definicion primaria del detector, pero juzgada por una
persona): la tecnica fue **usada por los autores en este estudio** (se describe en Metodos) **y sus datos se
presentan** en Resultados, figuras o tablas. Mencionarla en Introduccion/Discusion o citar otros estudios NO cuenta.

Flujo:
  python -m src.gold sample      -> data/gold_sample.csv (+ procesa esos articulos con el detector)
  python -m src.gold packets     -> paquetes de frases (recall amplio, sin mostrar la salida del detector)
  (anotar)                       -> data/gold_set.csv   columnas: pmcid, annotator, <tecnica>..., notes
  python -m src.gold evaluate    -> data/gold_metrics.csv (+ kappa si hay >= 2 anotadores)
"""
from __future__ import annotations

import math
import re
import sys

import numpy as np
import pandas as pd

from .common import CACHE, DATA, load_yaml
from .data import flag_def
from .detect import technique_names
from .extract import ARTICLES, process_batch
from .fulltext import load_parsed
from .prec import wilson
from .sample import family_rng

GOLD_SAMPLE = DATA / "gold_sample.csv"
GOLD_SET = DATA / "gold_set.csv"
GOLD_METRICS = DATA / "gold_metrics.csv"
PACKETS = CACHE / "gold_packets"

BROAD = {
    "cryoEM": r"cryo|vitrif|plunge",
    "TEM": r"\bTEM\b|transmission|electron micro|micrograph|HRTEM",
    "STEM": r"\bSTEM\b|HAADF",
    "SEM": r"\bSEM\b|scanning electron|FE-?SEM",
    "AFM": r"\bAFM\b|atomic force",
    "DLS": r"scatter|\bDLS\b|hydrodynamic|\bPDI\b|polydispers|Zetasizer|z-average|particle size|size distribution|Malvern",
    "zeta": r"zeta|ζ|surface charge|electrophor",
    "NTA": r"\bNTA\b|NanoSight|ZetaView|tracking",
    "SAXS": r"SAXS|SANS|small[- ]angle",
    "XRD": r"\bXRD\b|diffraction|X-?ray",
    "FTIR": r"FT-?IR|infrared|\bIR\b",
    "UVVis": r"\bUV\b|absorption spectr|absorbance|plasmon|spectrophotomet",
    "EDS": r"\bEDS\b|\bEDX\b|energy[- ]dispersive|elemental",
    "DSC_TGA": r"\bDSC\b|\bTGA\b|calorim|thermogravim|thermal analysis",
    "NMR": r"\bNMR\b|nuclear magnetic",
}
_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")


def sample_gold() -> pd.DataFrame:
    samp = load_yaml("sampling.yaml")
    order = pd.read_csv(DATA / "ids" / "sample_order.csv", dtype={"pmcid": str})
    picked = []
    per_fam = samp["gold_min_per_family"]
    for fam, g in order[order["analysis_set"] == "main"].groupby("primary_family"):
        rng = family_rng(samp["seed"], fam, salt=1)
        pool = g[(g["rank_in_family"] > samp["pilot_per_family"]) &
                 (g["rank_in_family"] <= max(samp["targets"].get(fam, 150), samp["pilot_per_family"] + 3 * per_fam))]
        cand = pool.iloc[rng.permutation(len(pool))[: per_fam * 2]]
        process_batch(cand)
        art = pd.read_csv(ARTICLES, dtype={"pmcid": str}, low_memory=False)
        ok = art[art["pmcid"].isin(cand["pmcid"]) & art["in_scope"].astype(bool)]
        keep = [p for p in cand["pmcid"] if p in set(ok["pmcid"])][:per_fam]
        picked.append(cand[cand["pmcid"].isin(keep)])
    gs = pd.concat(picked, ignore_index=True)
    gs.to_csv(GOLD_SAMPLE, index=False)
    return gs


def build_packets() -> None:
    """Una carpeta de texto por articulo con las frases de recall amplio por tecnica, agrupadas por seccion."""
    PACKETS.mkdir(parents=True, exist_ok=True)
    gs = pd.read_csv(GOLD_SAMPLE, dtype={"pmcid": str})
    rx = {t: re.compile(p, re.I) for t, p in BROAD.items()}
    for _, r in gs.iterrows():
        parsed = load_parsed(r["pmcid"])
        lines = [f"# {r['pmcid']} | familia={r['primary_family']} | {r['title']}"]
        for t, pat in rx.items():
            out = []
            for sec, label in (("methods", "M"), ("results", "R"), ("caption", "C")):
                sents = [s for s in _SENT.split(parsed["sections"].get(sec, "")) if pat.search(s)]
                for s in sents[:4]:
                    out.append(f"  [{label}] {s[:230]}")
            lines.append(f"## {t}" + ("" if out else "  (sin frases)"))
            lines.extend(out)
        (PACKETS / f"{r['pmcid']}.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(gs)} paquetes en {PACKETS}")


def build_provisional() -> pd.DataFrame:
    """Convierte data/gold_annotations_claude_provisional.json en filas de gold_set.csv (UN anotador, no humano).

    No sustituye al conjunto de doble anotacion humana que pide el brief: sirve para desbloquear el punto de
    control y debe reemplazarse/confirmarse por el equipo (ver REPORT.md). Para anadir anotadores humanos, agregar
    filas con otro valor en `annotator`; evaluate() calcula kappa cuando hay >= 2.
    """
    import json
    ann = json.loads((DATA / "gold_annotations_claude_provisional.json").read_text(encoding="utf-8-sig"))
    techs = technique_names("core")
    gs = pd.read_csv(GOLD_SAMPLE, dtype={"pmcid": str})
    rows = []
    for p in gs["pmcid"]:
        r = {"pmcid": p, "annotator": "claude_provisional"}
        r.update({t: t in ann[p] for t in techs})
        rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(GOLD_SET, index=False)
    return df


def cohen_kappa(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.astype(bool), b.astype(bool)
    po = (a == b).mean()
    pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def evaluate_all() -> pd.DataFrame:
    out = pd.concat([evaluate(d) for d in ("primary", "body_any", "methods_only", "any")], ignore_index=True)
    out.to_csv(GOLD_METRICS, index=False)
    return out


def evaluate(definition: str = "primary") -> pd.DataFrame:
    techs = technique_names("core")
    gold = pd.read_csv(GOLD_SET, dtype={"pmcid": str})
    art = pd.read_csv(ARTICLES, dtype={"pmcid": str}, low_memory=False).set_index("pmcid")
    annotators = sorted(gold["annotator"].unique())
    rows = []
    # consenso: si hay >= 2 anotadores, verdad = ambos de acuerdo (los desacuerdos se listan y se excluyen de la metrica)
    wide = {a: gold[gold["annotator"] == a].set_index("pmcid")[techs].astype(bool) for a in annotators}
    common = sorted(set.intersection(*[set(w.index) for w in wide.values()]))
    for t in techs:
        if len(annotators) >= 2:
            a1, a2 = wide[annotators[0]].loc[common, t].to_numpy(), wide[annotators[1]].loc[common, t].to_numpy()
            kappa = cohen_kappa(a1, a2)
            agree = a1 == a2
            truth = pd.Series(a1, index=common)[agree]
        else:
            kappa = float("nan")
            truth = wide[annotators[0]].loc[common, t]
        pred = flag_def(art.loc[truth.index], t, definition)
        tp = int((truth & pred).sum()); fp = int((~truth & pred).sum())
        fn = int((truth & ~pred).sum()); tn = int((~truth & ~pred).sum())
        prec = tp / (tp + fp) if tp + fp else float("nan")
        rec = tp / (tp + fn) if tp + fn else float("nan")
        f1 = 2 * prec * rec / (prec + rec) if prec == prec and rec == rec and prec + rec > 0 else float("nan")
        spec = tn / (tn + fp) if tn + fp else float("nan")
        rlo, rhi = wilson(tp, tp + fn) if tp + fn else (float("nan"),) * 2
        rows.append(dict(definition=definition, technique=t, n_eval=len(truth), n_true=tp + fn, tp=tp, fp=fp, fn=fn, tn=tn,
                         precision=prec, recall=rec, recall_ci_lo=rlo, recall_ci_hi=rhi, f1=f1,
                         sensitivity=rec, specificity=spec, kappa_annotators=kappa,
                         annotators="|".join(annotators),
                         unreliable=bool(rec == rec and tp + fn >= 3 and rec < 0.85)))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "sample":
        print(sample_gold().groupby("primary_family").size())
    elif cmd == "packets":
        build_packets()
    elif cmd == "build-provisional":
        print(len(build_provisional()))
    elif cmd == "evaluate":
        pd.set_option("display.width", 220)
        res = evaluate_all()
        cols = ["definition", "technique", "n_true", "tp", "fp", "fn", "precision", "recall", "f1", "unreliable"]
        for d, g in res.groupby("definition", sort=False):
            print(f"--- definicion: {d}   F1 medio (tecnicas con positivos): {g[g.n_true > 0]['f1'].mean():.3f}")
            print(g[cols].round(3).to_string(index=False))
    else:
        print(__doc__)
