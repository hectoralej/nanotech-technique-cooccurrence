"""OOF regression ladder on log10(size), using only the official article folds."""
from __future__ import annotations

import argparse
import json

from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge

from tabular_data import RESULTS, load_dataset, save_json
from tabular_common import N_JOBS, checkpoint, evaluate


def run(baselines_only=False):
    data = load_dataset()
    data = data[data.size_nm.notna()].copy()
    global_mean = evaluate("tamano_dummy", "Media global (Dummy)", data, "regresion", "A/B", DummyRegressor(strategy="mean"), baseline="global", permutation=False)
    class_mean = evaluate("tamano_media_clase", "Media por clase", data, "regresion", "A/B", baseline="class_mean", permutation=False)
    dummy_r2 = global_mean["metricas"]["r2"]["valor"]
    class_r2 = class_mean["metricas"]["r2"]["valor"]
    assert -.1 < dummy_r2 <= .001, f"Dummy inesperado: {dummy_r2}"
    difference = class_r2 - .18
    explanation = (
        f"Media global OOF R²={dummy_r2:.4f}; media por clase OOF R²={class_r2:.4f}; diferencia frente a 0,18={difference:+.4f}. "
        "La comparación usa filas descriptor individuales, cinco folds oficiales por artículo, media de log10(tamaño) calculada solo con entrenamiento y filtros 1–5000 nm. "
        "El valor previo 0,18 es aproximado y no incluye sus predicciones ni su partición de origen; por ello la igualdad exacta no es comprobable. "
        + ("La magnitud reproduce el piso comunicado." if abs(difference) <= .06 else "La diferencia queda explicada por el protocolo actual y la ausencia de partición/protocolo reproducible del valor previo; no se atribuye una causa concreta sin evidencia.")
    )
    save_json(RESULTS / "validacion_2.json", {"dummy_r2": dummy_r2, "media_clase_r2": class_r2, "referencia_r2": .18, "diferencia": difference, "explicacion": explanation, "estado": "PASS" if abs(difference) <= .06 else "DIFERENCIA_DOCUMENTADA"})
    checkpoint("validacion_2_antes_de_modelos", {"explicacion": explanation})
    if baselines_only:
        return
    for variant in ("A", "B"):
        models = [
            ("lineal", "Lineal múltiple", LinearRegression(), False, False),
            ("ridge", "Ridge (alpha interno)", Ridge(), True, True),
            ("rf300", "RF 300 / hoja 3", RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=N_JOBS), False, True),
            ("rf500", "RF 500 / hoja 1", RandomForestRegressor(n_estimators=500, min_samples_leaf=1, random_state=0, n_jobs=N_JOBS), False, False),
            ("hgb", "HistGradientBoosting", HistGradientBoostingRegressor(max_iter=300, learning_rate=.05, random_state=0, early_stopping=False), False, True),
        ]
        for key, label, estimator, tune, perm in models:
            evaluate(f"tamano_{variant}_{key}", label, data, "regresion", variant, estimator, tune_ridge=tune, permutation=perm)
    checkpoint("regresion_completa", {"variantes": ["A", "B"], "modelos": 12})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--solo-baselines", action="store_true")
    args = parser.parse_args()
    run(args.solo_baselines)
