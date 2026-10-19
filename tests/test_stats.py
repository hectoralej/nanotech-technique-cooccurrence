"""Pruebas de stats.py con datos sinteticos de probabilidades conocidas (brief seccion 10)."""
import math

import numpy as np
import pandas as pd

from src import stats
from src.prec import wilson


def synth(n=40000, pA=0.4, pB_A=0.7, pB_nA=0.2, seed=1):
    rng = np.random.default_rng(seed)
    A = rng.random(n) < pA
    B = np.where(A, rng.random(n) < pB_A, rng.random(n) < pB_nA)
    return A, B


def test_wilson_known_value():
    lo, hi = wilson(50, 100)
    assert abs(lo - 0.4038) < 5e-4 and abs(hi - 0.5962) < 5e-4
    lo, hi = wilson(0, 20)
    assert lo == 0 and abs(hi - 0.1611) < 5e-4


def test_conditional_probability_recovered_and_ci_covers_truth():
    A, B = synth()
    r = stats.pair_stats(A, B)
    assert abs(r["P_B_given_A"] - 0.7) < 0.01
    assert r["ci_lo"] < 0.7 < r["ci_hi"]
    assert abs(r["P_B_given_notA"] - 0.2) < 0.01
    assert abs(r["risk_diff"] - 0.5) < 0.015


def test_or_lift_phi_jaccard_match_theory():
    A, B = synth()
    r = stats.pair_stats(A, B)
    true_or = (0.7 / 0.3) / (0.2 / 0.8)                     # 9.333
    assert r["OR_lo"] < true_or < r["OR_hi"]
    pB = 0.4 * 0.7 + 0.6 * 0.2                               # 0.40
    assert abs(r["lift"] - 0.7 / pB) < 0.03                 # 1.75
    sA, sB = math.sqrt(0.4 * 0.6), math.sqrt(pB * (1 - pB))
    true_phi = (0.4 * 0.7 - 0.4 * pB) / (sA * sB)
    assert abs(r["phi"] - true_phi) < 0.01
    true_j = (0.4 * 0.7) / (0.4 + pB - 0.4 * 0.7)
    assert abs(r["jaccard"] - true_j) < 0.01


def test_haldane_anscombe_with_zero_cell():
    est, lo, hi = stats.or_haldane(10, 0, 5, 20)
    assert np.isfinite(est) and lo > 0 and hi > est


def test_cell_flags_low_n_and_wide_ci():
    rng = np.random.default_rng(0)
    A = np.zeros(500, bool); A[:15] = True
    B = rng.random(500) < 0.5
    r = stats.pair_stats(A, B)
    assert r["low_n"] and r["wide_ci"]
    A2 = np.zeros(500, bool); A2[:300] = True
    assert not stats.pair_stats(A2, B)["low_n"]


def test_benjamini_hochberg_known():
    p = np.array([0.01, 0.04, 0.03, 0.005])
    adj = stats.bh_adjust(p)
    # p ordenados: .005,.01,.03,.04 -> .02,.02,.04,.04
    assert np.allclose(sorted(adj), [0.02, 0.02, 0.04, 0.04])
    assert np.isnan(stats.bh_adjust(np.array([np.nan, 0.01]))[0])


def test_simpson_paradox_mantel_haenszel_recovers_conditional_independence():
    """Dentro de cada familia A y B son independientes, pero ambas son mas prevalentes en la familia 2."""
    rng = np.random.default_rng(3)
    n1, n2 = 20000, 20000
    A1 = rng.random(n1) < 0.1; B1 = rng.random(n1) < 0.1
    A2 = rng.random(n2) < 0.8; B2 = rng.random(n2) < 0.8
    A = np.concatenate([A1, A2]); B = np.concatenate([B1, B2])
    fam = np.array(["f1"] * n1 + ["f2"] * n2)
    crude = stats.pair_stats(A, B)
    assert crude["OR"] > 3                                    # asociacion espuria agregada
    mh = stats.mantel_haenszel(A, B, fam)
    assert mh["MH_lo"] < 1.0 < mh["MH_hi"]                    # estratificada ~ 1
    df = pd.DataFrame({"A": A, "B": B, "primary_family": fam, "year": rng.integers(2018, 2027, n1 + n2),
                       "journal": rng.choice(list("abcdefghij"), n1 + n2)})
    lg = stats.logistic_adjusted(df, "A", "B")
    assert lg["adj_lo"] < 1.0 < lg["adj_hi"]


def test_mantel_haenszel_recovers_common_or():
    rng = np.random.default_rng(5)
    xs, ys, ss = [], [], []
    for s, (pa, p0) in enumerate([(0.3, 0.1), (0.5, 0.3), (0.7, 0.5)]):
        n = 30000
        a = rng.random(n) < pa
        odds0 = p0 / (1 - p0)
        p1 = (4 * odds0) / (1 + 4 * odds0)                    # OR comun = 4
        b = np.where(a, rng.random(n) < p1, rng.random(n) < p0)
        xs.append(a); ys.append(b); ss.append(np.full(n, s))
    mh = stats.mantel_haenszel(np.concatenate(xs), np.concatenate(ys), np.concatenate(ss))
    assert mh["MH_lo"] < 4 < mh["MH_hi"]


def test_cochran_armitage_detects_trend_and_null():
    z, p = stats.cochran_armitage([10, 20, 30, 40], [100, 100, 100, 100])
    assert z > 0 and p < 1e-6
    z0, p0 = stats.cochran_armitage([25, 25, 25, 25], [100, 100, 100, 100])
    assert abs(z0) < 1e-9 and p0 > 0.99


def test_rogan_gladen():
    # prevalencia real 0.3, sens 0.9, spec 0.95 -> observada 0.3*0.9 + 0.7*0.05 = 0.305
    assert abs(stats.rogan_gladen(0.305, 0.9, 0.95) - 0.3) < 1e-9
    assert math.isnan(stats.rogan_gladen(0.3, 0.5, 0.4))


def test_frequent_itemsets_and_next_given_combo_exact():
    X = np.zeros((100, 3), bool)
    X[:60, 0] = True                       # A en 60
    X[:40, 1] = True                       # B en 40, todos con A
    X[:10, 2] = True                       # C en 10, todos con A y B
    names = ["A", "B", "C"]
    fi = stats.frequent_itemsets(X, names, min_support=0.05)
    sup = dict(zip(fi["itemset"], fi["support"]))
    assert sup["{A}"] == 0.6 and sup["{A, B}"] == 0.4 and sup["{A, B, C}"] == 0.1
    nx = stats.next_given_combo(X, names, ["A", "B"]).set_index("next")
    assert nx.loc["C", "k"] == 10 and nx.loc["C", "n_combo"] == 40 and abs(nx.loc["C", "P"] - 0.25) < 1e-12
    ep = stats.exact_patterns(X, names)
    assert int(ep[ep["pattern"] == ("A",)]["count"].iloc[0]) == 20


def test_cluster_order_groups_correlated_columns():
    rng = np.random.default_rng(0)
    base1 = rng.random(2000) < 0.5
    base2 = rng.random(2000) < 0.5
    flip = lambda x: x ^ (rng.random(2000) < 0.05)           # noqa: E731
    X = np.column_stack([base1, base2, flip(base1), flip(base2)])
    order = stats.cluster_order(X)
    pos = {c: i for i, c in enumerate(order)}
    assert abs(pos[0] - pos[2]) == 1 and abs(pos[1] - pos[3]) == 1


def test_pair_table_asymmetric_and_diagonal_excluded():
    A, B = synth(n=5000)
    X = np.column_stack([A, B])
    t = stats.pair_table(X, ["A", "B"], "ALL")
    assert len(t) == 2 and set(zip(t.A, t.B)) == {("A", "B"), ("B", "A")}
    ab = t[(t.A == "A")].iloc[0]; ba = t[(t.A == "B")].iloc[0]
    assert ab["P_B_given_A"] != ba["P_B_given_A"]            # la matriz NO es simetrica
    assert abs(ab["phi"] - ba["phi"]) < 1e-12                # phi si lo es
