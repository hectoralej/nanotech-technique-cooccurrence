"""Intervalos de Wilson y criterio de parada de precision (brief 4.3)."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.stats import norm


def wilson(k: float, n: float, conf: float = 0.95) -> tuple[float, float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    z = norm.ppf(1 - (1 - conf) / 2)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def median_halfwidth(df: pd.DataFrame, techs: list[str], min_nA: int = 30) -> tuple[float, int]:
    """Mitad de ancho mediana del IC95 % de P(B|A) sobre pares (A,B) con n(A) >= min_nA.

    df: una fila por articulo, columnas binarias por tecnica. Devuelve (mediana, numero de celdas).
    """
    X = df[techs].to_numpy(dtype=bool)
    widths = []
    for i, _a in enumerate(techs):
        nA = int(X[:, i].sum())
        if nA < min_nA:
            continue
        for j, _b in enumerate(techs):
            if i == j:
                continue
            k = int((X[:, i] & X[:, j]).sum())
            lo, hi = wilson(k, nA)
            widths.append((hi - lo) / 2)
    if not widths:
        return (float("nan"), 0)
    return (float(np.median(widths)), len(widths))
