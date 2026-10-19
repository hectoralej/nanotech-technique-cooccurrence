"""Muestreo aleatorio estratificado y reproducible.

Dentro de cada familia primaria, los articulos se ordenan de forma que *cualquier prefijo* de la lista sea una
muestra estratificada proporcional (familia x periodo x grupo de licencia): se permuta cada estrato con la
semilla fija y se ordena por (posicion + 0.5) / tamano_del_estrato. Asi el piloto (primeros 30) es parte de la
muestra final y el muestreo puede detenerse en cualquier punto (criterio de parada, brief 4.3).
"""
from __future__ import annotations

import zlib

import numpy as np
import pandas as pd

from .common import DATA, load_yaml


def family_rng(seed: int, family: str, salt: int = 0) -> np.random.Generator:
    return np.random.default_rng([seed, zlib.crc32(family.encode()), salt])


def build_order() -> pd.DataFrame:
    samp = load_yaml("sampling.yaml")
    uni = pd.read_csv(DATA / "ids" / "universe.csv", dtype={"pmcid": str, "year": "Int64"})
    uni = uni[uni["eligible"] & ~uni["is_review_flag"]].copy()
    parts = []
    main_periods = ["main_early", "main_late"]
    for fam, g in uni.groupby("primary_family", sort=True):
        rng = family_rng(samp["seed"], fam)       # una semilla por familia: cambiar una no altera las demas
        main = g[g["period"].isin(main_periods)].copy()
        main["stratum"] = main["period"] + "|" + main["license_group"]
        main = main.sort_values("pmcid")                       # orden de entrada determinista
        scores = np.empty(len(main))
        idx_all = np.arange(len(main))
        strata = main["stratum"].to_numpy()
        for s in np.unique(strata):
            idx = idx_all[strata == s]
            perm = rng.permutation(len(idx))
            scores[idx[perm]] = (np.arange(len(idx)) + 0.5) / len(idx)
        main["N_stratum"] = main.groupby("stratum")["pmcid"].transform("size")
        main["score"] = scores + rng.random(len(main)) * 1e-9  # desempate
        main = main.sort_values("score")
        main["rank_in_family"] = np.arange(1, len(main) + 1)
        main["analysis_set"] = "main"
        parts.append(main)

        trend = g[g["period"] == "trend_only"].copy().sort_values("pmcid")
        if len(trend):
            trend["stratum"] = "trend_only|" + trend["license_group"]
            trend["N_stratum"] = trend.groupby("stratum")["pmcid"].transform("size")
            pick = rng.permutation(len(trend))[: samp["trend_only_per_family"]]
            trend = trend.iloc[sorted(pick)].copy()
            trend["score"] = np.nan
            trend["rank_in_family"] = np.arange(1, len(trend) + 1)
            trend["analysis_set"] = "trend_only"
            parts.append(trend)
    order = pd.concat(parts, ignore_index=True)
    keep = ["pmcid", "pmid", "doi", "year", "journal", "license", "license_group", "period", "primary_family", "subtype",
            "families_matched", "title", "pub_types", "stratum", "N_stratum", "rank_in_family", "analysis_set"]
    return order[keep]


def main() -> None:
    order = build_order()
    order.to_csv(DATA / "ids" / "sample_order.csv", index=False)
    print(order.groupby(["primary_family", "analysis_set"]).size())


if __name__ == "__main__":
    main()
