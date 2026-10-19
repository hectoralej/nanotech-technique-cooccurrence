"""Carga del analisis: articulos en alcance con columnas binarias segun la definicion de 'tecnica reportada'."""
from __future__ import annotations

import pandas as pd

from .common import DATA, load_yaml
from .detect import technique_names

ARTICLES_ALL = DATA / "articles_all.csv"
ORGANIC = ["liposome", "LNP", "SLN_NLC", "PLN", "polymeric"]
FAMILY_ORDER = ["LNP", "liposome", "SLN_NLC", "PLN", "polymeric", "inorganic", "AAV"]
MICRO = ["cryoEM", "TEM", "STEM", "SEM", "AFM"]


def flag_def(art: pd.DataFrame, t: str, which: str) -> pd.Series:
    """'Tecnica reportada' desde las banderas por seccion (m, r, c = metodos/resultados/pie; o = otras; a = resumen)."""
    m, r, c, o, a = (art[f"{t}__{k}"].astype(bool) for k in "mrcoa")
    return {"primary": m & (r | c), "body_any": m | r | c, "methods_only": m, "caption_only": c,
            "any": m | r | c | o | a}[which]


def load_articles(definition: str | None = None, analysis_set: str | None = "main", only_in_scope: bool = True) -> pd.DataFrame:
    """Una fila por articulo, una columna booleana por tecnica (segun `definition`; por defecto la principal)."""
    definition = definition or load_yaml("sampling.yaml")["headline_definition"]
    art = pd.read_csv(ARTICLES_ALL, dtype={"pmcid": str}, low_memory=False)
    if only_in_scope:
        art = art[art["in_scope"].astype(bool)]
    if analysis_set:
        art = art[art["analysis_set"] == analysis_set]
    art = art.reset_index(drop=True)
    bin_cols = {t: flag_def(art, t, definition) for t in technique_names()}
    out = art.copy()
    for t, s in bin_cols.items():
        out[t] = s.to_numpy()
    sub = [c for c in out.columns if c.startswith("sub__")]
    for c in sub:
        out[c] = out[c].fillna(False).astype(bool)
    out["year"] = out["year"].astype(int)
    out["EM"] = out[MICRO].any(axis=1)
    out.attrs["definition"] = definition
    return out


def reliability_table(definition: str | None = None) -> pd.DataFrame:
    """Fiabilidad por tecnica a partir de data/gold_metrics.csv (definicion indicada)."""
    definition = definition or load_yaml("sampling.yaml")["headline_definition"]
    path = DATA / "gold_metrics.csv"
    techs = technique_names()
    base = pd.DataFrame({"technique": techs})
    if not path.exists():
        base["reliability"] = "unvalidated"
        return base
    g = pd.read_csv(path)
    g = g[g["definition"] == definition].set_index("technique")
    rows = []
    for t in techs:
        if t not in g.index or g.loc[t, "n_true"] < 3:
            rows.append(dict(technique=t, reliability="unvalidated", n_true=int(g.loc[t, "n_true"]) if t in g.index else 0,
                             recall=float("nan"), precision=float("nan")))
            continue
        rec, prec = g.loc[t, "recall"], g.loc[t, "precision"]
        flag = "recall_low" if rec < 0.85 else ("precision_low" if prec < 0.80 else "ok")
        rows.append(dict(technique=t, reliability=flag, n_true=int(g.loc[t, "n_true"]), recall=rec, precision=prec))
    return pd.DataFrame(rows)
