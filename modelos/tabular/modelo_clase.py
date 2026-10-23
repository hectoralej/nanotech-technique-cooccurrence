"""Four/three-class OOF classifiers with a strict feature allowlist and seed replay."""
from __future__ import annotations

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from tabular_data import RESULTS, load_dataset, save_json
from tabular_common import CLASS_FEATURES, N_JOBS, assert_classification_features, checkpoint, evaluate


def run():
    assert_classification_features(CLASS_FEATURES)
    rejected = []
    for forbidden in ("family", "carrier_type", "categoria_uso", "title", "sample", "clase_modelo", "clase_derivada"):
        try:
            assert_classification_features([*CLASS_FEATURES, forbidden])
        except AssertionError:
            rejected.append(forbidden)
        else:
            raise AssertionError(f"La prueba de fugas no rechaza {forbidden}")
    all_data = load_dataset()
    all_data = all_data[all_data.clase_modelo.ne("") & all_data[["size_nm", "zeta_mV", "pdi"]].notna().any(axis=1)].copy()
    validation = {"columnas_permitidas": CLASS_FEATURES, "columnas_prohibidas_rechazadas": rejected, "prueba_columnas_prohibidas": "PASS", "experimentos": []}
    for n_classes in (4, 3):
        data = all_data if n_classes == 4 else all_data[all_data.clase_modelo.ne("nanomaterial")].copy()
        models = [
            ("mayoritaria", "Clase mayoritaria", DummyClassifier(strategy="most_frequent"), "majority", False),
            ("logistica", "Logística multinomial", LogisticRegression(max_iter=3000, solver="lbfgs", random_state=0), None, True),
            ("rf", "RandomForest balanceado", RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=0, n_jobs=N_JOBS), None, True),
            ("hgb", "HistGradientBoosting", HistGradientBoostingClassifier(max_iter=300, learning_rate=.05, random_state=0, early_stopping=False), None, True),
        ]
        for key, name, estimator, baseline, perm in models:
            result = evaluate(f"clase{n_classes}_{key}", name, data, "clasificacion", str(n_classes), estimator, baseline=baseline, permutation=perm)
            if baseline:
                proportion = float(data.clase_modelo.value_counts(normalize=True).max())
                measured = result["metricas"]["exactitud"]["valor"]
                same = bool(np.isclose(proportion, measured))
                validation["experimentos"].append({"n_clases": n_classes, "proporcion_mayoritaria": proportion, "exactitud_dummy": measured, "coinciden": same, "explicacion": "La misma clase es mayoritaria en los cinco entrenamientos." if same else "La clase mayoritaria cambia con los datos de entrenamiento de algún fold; se usa la mayoría del entrenamiento, nunca la del test."})
                checkpoint("baseline_clasificacion_validada", validation["experimentos"][-1])
    validation["repeticion"] = "Cada modelo/fold se ajustó dos veces con la misma semilla; predicciones exactamente iguales. Se conserva la evidencia en las métricas por fold."
    save_json(RESULTS / "validacion_3.json", validation)
    checkpoint("clasificacion_completa", {"experimentos": [4, 3], "modelos": 8, "columnas_prohibidas": "PASS", "repeticion": "PASS"})


if __name__ == "__main__":
    run()
