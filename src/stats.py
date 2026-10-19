"""Analisis estadistico de co-ocurrencia (brief seccion 5).

Convenciones: X es una matriz booleana [N articulos x k tecnicas]; la fila de la matriz es la condicion A y la
columna el resultado B. Todas las funciones puras (sin E/S) estan cubiertas por tests/test_stats.py con datos
sinteticos de probabilidades conocidas.
"""
from __future__ import annotations

import itertools
import math
import warnings

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform
from scipy.stats import fisher_exact, norm

from .prec import wilson

MIN_NA_SHOWN = 20          # n(A) < 20 -> celda atenuada y rotulada (brief 5.7)
WIDE_CI = 0.30             # IC > 0.3 de ancho -> senalado


# ----------------------------------------------------------------------------------------------
# Tabla 2x2 y medidas de asociacion
# ----------------------------------------------------------------------------------------------

def or_haldane(a: float, b: float, c: float, d: float, conf: float = 0.95) -> tuple[float, float, float]:
    """OR con IC de Woolf; Haldane-Anscombe (+0.5 en todas las celdas) cuando alguna celda es 0."""
    if min(a, b, c, d) == 0:
        a, b, c, d = a + .5, b + .5, c + .5, d + .5
    est = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    z = norm.ppf(1 - (1 - conf) / 2)
    return est, math.exp(math.log(est) - z * se), math.exp(math.log(est) + z * se)


def phi_coef(a: int, b: int, c: int, d: int) -> float:
    den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return float("nan") if den == 0 else (a * d - b * c) / den


def pair_stats(xa: np.ndarray, xb: np.ndarray) -> dict:
    """Todas las medidas para el par ordenado (A=xa, B=xb)."""
    N = len(xa)
    a = int((xa & xb).sum())            # A y B
    b = int((xa & ~xb).sum())           # A, no B
    c = int((~xa & xb).sum())           # no A, B
    d = int((~xa & ~xb).sum())
    nA, nB, nnA = a + b, a + c, c + d
    pBA = a / nA if nA else float("nan")
    lo, hi = wilson(a, nA) if nA else (float("nan"),) * 2
    pBnA = c / nnA if nnA else float("nan")
    orr, orlo, orhi = or_haldane(a, b, c, d) if min(nA, nnA) > 0 and (a + c) > 0 and (b + d) > 0 else (float("nan"),) * 3
    pB = nB / N if N else float("nan")
    p_fisher = fisher_exact([[a, b], [c, d]])[1] if min(nA, nnA) > 0 else float("nan")
    return dict(N=N, nA=nA, nB=nB, nAB=a, P_B_given_A=pBA, ci_lo=lo, ci_hi=hi, ci_halfwidth=(hi - lo) / 2 if nA else float("nan"),
                P_B_given_notA=pBnA, risk_diff=pBA - pBnA if nA and nnA else float("nan"),
                OR=orr, OR_lo=orlo, OR_hi=orhi,
                lift=(pBA / pB) if pB and nA else float("nan"),
                phi=phi_coef(a, b, c, d), jaccard=a / (a + b + c) if (a + b + c) else float("nan"),
                p_fisher=p_fisher, low_n=nA < MIN_NA_SHOWN, wide_ci=bool(nA and (hi - lo) > WIDE_CI))


def bh_adjust(p: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg (FDR). NaN se conserva."""
    p = np.asarray(p, dtype=float)
    out = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    if ok.sum() == 0:
        return out
    pv = p[ok]
    n = len(pv)
    order = np.argsort(pv)
    ranked = pv[order] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(n)
    adj[order] = np.minimum(ranked, 1.0)
    out[ok] = adj
    return out


def pair_table(X: np.ndarray, names: list[str], stratum: str) -> pd.DataFrame:
    rows = []
    for i, A in enumerate(names):
        for j, B in enumerate(names):
            if i == j:
                continue
            r = pair_stats(X[:, i], X[:, j])
            r.update(stratum=stratum, A=A, B=B)
            rows.append(r)
    df = pd.DataFrame(rows)
    df["p_adj_bh"] = bh_adjust(df["p_fisher"].to_numpy())
    return df


# ----------------------------------------------------------------------------------------------
# Estratificacion: Mantel-Haenszel y regresion logistica con errores robustos por revista
# ----------------------------------------------------------------------------------------------

def mantel_haenszel(xa: np.ndarray, xb: np.ndarray, strata: np.ndarray) -> dict:
    from statsmodels.stats.contingency_tables import StratifiedTable
    tables = []
    for s in pd.unique(strata):
        m = strata == s
        a = int((xa[m] & xb[m]).sum()); b = int((xa[m] & ~xb[m]).sum())
        c = int((~xa[m] & xb[m]).sum()); d = int((~xa[m] & ~xb[m]).sum())
        if (a + b) > 0 and (c + d) > 0 and (a + c) > 0 and (b + d) > 0:   # estrato informativo
            tables.append(np.array([[a, b], [c, d]]))
    out = dict(MH_OR=float("nan"), MH_lo=float("nan"), MH_hi=float("nan"), MH_p=float("nan"), MH_strata=len(tables))
    if not tables:
        return out
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            st = StratifiedTable(tables)
            lo, hi = st.oddsratio_pooled_confint()
            out.update(MH_OR=float(st.oddsratio_pooled), MH_lo=float(lo), MH_hi=float(hi), MH_p=float(st.test_null_odds().pvalue))
    except Exception:  # noqa: BLE001 - tabla degenerada
        pass
    return out


def logistic_adjusted(df: pd.DataFrame, A: str, B: str, family_col="primary_family", year_col="year", cluster_col="journal") -> dict:
    """B ~ A + familia + ano (centrado), SE robustos agrupados por revista."""
    import statsmodels.api as sm
    out = dict(adj_OR=float("nan"), adj_lo=float("nan"), adj_hi=float("nan"), adj_p=float("nan"), adj_n_clusters=0)
    y = df[B].astype(int).to_numpy()
    a = df[A].astype(int).to_numpy()
    if y.min() == y.max() or a.min() == a.max():
        return out
    fam = pd.get_dummies(df[family_col], drop_first=True, dtype=float)
    X = pd.concat([pd.Series(a, index=df.index, name="A", dtype=float), fam,
                   (df[year_col].astype(float) - df[year_col].astype(float).mean()).rename("year_c")], axis=1)
    X = sm.add_constant(X, has_constant="add")
    groups = pd.factorize(df[cluster_col].fillna("NA"))[0]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = sm.GLM(y, X, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": groups})
        b, se = res.params["A"], res.bse["A"]
        if not np.isfinite(b) or not np.isfinite(se) or abs(b) > 15:     # separacion casi perfecta
            return out
        z = norm.ppf(0.975)
        out.update(adj_OR=math.exp(b), adj_lo=math.exp(b - z * se), adj_hi=math.exp(b + z * se),
                   adj_p=float(res.pvalues["A"]), adj_n_clusters=int(len(set(groups))))
    except Exception:  # noqa: BLE001
        pass
    return out


# ----------------------------------------------------------------------------------------------
# Orden por agrupamiento jerarquico, tendencias, correccion de detector
# ----------------------------------------------------------------------------------------------

def phi_matrix(X: np.ndarray) -> np.ndarray:
    k = X.shape[1]
    M = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            if i == j:
                M[i, j] = 1.0
                continue
            xa, xb = X[:, i], X[:, j]
            v = phi_coef(int((xa & xb).sum()), int((xa & ~xb).sum()), int((~xa & xb).sum()), int((~xa & ~xb).sum()))
            M[i, j] = 0.0 if v != v else v
    return M


def cluster_order(X: np.ndarray) -> list[int]:
    """Orden de las columnas por clustering jerarquico (enlace promedio) sobre 1 - phi."""
    k = X.shape[1]
    if k < 3:
        return list(range(k))
    D = 1 - phi_matrix(X)
    D = np.clip((D + D.T) / 2, 0, None)
    np.fill_diagonal(D, 0)
    return [int(i) for i in leaves_list(linkage(squareform(D, checks=False), method="average"))]


def cochran_armitage(x: np.ndarray, n: np.ndarray, scores: np.ndarray | None = None) -> tuple[float, float]:
    """Prueba de tendencia de Cochran-Armitage (bilateral). x: exitos por nivel, n: totales. Devuelve (Z, p)."""
    x, n = np.asarray(x, float), np.asarray(n, float)
    t = np.arange(len(x), dtype=float) if scores is None else np.asarray(scores, float)
    N, R = n.sum(), x.sum()
    p = R / N
    if p in (0, 1) or len(x) < 2:
        return float("nan"), float("nan")
    T = np.sum(t * (x - n * p))
    var = p * (1 - p) * (np.sum(n * t ** 2) - np.sum(n * t) ** 2 / N)
    if var <= 0:
        return float("nan"), float("nan")
    z = T / math.sqrt(var)
    return float(z), float(2 * (1 - norm.cdf(abs(z))))


def rogan_gladen(p_obs: float, sens: float, spec: float) -> float:
    den = sens + spec - 1
    if den <= 0:
        return float("nan")
    return float(min(1.0, max(0.0, (p_obs + spec - 1) / den)))


# ----------------------------------------------------------------------------------------------
# Combinaciones: reglas de asociacion (Apriori) y patrones exactos para UpSet
# ----------------------------------------------------------------------------------------------

def frequent_itemsets(X: np.ndarray, names: list[str], min_support: float = 0.05, max_size: int = 5) -> pd.DataFrame:
    N = X.shape[0]
    min_count = max(1, math.ceil(min_support * N))
    cols = {i: X[:, i] for i in range(X.shape[1])}
    level = {(i,): int(col.sum()) for i, col in cols.items() if col.sum() >= min_count}
    allsets = dict(level)
    size = 1
    while level and size < max_size:
        keys = sorted(level)
        cand = set()
        for s1, s2 in itertools.combinations(keys, 2):
            if s1[:-1] == s2[:-1]:
                u = tuple(sorted(set(s1) | set(s2)))
                if all(tuple(sorted(set(u) - {x})) in level for x in u):
                    cand.add(u)
        nxt = {}
        for u in cand:
            cnt = int(np.logical_and.reduce([cols[i] for i in u]).sum())
            if cnt >= min_count:
                nxt[u] = cnt
        allsets.update(nxt)
        level = nxt
        size += 1
    rows = [dict(itemset="{" + ", ".join(names[i] for i in s) + "}", size=len(s), count=c, support=c / N)
            for s, c in allsets.items()]
    return pd.DataFrame(rows).sort_values(["support", "size"], ascending=[False, False]).reset_index(drop=True) if rows \
        else pd.DataFrame(columns=["itemset", "size", "count", "support"])


def next_given_combo(X: np.ndarray, names: list[str], combo: list[str]) -> pd.DataFrame:
    idx = [names.index(c) for c in combo]
    has = np.logical_and.reduce([X[:, i] for i in idx])
    n = int(has.sum())
    rows = []
    for j, t in enumerate(names):
        if j in idx:
            continue
        k = int((has & X[:, j]).sum())
        lo, hi = wilson(k, n) if n else (float("nan"),) * 2
        rows.append(dict(combo="{" + ", ".join(combo) + "}", n_combo=n, next=t, k=k, P=k / n if n else float("nan"), ci_lo=lo, ci_hi=hi))
    return pd.DataFrame(rows).sort_values("P", ascending=False)


def exact_patterns(X: np.ndarray, names: list[str]) -> pd.DataFrame:
    """Conteo de patrones exactos (combinacion de tecnicas presentes) para UpSet."""
    pats = pd.Series([tuple(np.flatnonzero(r)) for r in X]).value_counts()
    rows = [dict(pattern=tuple(names[i] for i in p), size=len(p), count=int(c), share=c / len(X)) for p, c in pats.items() if len(p) > 0]
    return pd.DataFrame(rows)
