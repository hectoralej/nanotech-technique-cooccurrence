"""Orquestador del analisis (brief seccion 5). Escribe en data/:

  articles.csv            articulos de la muestra principal en alcance (una columna binaria por tecnica)
  pairs.csv               pares ordenados (A,B) x estrato, definicion principal
  pairs_sensitivity.csv   los mismos pares bajo las definiciones/escenarios de sensibilidad
  sensitivity_summary.csv que conclusiones cambian
  prevalence.csv          prevalencia marginal con IC, por familia, y ajuste de Rogan-Gladen
  itemsets.csv, next_given_combo.csv, patterns.csv   combinaciones (Apriori y patrones exactos para UpSet)
  trend.csv               prevalencia por ano y prueba de Cochran-Armitage
  em_row.csv              fila 'EM' resumida por familia (figura 6)
  cell_pmcids/<estrato>.csv   PMCID de cada celda A&B
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from . import stats
from .common import DATA, load_yaml
from .data import FAMILY_ORDER, MICRO, ORGANIC, flag_def, load_articles, reliability_table
from .detect import DEFINITIONS, technique_names
from .prec import wilson

MIN_TECH_N = 20            # una tecnica entra en la matriz si tiene >= 20 articulos en la muestra principal
SPECTRA = ["UVVis", "FTIR", "XRD", "NMR", "EDS", "SAXS", "Raman_SERS", "XPS"]


def strata_masks(df: pd.DataFrame) -> dict[str, np.ndarray]:
    m = {"ALL": np.ones(len(df), bool), "ORGANIC": df["primary_family"].isin(ORGANIC).to_numpy()}
    for f in FAMILY_ORDER:
        m[f] = (df["primary_family"] == f).to_numpy()
    return m


def matrix_techniques(df: pd.DataFrame) -> list[str]:
    return [t for t in technique_names() if int(df[t].sum()) >= MIN_TECH_N and int((~df[t]).sum()) >= MIN_TECH_N]


def build_pairs(df: pd.DataFrame, techs: list[str], with_adjusted: bool, definition: str, scenario: str = "headline") -> pd.DataFrame:
    X = df[techs].to_numpy(dtype=bool)
    parts = []
    for name, mask in strata_masks(df).items():
        if mask.sum() < 10:
            continue
        t = stats.pair_table(X[mask], techs, name)
        parts.append(t)
    pairs = pd.concat(parts, ignore_index=True)
    # estratificado (solo ALL): MH por familia primaria y regresion logistica con SE robustos por revista
    mh_rows = []
    fam = df["primary_family"].to_numpy()
    for i, A in enumerate(techs):
        for j, B in enumerate(techs):
            if i == j:
                continue
            row = dict(stratum="ALL", A=A, B=B, **stats.mantel_haenszel(X[:, i], X[:, j], fam))
            if with_adjusted:
                row.update(stats.logistic_adjusted(df, A, B))
            mh_rows.append(row)
    mh = pd.DataFrame(mh_rows)
    mh["MH_p_adj"] = stats.bh_adjust(mh["MH_p"].to_numpy())
    if with_adjusted:
        mh["adj_p_adj"] = stats.bh_adjust(mh["adj_p"].to_numpy())
    pairs = pairs.merge(mh, on=["stratum", "A", "B"], how="left")
    rel = reliability_table(definition).set_index("technique")["reliability"]
    pairs["A_reliability"] = pairs["A"].map(rel)
    pairs["B_reliability"] = pairs["B"].map(rel)
    pairs.insert(0, "definition", definition)
    pairs.insert(1, "scenario", scenario)
    return pairs


def cell_pmcids(df: pd.DataFrame, techs: list[str]) -> None:
    out = DATA / "cell_pmcids"
    out.mkdir(exist_ok=True)
    X = df[techs].to_numpy(dtype=bool)
    ids = df["pmcid"].to_numpy()
    for name, mask in strata_masks(df).items():
        rows = []
        for i, A in enumerate(techs):
            for j in range(i + 1, len(techs)):
                both = mask & X[:, i] & X[:, j]
                if both.any():
                    rows.append(dict(A=A, B=techs[j], n=int(both.sum()), pmcids="|".join(ids[both])))
        pd.DataFrame(rows).to_csv(out / f"{name}.csv", index=False)


def prevalence_table(df: pd.DataFrame, techs: list[str]) -> pd.DataFrame:
    gm = DATA / "gold_metrics.csv"
    sens_spec = {}
    if gm.exists():
        g = pd.read_csv(gm)
        g = g[g["definition"] == df.attrs["definition"]].set_index("technique")
        for t in g.index:
            if g.loc[t, "n_true"] >= 3:
                sens_spec[t] = (g.loc[t, "sensitivity"], g.loc[t, "specificity"])
    rows = []
    for name, mask in strata_masks(df).items():
        sub = df[mask]
        for t in techs:
            k, n = int(sub[t].sum()), len(sub)
            lo, hi = wilson(k, n) if n else (np.nan, np.nan)
            rg = np.nan
            if t in sens_spec and n:
                rg = stats.rogan_gladen(k / n, *sens_spec[t])
            rows.append(dict(stratum=name, technique=t, n=n, k=k, prevalence=k / n if n else np.nan, ci_lo=lo, ci_hi=hi,
                             prevalence_rogan_gladen=rg))
    return pd.DataFrame(rows)


def combos(df: pd.DataFrame, techs: list[str], min_support: float = 0.05, top: int = 15):
    its, nxt, pats = [], [], []
    for name, mask in strata_masks(df).items():
        if mask.sum() < 30:
            continue
        sub = df[mask]
        # solo tecnicas con soporte suficiente dentro del estrato
        use = [t for t in techs if sub[t].mean() >= min_support]
        if len(use) < 2:
            continue
        X = sub[use].to_numpy(dtype=bool)
        fi = stats.frequent_itemsets(X, use, min_support)
        fi2 = fi[fi["size"] >= 2].head(top).copy()
        fi2.insert(0, "stratum", name)
        its.append(fi2)
        for s in fi2["itemset"]:
            combo = [x.strip() for x in s.strip("{}").split(",")]
            n = stats.next_given_combo(sub[techs].to_numpy(dtype=bool), techs, combo)
            n.insert(0, "stratum", name)
            nxt.append(n)
        ep = stats.exact_patterns(sub[use].to_numpy(dtype=bool), use).head(top)
        ep.insert(0, "stratum", name)
        ep["pattern"] = ep["pattern"].map(lambda p: " + ".join(p))
        pats.append(ep)
    cat = lambda xs: pd.concat(xs, ignore_index=True) if xs else pd.DataFrame()   # noqa: E731
    return cat(its), cat(nxt), cat(pats)


def trend_table(definition: str, techs: list[str]) -> pd.DataFrame:
    full = pd.concat([load_articles(definition, "main"), load_articles(definition, "trend_only")], ignore_index=True)
    top8 = full[techs].mean().sort_values(ascending=False).head(8).index.tolist()
    rows = []
    for t in top8:
        yrs = sorted(full["year"].unique())
        x = np.array([full.loc[full.year == y, t].sum() for y in yrs])
        n = np.array([(full.year == y).sum() for y in yrs])
        z, p = stats.cochran_armitage(x, n, scores=np.array(yrs, float))
        for y, xi, ni in zip(yrs, x, n):
            lo, hi = wilson(xi, ni) if ni else (np.nan, np.nan)
            rows.append(dict(technique=t, year=int(y), n=int(ni), k=int(xi), prevalence=xi / ni if ni else np.nan,
                             ci_lo=lo, ci_hi=hi, CA_z=z, CA_p=p))
    return pd.DataFrame(rows)


def em_row(df: pd.DataFrame, techs: list[str]) -> pd.DataFrame:
    """Fila 'EM' resumida: dado que el articulo tiene micrografia (cualquier microscopia), P(tecnica|EM) por familia."""
    rows = []
    for name, mask in strata_masks(df).items():
        sub = df[mask & df["EM"].to_numpy()]
        n = len(sub)
        for t in techs:
            if t in MICRO:
                continue
            k = int(sub[t].sum()); lo, hi = wilson(k, n) if n else (np.nan, np.nan)
            rows.append(dict(stratum=name, what=t, n_EM=n, k=k, P=k / n if n else np.nan, ci_lo=lo, ci_hi=hi))
        k = int(sub["figms_any"].sum()); lo, hi = wilson(k, n) if n else (np.nan, np.nan)
        rows.append(dict(stratum=name, what="micrograph+spectrum_same_figure", n_EM=n, k=k, P=k / n if n else np.nan, ci_lo=lo, ci_hi=hi))
        for s in SPECTRA:
            k = int(sub["figms_techs"].fillna("").str.contains(rf"(?:^|\|){s}(?:\||$)").sum())
            lo, hi = wilson(k, n) if n else (np.nan, np.nan)
            rows.append(dict(stratum=name, what=f"same_figure:{s}", n_EM=n, k=k, P=k / n if n else np.nan, ci_lo=lo, ci_hi=hi))
    return pd.DataFrame(rows)


def sensitivity(headline: str, techs: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Repite pares bajo definiciones y escenarios. Devuelve (largo, resumen de que cambia)."""
    base = load_articles(headline)
    rel = reliability_table(headline)
    reliable = rel.loc[rel["reliability"].isin(["ok", "precision_low"]), "technique"].tolist()
    runs = []
    for d in DEFINITIONS:
        if d == headline:
            continue
        runs.append((f"def:{d}", d, load_articles(d), techs))
    runs.append(("cc_by_only", headline, base[base["license_group"] == "cc_by"].reset_index(drop=True), techs))
    # duplicacion de articulos multietiqueta: cada articulo cuenta en cada familia coincidente
    dup = []
    for fam in FAMILY_ORDER:
        sub = base[base["families_matched"].fillna("").str.split("|").map(lambda l: fam in l)].copy()
        sub["primary_family"] = fam
        dup.append(sub)
    runs.append(("multilabel_duplicated", headline, pd.concat(dup, ignore_index=True), techs))
    runs.append(("reliable_techniques_only", headline, base, [t for t in techs if t in reliable]))
    long = []
    for scen, d, df_, tt in runs:
        tt = [t for t in tt if int(df_[t].sum()) >= MIN_TECH_N and int((~df_[t]).sum()) >= MIN_TECH_N]
        if len(tt) < 2:
            continue
        p = build_pairs(df_, tt, with_adjusted=False, definition=d, scenario=scen)
        long.append(p)
    long = pd.concat(long, ignore_index=True)
    # resumen: para cada escenario, comparar con el titular en ALL (misma direccion de log-lift y misma significancia FDR)
    head = build_pairs(base, techs, with_adjusted=False, definition=headline, scenario="headline")
    hb = head[head.stratum == "ALL"].set_index(["A", "B"])
    summ = []
    for scen, g in long[long.stratum == "ALL"].groupby("scenario"):
        g = g.set_index(["A", "B"])
        common = g.index.intersection(hb.index)
        if not len(common):
            continue
        h, s = hb.loc[common], g.loc[common]
        sign_same = (np.sign(np.log(h["lift"])) == np.sign(np.log(s["lift"]))).mean()
        sig_h = (h["p_adj_bh"] < 0.05); sig_s = (s["p_adj_bh"] < 0.05)
        both_eval = (~h["low_n"]) & (~s["low_n"])
        ok = both_eval & h["P_B_given_A"].notna() & s["P_B_given_A"].notna()
        rho = np.corrcoef(h.loc[ok, "P_B_given_A"], s.loc[ok, "P_B_given_A"])[0, 1] if ok.sum() > 3 else np.nan
        flips = [f"{a}->{b}" for (a, b), f in (sig_h != sig_s)[ok].items() if f][:40]
        summ.append(dict(scenario=scen, n_pairs=len(common), pearson_P_B_given_A=rho, direction_agreement=sign_same,
                         n_fdr_significance_changes=int((sig_h != sig_s)[ok].sum()), examples_changed="; ".join(flips)))
    return long, pd.DataFrame(summ)


def main() -> None:
    headline = load_yaml("sampling.yaml")["headline_definition"]
    df = load_articles(headline)
    techs = matrix_techniques(df)
    print(f"articulos en alcance (muestra principal): {len(df)}; tecnicas en la matriz: {len(techs)}", flush=True)
    keep = ["pmcid", "pmid", "doi", "year", "journal", "license", "license_group", "period", "primary_family", "subtype",
            "families_matched", "stratum", "N_stratum", "rank_in_family", "title", "article_type", "has_methods",
            "has_results", "n_captions", "figms_any", "figms_techs"]
    cols = keep + technique_names() + [c for c in df.columns if c.startswith("sub__")]
    df[cols].to_csv(DATA / "articles.csv", index=False)
    pairs = build_pairs(df, techs, with_adjusted=True, definition=headline)
    pairs.to_csv(DATA / "pairs.csv", index=False)
    cell_pmcids(df, techs)
    prevalence_table(df, technique_names()).to_csv(DATA / "prevalence.csv", index=False)
    its, nxt, pats = combos(df, techs)
    its.to_csv(DATA / "itemsets.csv", index=False); nxt.to_csv(DATA / "next_given_combo.csv", index=False); pats.to_csv(DATA / "patterns.csv", index=False)
    trend_table(headline, techs).to_csv(DATA / "trend.csv", index=False)
    em_row(df, technique_names()).to_csv(DATA / "em_row.csv", index=False)
    long, summ = sensitivity(headline, techs)
    long.to_csv(DATA / "pairs_sensitivity.csv", index=False)
    summ.to_csv(DATA / "sensitivity_summary.csv", index=False)
    (DATA / "analysis_meta.json").write_text(json.dumps(
        dict(definition=headline, n_articles=len(df), techniques_in_matrix=techs,
             by_family=df["primary_family"].value_counts().to_dict()), indent=1), encoding="utf-8")
    print("listo")


if __name__ == "__main__":
    main()
