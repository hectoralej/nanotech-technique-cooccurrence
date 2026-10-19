"""Contraste de H1..H10 con las reglas de decision de PREREGISTRATION.md. Escribe data/hypotheses.csv."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.stats import norm

from .common import DATA, load_yaml
from .data import FAMILY_ORDER, MICRO, ORGANIC, load_articles, reliability_table
from .prec import wilson

MIN_N = 20


def cond(df: pd.DataFrame, A, B, fam=None):
    """(k, n, p, lo, hi) de P(B|A) dentro de la familia `fam` (o todo). A, B: nombre de columna o serie booleana."""
    sub = df if fam is None else df[df["primary_family"].isin([fam] if isinstance(fam, str) else fam)]
    a = sub[A] if isinstance(A, str) else A.loc[sub.index]
    b = sub[B] if isinstance(B, str) else B.loc[sub.index]
    n = int(a.sum()); k = int((a & b).sum())
    lo, hi = wilson(k, n) if n else (np.nan, np.nan)
    return k, n, (k / n if n else np.nan), lo, hi


def z2(k1, n1, k2, n2) -> float:
    """p bilateral de la prueba z para dos proporciones independientes."""
    if min(n1, n2) == 0:
        return float("nan")
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return float("nan") if se == 0 else float(2 * (1 - norm.cdf(abs((k1 / n1 - k2 / n2) / se))))


def fmt(c):
    k, n, p, lo, hi = c
    return "n.d." if not n else f"{p:.2f} [{lo:.2f}-{hi:.2f}] ({k}/{n})"


def run() -> pd.DataFrame:
    headline = load_yaml("sampling.yaml")["headline_definition"]
    df = load_articles(headline)
    rel = reliability_table(headline).set_index("technique")["reliability"]
    pairs = pd.read_csv(DATA / "pairs.csv")
    out = []

    def caveat(*techs):
        bad = [f"{t}:{rel.get(t, 'unvalidated')}" for t in techs if rel.get(t, "unvalidated") != "ok"]
        return ("detector no plenamente fiable/validado: " + ", ".join(bad)) if bad else ""

    def add(h, verdict, evidence, techs=()):
        out.append(dict(id=h, verdict=verdict, evidence=evidence, caveat=caveat(*techs)))

    # ------------------------------------------------------------------ H1
    ev, ok_all, ev_n = [], True, 0
    comp_hits = []
    for f in ORGANIC:
        c_tem, c_sem = cond(df, "TEM", "DLS", f), cond(df, "SEM", "DLS", f)
        ev.append(f"{f}: P(DLS|TEM)={fmt(c_tem)} vs P(DLS|SEM)={fmt(c_sem)}")
        if c_tem[1] >= MIN_N:
            ev_n += 1
            ok_all &= c_tem[2] >= 0.5
            if c_sem[1] >= MIN_N:
                comp_hits.append(c_tem[2] > c_sem[2])
    agg_tem = cond(df, "TEM", "DLS", ORGANIC); agg_sem = cond(df, "SEM", "DLS", ORGANIC)
    ev.append(f"organicas agregadas: P(DLS|TEM)={fmt(agg_tem)} vs P(DLS|SEM)={fmt(agg_sem)}; p(z)={z2(agg_tem[0], agg_tem[1], agg_sem[0], agg_sem[1]):.3g}")
    maj = (sum(comp_hits) > len(comp_hits) / 2) if comp_hits else False
    if ev_n < 3:
        v = "inconclusa"
    elif ok_all and agg_tem[2] > agg_sem[2] and maj:
        v = "confirmada"
    elif (not ok_all) and agg_tem[2] <= agg_sem[2]:
        v = "refutada"
    else:
        v = "parcial (ver evidencia)"
    add("H1", v, " | ".join(ev), ["TEM", "SEM", "DLS"])

    # ------------------------------------------------------------------ H2
    dry_tem = df["TEM"] & ~df["cryoEM"]
    ev, res = [], []
    for f in ("LNP", "liposome"):
        ccr, ctem = cond(df, "cryoEM", "SAXS", f), cond(df, dry_tem, "SAXS", f)
        pz = z2(ccr[0], ccr[1], ctem[0], ctem[1])
        # "mayor" = mayor y diferencia significativa (definicion general del preregistro); prueba exacta de Fisher por conteos pequenos
        from scipy.stats import fisher_exact
        pf = fisher_exact([[ccr[0], ccr[1] - ccr[0]], [ctem[0], ctem[1] - ctem[0]]], alternative="greater")[1] if min(ccr[1], ctem[1]) else float("nan")
        ev.append(f"{f}: P(SAXS|cryoEM)={fmt(ccr)} vs P(SAXS|TEM seco)={fmt(ctem)} (Fisher unilateral p={pf:.3g})")
        res.append(None if ccr[1] < MIN_N or ctem[1] < MIN_N else (ccr[2] > ctem[2] and pf < 0.05))
    v = "inconclusa" if any(r is None for r in res) else ("confirmada" if all(res) else ("refutada" if not any(res) else "parcial (ver evidencia)"))
    add("H2", v, " | ".join(ev), ["cryoEM", "TEM", "SAXS"])

    # ------------------------------------------------------------------ H3
    ev, res = [], []
    for t in ("UVVis", "XRD"):
        ci = cond(df, "TEM", t, "inorganic"); co = cond(df, "TEM", t, ORGANIC)
        p = z2(ci[0], ci[1], co[0], co[1])
        ev.append(f"P({t}|TEM): inorganica={fmt(ci)} vs organicas={fmt(co)} (p={p:.3g})")
        res.append(None if ci[1] < MIN_N or co[1] < MIN_N else (ci[2] > co[2] and p < 0.05))
    v = "inconclusa" if any(r is None for r in res) else ("confirmada" if all(res) else ("refutada" if not any(res) else "parcial (ver evidencia)"))
    add("H3", v, " | ".join(ev), ["TEM", "UVVis", "XRD"])

    # ------------------------------------------------------------------ H4
    ev = []
    csem, ctem = cond(df, "SEM", "EDS", "inorganic"), cond(df, "TEM", "EDS", "inorganic")
    p = z2(csem[0], csem[1], ctem[0], ctem[1])
    ev.append(f"inorganica: P(EDS|SEM)={fmt(csem)} vs P(EDS|TEM)={fmt(ctem)} (p={p:.3g})")
    org_ok = []
    for f in ORGANIC:
        for a in ("SEM", "TEM"):
            c = cond(df, a, "EDS", f)
            ev.append(f"{f}: P(EDS|{a})={fmt(c)}")
            if c[1] >= MIN_N:
                org_ok.append(c[2] < 0.10)
    if csem[1] < MIN_N or ctem[1] < MIN_N or not org_ok:
        v = "inconclusa"
    else:
        part1 = csem[2] > ctem[2]
        part2 = all(org_ok)
        v = "confirmada" if part1 and part2 else ("refutada" if not part1 and not part2 else "parcial (ver evidencia)")
    add("H4", v, " | ".join(ev), ["SEM", "TEM", "EDS"])

    # ------------------------------------------------------------------ H5
    sub = pairs[(pairs.A == "DLS") & (pairs.B == "zeta") & pairs.stratum.isin(["ALL"] + FAMILY_ORDER)].set_index("stratum")
    phi_all = float(sub.loc["ALL", "phi"])
    fam_ok = [f for f in FAMILY_ORDER if f in sub.index and sub.loc[f, "nAB"] >= 0 and sub.loc[f, "phi"] >= 0.3 and sub.loc[f, "N"] >= MIN_N]
    core = [t for t in load_yaml("techniques.yaml")["techniques"] if load_yaml("techniques.yaml")["techniques"][t]["tier"] == "core"]
    allp = pairs[(pairs.stratum == "ALL") & pairs.A.isin(core) & pairs.B.isin(core) & (pairs.A < pairs.B)].sort_values("phi", ascending=False)
    rank = list(zip(allp.A, allp.B)).index(("DLS", "zeta")) + 1 if ("DLS", "zeta") in set(zip(allp.A, allp.B)) else None
    ev = f"phi(DLS,zeta) ALL={phi_all:.2f}; familias con phi>=0.3: {fam_ok}; rango entre pares de nucleo (ALL): {rank} de {len(allp)}"
    v = "confirmada" if phi_all >= 0.3 and len(fam_ok) >= 4 and rank is not None and rank <= 3 else (
        "refutada" if phi_all < 0.3 else "parcial (ver evidencia)")
    add("H5", v, ev, ["DLS", "zeta"])

    # ------------------------------------------------------------------ H6
    ev, res = [], []
    for t in ("FTIR", "DSC_TGA"):
        lnp = cond(df, df["EM"] | ~df["EM"], t, "LNP")
        for f in ("polymeric", "SLN_NLC"):
            c = cond(df, df["EM"] | ~df["EM"], t, f)
            sep = c[3] > lnp[4]                                    # IC inferior de f > IC superior de LNP
            ev.append(f"{t}: {f}={fmt(c)} vs LNP={fmt(lnp)}" + (" (IC no solapados)" if sep else ""))
            res.append(None if min(c[1], lnp[1]) < MIN_N else sep)
    v = "inconclusa" if any(r is None for r in res) else ("confirmada" if all(res) else ("refutada" if not any(res) else "parcial (ver evidencia)"))
    add("H6", v, " | ".join(ev), ["FTIR", "DSC_TGA"])

    # ------------------------------------------------------------------ H7
    aav = df[df["primary_family"] == "AAV"]
    em_aav = aav["cryoEM"] | aav["TEM"]
    other = aav["AUC"] | aav["qPCR_ddPCR"]
    c1 = cond(aav, em_aav, other, None); c2 = cond(aav, em_aav, aav["DLS"], None)
    sem_prev = (int(aav["SEM"].sum()), len(aav)) + tuple(wilson(int(aav["SEM"].sum()), len(aav)))
    ev = f"AAV: P(AUC o qPCR | cryoEM o TEM)={fmt(c1)} vs P(DLS | cryoEM o TEM)={fmt(c2)}; prevalencia SEM={sem_prev[0]}/{sem_prev[1]}"
    if c1[1] < MIN_N:
        v = "inconclusa"
    else:
        a, b = c1[2] > c2[2], (sem_prev[0] / max(sem_prev[1], 1)) < 0.05
        v = "confirmada" if a and b else ("refutada" if not a and not b else "parcial (ver evidencia)")
    add("H7", v, ev, ["cryoEM", "TEM", "AUC", "qPCR_ddPCR", "DLS", "SEM"])

    # ------------------------------------------------------------------ H8
    c = cond(df, "DLS", "zeta", None)
    cf = [f"{f}: {fmt(cond(df, 'DLS', 'zeta', f))}" for f in FAMILY_ORDER]
    add("H8", "confirmada" if c[4] < 0.95 else ("refutada" if c[3] >= 0.95 else "inconclusa"),
        f"P(zeta|DLS) ALL={fmt(c)}; por familia: " + " | ".join(cf), ["DLS", "zeta"])

    # ------------------------------------------------------------------ H9
    em = df[df["EM"]]
    allc = cond(em, em["EM"], em["figms_any"].astype(bool), None)
    fam_vals = {}
    for f in FAMILY_ORDER:
        s = em[em["primary_family"] == f]
        if len(s) >= MIN_N:
            fam_vals[f] = (int(s["figms_any"].sum()), len(s), s["figms_any"].mean())
    rng = (max(v[2] for v in fam_vals.values()) - min(v[2] for v in fam_vals.values())) if fam_vals else float("nan")
    ev = (f"micrografia+espectro en la misma figura entre articulos con EM: ALL={fmt(allc)}; por familia: " +
          " | ".join(f"{f}={v[0]}/{v[1]}={v[2]:.2f}" for f, v in fam_vals.items()) + f"; rango={rng:.2f}")
    v = "confirmada" if allc[2] < 0.25 and rng > 0.10 else ("refutada" if allc[2] >= 0.25 and rng <= 0.10 else "parcial (ver evidencia)")
    add("H9", v, ev + "  [proxy: pie con termino de microscopia y de espectroscopia; el detector de pie es mas estricto que el de articulo]",
        ["cryoEM", "TEM", "SEM"])

    # ------------------------------------------------------------------ H10
    em = df[df["EM"]].copy()
    cry = em["cryoEM"]
    negsem = (em["sub__neg_stain"] | em["SEM"])
    dry = em["TEM"] & em["sub__dried_unstained"] & ~em["sub__neg_stain"] & ~em["cryoEM"] & ~em["sub__pos_stain"]
    tem_nostain = em["TEM"] & ~em["cryoEM"] & ~em["sub__neg_stain"] & ~em["sub__pos_stain"]   # medida alternativa (TEM sin tincion declarada)
    shares = {}
    for f in FAMILY_ORDER:
        s = em["primary_family"] == f
        n = int(s.sum())
        shares[f] = dict(n=n, cryo=cry[s].mean() if n else np.nan, negsem=negsem[s].mean() if n else np.nan, dry=dry[s].mean() if n else np.nan,
                         nostain=tem_nostain[s].mean() if n else np.nan)
    ev = " | ".join(f"{f}(n={v['n']}): cryo={v['cryo']:.2f} negstain|SEM={v['negsem']:.2f} TEM seco sin teñir (explicito)={v['dry']:.2f} "
                    f"TEM sin cryo ni tincion declarada={v['nostain']:.2f}" for f, v in shares.items() if v["n"])
    # H10 compara lipidos, polimeros e inorganicas; AAV queda fuera del alcance de la hipotesis (se muestra en la evidencia)
    valid = {f: v for f, v in shares.items() if v["n"] >= MIN_N and f != "AAV"}
    if not all(f in valid for f in ("LNP", "liposome", "polymeric", "inorganic")):
        v = "inconclusa"
    else:
        a = min(valid["LNP"]["cryo"], valid["liposome"]["cryo"]) > max(valid[f]["cryo"] for f in valid if f not in ("LNP", "liposome"))
        b = valid["polymeric"]["negsem"] > max(valid["LNP"]["negsem"], valid["liposome"]["negsem"])
        c_ = valid["inorganic"]["dry"] == max(valid[f]["dry"] for f in valid)
        v = "confirmada" if a and b and c_ else ("refutada" if not (a or b or c_) else f"parcial (cryo lipidos mayor: {a}; neg-stain/SEM polimeros mayor: {b}; seco sin teñir mayor en inorganicas: {c_})")
    add("H10", v, ev, ["cryoEM", "TEM", "SEM"])

    res = pd.DataFrame(out)
    res.to_csv(DATA / "hypotheses.csv", index=False)
    return res


if __name__ == "__main__":
    pd.set_option("display.max_colwidth", 400, "display.width", 250)
    for _, r in run().iterrows():
        print(f"\n{r['id']}: {r['verdict']}\n   {r['evidence']}\n   {r['caveat']}")
