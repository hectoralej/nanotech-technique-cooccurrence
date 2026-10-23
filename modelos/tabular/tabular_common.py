"""Shared grouped evaluation, leakage controls, bootstrap and resumable folds."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

from tabular_data import HERE, RESULTS, ROOT, DATASET, FLAGS, save_json, load_dataset

N_BOOT = 1000
# Windows sandbox blocks joblib's named pipes even for its threaded pool.
N_JOBS = 1
PRODUCT = ROOT / "producto" / "modelo_tabular"
REG_A = ["clase_modelo", "carrier_type", "medio_declarado", "medium", "year", "n_paneles", *FLAGS]
CLASS_FEATURES = ["log10_size_nm", "zeta_mV", "pdi", "medio_declarado", "medium", "year", "n_paneles", *FLAGS]
FORBIDDEN = {"family", "carrier_type", "categoria_uso", "title", "titulo", "sample", "clase_modelo"}


def checkpoint(stage, details=None):
    state = {"etapa": stage, "detalles": details or {}, "hora_local": datetime.now().isoformat(timespec="seconds")}
    save_json(HERE / "progreso.json", state)
    with (HERE / "CHECKPOINTS.md").open("a", encoding="utf-8") as stream:
        stream.write(f"\n- {state['hora_local']} — {stage}: {json.dumps(details or {}, ensure_ascii=False)}\n")
    print(f"CHECKPOINT {stage}: {details or {}}", flush=True)


def assert_classification_features(features):
    bad = set(features) & FORBIDDEN
    unknown = set(features) - set(CLASS_FEATURES)
    assert not bad and not unknown, f"Fuga de etiqueta: prohibidas={sorted(bad)}, no permitidas={sorted(unknown)}"


def feature_matrix(data, task, variant):
    frame = data.copy()
    if task == "regresion":
        features = REG_A + (["zeta_mV", "pdi"] if variant == "B" else [])
    else:
        frame["log10_size_nm"] = np.log10(frame.size_nm)
        features = CLASS_FEATURES
        assert_classification_features(features)
    X = frame[features].copy()
    if task != "regresion":
        assert_classification_features(X.columns)
    return X


def pipeline_for(model, X):
    cats = [c for c in X if c in {"medium", "clase_modelo", "carrier_type"}]
    nums = [c for c in X if c not in cats]
    preprocess = ColumnTransformer([
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cats),
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True)), ("scale", StandardScaler())]), nums),
    ], remainder="drop", verbose_feature_names_out=True)
    return Pipeline([("preprocess", preprocess), ("model", model)])


def metric_values(y, pred, task, labels=None):
    if task == "regresion":
        relative = np.abs(np.power(10.0, np.clip(pred, -100, 100)) - np.power(10.0, y)) / np.power(10.0, y)
        return {"r2": float(r2_score(y, pred)), "mae_log10": float(mean_absolute_error(y, pred)), "error_mediano_relativo_nm": float(np.median(relative)), "mae_nm": float(np.mean(relative * np.power(10.0, y)))}
    return {"exactitud": float(accuracy_score(y, pred)), "f1_macro": float(f1_score(y, pred, labels=labels, average="macro", zero_division=0))}


def bootstrap_by_article(y, pred, pmcid, task, labels=None):
    """Resample articles with replacement, retaining every descriptor row of each draw."""
    codes, groups = pd.factorize(pmcid, sort=True)
    ng = len(groups)
    rng = np.random.default_rng(0)
    multiplicities = rng.multinomial(ng, np.full(ng, 1.0 / ng), size=N_BOOT)
    if task == "regresion":
        y = np.asarray(y, float); pred = np.asarray(pred, float)
        rel = np.abs(np.power(10.0, np.clip(pred, -100, 100)) - np.power(10.0, y)) / np.power(10.0, y)
        stats = np.column_stack([np.ones(len(y)), y, y*y, (y-pred)**2, np.abs(y-pred), rel*np.power(10.0, y)])
        group_stats = np.zeros((ng, stats.shape[1]))
        np.add.at(group_stats, codes, stats)
        sums = multiplicities @ group_stats
        denom = sums[:, 2] - sums[:, 1]**2 / sums[:, 0]
        vals = {"r2": 1 - sums[:, 3] / np.maximum(denom, 1e-30), "mae_log10": sums[:, 4]/sums[:, 0], "mae_nm": sums[:, 5]/sums[:, 0]}
        order = np.argsort(rel, kind="stable"); sorted_rel = rel[order]; sorted_codes = codes[order]
        medians = []
        for weights in multiplicities:
            cumul = np.cumsum(weights[sorted_codes]); n = cumul[-1]
            lo = np.searchsorted(cumul, (n-1)//2 + 1); hi = np.searchsorted(cumul, n//2 + 1)
            medians.append((sorted_rel[lo] + sorted_rel[hi]) / 2)
        vals["error_mediano_relativo_nm"] = np.asarray(medians)
    else:
        index = {lab: i for i, lab in enumerate(labels)}; k = len(labels)
        grouped_cm = np.zeros((ng, k*k))
        for i, (a, b) in enumerate(zip(y, pred)):
            grouped_cm[codes[i], index[a]*k+index[b]] += 1
        cms = (multiplicities @ grouped_cm).reshape(N_BOOT, k, k)
        tp = np.diagonal(cms, axis1=1, axis2=2)
        f1 = 2*tp / np.maximum(cms.sum(axis=1) + cms.sum(axis=2), 1)
        vals = {"exactitud": tp.sum(axis=1)/cms.sum(axis=(1, 2)), "f1_macro": f1.mean(axis=1)}
    return {key: [float(np.quantile(values, .025)), float(np.quantile(values, .975))] for key, values in vals.items()}


def input_fingerprint():
    digest = hashlib.sha256(DATASET.read_bytes())
    for path in [HERE / name for name in ("tabular_data.py", "tabular_common.py", "modelo_tamano.py", "modelo_clase.py")]:
        digest.update(path.name.encode()); digest.update(path.read_bytes())
    digest.update(sklearn.__version__.encode())
    return digest.hexdigest()


def coefficients(fitted, fold):
    model = fitted.named_steps["model"]
    if not hasattr(model, "coef_"):
        return []
    names = fitted.named_steps["preprocess"].get_feature_names_out()
    coefs = np.atleast_2d(model.coef_)
    labels = list(model.classes_) if hasattr(model, "classes_") else ["log10_size_nm"]
    return [{"fold": int(fold), "clase": str(label), "variable_transformada": str(name), "coeficiente": float(value)} for label, row in zip(labels, coefs) for name, value in zip(names, row)]


def save_registry(result):
    PRODUCT.mkdir(parents=True, exist_ok=True)
    path = PRODUCT / "metricas_tabular.json"
    registry = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"evaluacion": "5 particiones por artículo", "bootstrap": "1000 remuestreos por artículo de predicciones fuera de muestra; no reentrena modelos", "modelos": []}
    registry["modelos"] = [r for r in registry["modelos"] if r["id"] != result["id"]] + [result]
    save_json(path, registry)


def evaluate(model_id, label, data, task, variant, estimator=None, baseline=None, tune_ridge=False, permutation=True):
    data = data.copy()
    X = feature_matrix(data, task, variant)
    y = np.log10(data.size_nm.to_numpy(float)) if task == "regresion" else data.clase_modelo.to_numpy(str)
    labels = sorted(set(y)) if task != "regresion" else None
    predictions = np.empty(len(data), dtype=float if task == "regresion" else object)
    fingerprint = input_fingerprint()
    folds_info, importances, coef_rows = [], [], []
    cache_dir = RESULTS / "cache" / model_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    for fold in range(5):
        train = np.flatnonzero(data.fold.to_numpy() != fold); test = np.flatnonzero(data.fold.to_numpy() == fold)
        assert len(test) and len(train)
        assert not set(data.iloc[train].pmcid) & set(data.iloc[test].pmcid)
        cache_path = cache_dir / f"fold_{fold}.json"
        cached = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
        if cached.get("fingerprint") == fingerprint and cached.get("test_rows") == test.tolist():
            predictions[test] = cached["predictions"]
            folds_info.append(cached["fold_info"]); importances += cached["importances"]; coef_rows += cached["coefficients"]
            continue
        checkpoint("entrenamiento", {"modelo": model_id, "fold": fold, "train_articulos": int(data.iloc[train].pmcid.nunique()), "test_articulos": int(data.iloc[test].pmcid.nunique())})
        extra = {}
        fitted = None
        if baseline == "class_mean":
            training = pd.DataFrame({"clase_modelo": data.iloc[train].clase_modelo.to_numpy(), "target": y[train]})
            means = training.groupby("clase_modelo").target.mean().to_dict()
            pred = np.asarray([means.get(c, float(y[train].mean())) for c in data.iloc[test].clase_modelo])
        else:
            fitted = pipeline_for(clone(estimator), X)
            with threadpool_limits(limits=1):
                if tune_ridge:
                    search = GridSearchCV(fitted, {"model__alpha": [0.01, 0.1, 1, 10, 100]}, cv=GroupKFold(n_splits=4), scoring="neg_mean_absolute_error", refit=True, n_jobs=1, error_score="raise")
                    search.fit(X.iloc[train], y[train], groups=data.iloc[train].pmcid)
                    fitted = search.best_estimator_
                    extra = {"alpha": float(search.best_params_["model__alpha"]), "mae_interno": float(-search.best_score_)}
                else:
                    fitted.fit(X.iloc[train], y[train])
                pred = fitted.predict(X.iloc[test])
                if task != "regresion":
                    duplicate = clone(fitted).fit(X.iloc[train], y[train])
                    repeated = duplicate.predict(X.iloc[test])
                    assert np.array_equal(pred, repeated), f"Entrenamiento no reproducible: {model_id}, fold {fold}"
                    extra["repeticion_entrenamiento_predicciones_identicas"] = True
                if permutation and baseline is None:
                    perm = permutation_importance(fitted, X.iloc[test], y[test], scoring="r2" if task == "regresion" else "f1_macro", n_repeats=5, random_state=0, n_jobs=1)
                    local_importances = [{"fold": fold, "variable": feature, "importancia_media": float(avg), "importancia_std": float(sd)} for feature, avg, sd in zip(X.columns, perm.importances_mean, perm.importances_std)]
                else:
                    local_importances = []
        if fitted is None:
            local_importances = []
        predictions[test] = pred
        info = {"fold": fold, "n_train": len(train), "n_test": len(test), "articulos_train": int(data.iloc[train].pmcid.nunique()), "articulos_test": int(data.iloc[test].pmcid.nunique()), **extra, **metric_values(y[test], pred, task, labels)}
        local_coef = coefficients(fitted, fold) if fitted is not None else []
        folds_info.append(info); importances += local_importances; coef_rows += local_coef
        save_json(cache_path, {"fingerprint": fingerprint, "test_rows": test.tolist(), "predictions": np.asarray(pred).tolist(), "fold_info": info, "importances": local_importances, "coefficients": local_coef})
    assert all(pred is not None for pred in predictions)
    metrics = metric_values(y, predictions, task, labels)
    cis = bootstrap_by_article(y, predictions, data.pmcid.to_numpy(), task, labels)
    out = data[["pmcid", "sample", "fold"]].copy()
    out["y_real"] = y; out["y_pred"] = predictions
    out[["pmcid", "sample", "y_real", "y_pred", "fold"]].to_csv(RESULTS / f"predicciones_{model_id}.csv", index=False, encoding="utf-8-sig")
    if importances:
        pd.DataFrame(importances).to_csv(RESULTS / f"importancia_{model_id}.csv", index=False, encoding="utf-8-sig")
    if coef_rows:
        pd.DataFrame(coef_rows).to_csv(RESULTS / f"coeficientes_{model_id}.csv", index=False, encoding="utf-8-sig")
    per_class = []
    if task == "regresion":
        classes = data.clase_modelo.replace("", "(sin clase)").to_numpy()
        for cls in sorted(set(classes)):
            mask = classes == cls
            per_class.append({"clase": cls, "n_filas": int(mask.sum()), "n_articulos": int(data.loc[mask].pmcid.nunique()), "r2": float(r2_score(y[mask], predictions[mask])) if mask.sum() > 1 else None})
        pd.DataFrame(per_class).to_csv(RESULTS / f"r2_por_clase_{model_id}.csv", index=False, encoding="utf-8-sig")
    else:
        cm = confusion_matrix(y, predictions, labels=labels, normalize="true")
        pd.DataFrame(cm, index=labels, columns=labels).to_csv(RESULTS / f"confusion_{model_id}.csv", encoding="utf-8-sig")
    result = {
        "id": model_id, "nombre": label, "tarea": "tamano_log10" if task == "regresion" else f"clase_{len(labels)}",
        "variante": variant, "entradas": ["clase_modelo"] if baseline == "class_mean" else [] if baseline else list(X.columns),
        "n_filas": len(data), "n_articulos": int(data.pmcid.nunique()), "evaluacion": "5 particiones por artículo", "metricas": {k: {"valor": v, "ic95": cis[k]} for k, v in metrics.items()},
        "linea_base": "tamano_media_clase" if task == "regresion" else f"clase{len(labels)}_mayoritaria", "por_fold": folds_info, "r2_por_clase": per_class,
        "predicciones": f"modelos/tabular/resultados/predicciones_{model_id}.csv", "fingerprint": fingerprint,
    }
    save_json(RESULTS / f"metricas_{model_id}.json", result)
    save_registry(result)
    checkpoint("modelo_validado", {"modelo": model_id, "metricas": metrics, "n_articulos": result["n_articulos"]})
    return result


def environment():
    import matplotlib
    save_json(RESULTS / "entorno.json", {"python": sys.version, "numpy": np.__version__, "pandas": pd.__version__, "sklearn": sklearn.__version__, "matplotlib": matplotlib.__version__, "bootstrap": N_BOOT, "random_state": 0, "hilos_RF": N_JOBS})
