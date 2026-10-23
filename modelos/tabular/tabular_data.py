"""Dataset descriptor-level, derived read-only from frozen curation inputs."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "resultados"
DATASET = HERE / "dataset_descriptores.csv"
CUR = ROOT / "curation"
FLAGS = ["tiene_TEM", "tiene_SEM", "tiene_cryoTEM", "tiene_FTIR", "tiene_XRD", "tiene_UVVis", "tiene_SAXS", "tiene_EDS", "tiene_Raman"]
COLUMNS = ["pmcid", "sample", "size_nm", "pdi", "zeta_mV", "medium", "medio_declarado", "clase_modelo", "carrier_type", "categoria_uso", "year", "n_paneles", *FLAGS, "fold"]


def read_csv(path):
    return pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False, dtype=str)


def imported_rules():
    spec = importlib.util.spec_from_file_location("frozen_model_rules", CUR / "tabla_modelo.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def protected_hashes():
    paths = list(CUR.glob("ext_*.csv")) + [p for p in (CUR / "v0.1").rglob("*") if p.is_file()]
    paths.append(CUR / "tabla_modelo.py")
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def build_dataset():
    RESULTS.mkdir(parents=True, exist_ok=True)
    before = protected_hashes()
    rules = imported_rules()
    desc = read_csv(CUR / "ext_descriptores.csv")
    articles = read_csv(CUR / "ext_articulos.csv")
    panels = read_csv(CUR / "ext_paneles.csv")
    spectra = read_csv(CUR / "ext_espectros.csv")
    frozen = read_csv(CUR / "v0.1" / "tabla_modelo.csv")
    assert articles.pmcid.is_unique, "PMCID duplicado en artículos"
    assert frozen.groupby("pmcid").fold.nunique().max() == 1
    assert frozen.groupby("pmcid").clase_modelo.nunique().max() == 1
    official = frozen.drop_duplicates("pmcid").set_index("pmcid")
    metadata = articles.set_index("pmcid")
    assert set(desc.pmcid) <= set(metadata.index)
    classes = {pm: rules.CLASSES.get(row.carrier_type, "") for pm, row in metadata.iterrows()}
    missing = sorted(set(desc.pmcid) - set(official.index))
    fallback = {}
    if missing:
        records = panels[["pmcid", "image_file"]].drop_duplicates().to_dict("records")
        represented = {r["pmcid"] for r in records}
        records += [{"pmcid": pm, "image_file": ""} for pm in missing if pm not in represented]
        fallback = rules.assign_folds(records, classes)

    panel_counts = panels.groupby("pmcid").size().to_dict()
    micro = panels.groupby("pmcid").variant.agg(lambda vals: "|".join(vals).upper()).to_dict()
    techs = spectra.groupby("pmcid").technique.agg(lambda vals: {str(v).casefold() for v in vals}).to_dict()
    data = desc[["pmcid", "sample", "size_nm", "pdi", "zeta_mV", "medium"]].copy()
    filtered = {}
    for field, valid in {
        "size_nm": lambda s: s.between(1, 5000),
        "pdi": lambda s: s.le(1.5),
        "zeta_mV": lambda s: s.abs().le(150),
    }.items():
        values = pd.to_numeric(data[field], errors="coerce")
        mask = valid(values) & np.isfinite(values)
        filtered[field] = int((values.notna() & ~mask).sum())
        data[field] = values.where(mask)
    data["medium"] = data.medium.str.strip().replace("", "not_declared")
    data["medio_declarado"] = data.medium.str.casefold().ne("not_declared").astype(int)
    data["clase_modelo"] = data.pmcid.map(lambda pm: official.loc[pm, "clase_modelo"] if pm in official.index else classes[pm])
    for field in ("carrier_type", "categoria_uso", "year"):
        data[field] = data.pmcid.map(metadata[field])
    data["year"] = pd.to_numeric(data.year, errors="coerce")
    data["n_paneles"] = data.pmcid.map(panel_counts).fillna(0).astype(int)
    data["tiene_TEM"] = data.pmcid.map(lambda pm: int("TEM" in micro.get(pm, "")))
    data["tiene_SEM"] = data.pmcid.map(lambda pm: int("SEM" in micro.get(pm, "")))
    data["tiene_cryoTEM"] = data.pmcid.map(lambda pm: int("CRYOTEM" in micro.get(pm, "")))
    for technique in ("FTIR", "XRD", "UVVis", "SAXS", "EDS", "Raman"):
        data[f"tiene_{technique}"] = data.pmcid.map(lambda pm: int(technique.casefold() in techs.get(pm, set())))
    data["fold"] = data.pmcid.map(lambda pm: int(official.loc[pm, "fold"]) if pm in official.index else fallback[pm])
    data = data[COLUMNS]
    assert len(data) == len(desc)
    assert data.fold.notna().all() and data.fold.between(0, 4).all()
    assert data.groupby("pmcid").fold.nunique().eq(1).all()
    expected = data[data.pmcid.isin(official.index)].pmcid.map(official.fold.astype(int))
    assert np.array_equal(data.loc[expected.index, "fold"], expected)
    assert (data[["pmcid", "sample"]].values == desc[["pmcid", "sample"]].values).all()
    assert before == protected_hashes(), "Se modificó un archivo protegido"
    data.to_csv(DATASET, index=False, encoding="utf-8-sig")
    counts = data.assign(clase_modelo=data.clase_modelo.replace("", "(sin clase)")).groupby(["fold", "clase_modelo"]).agg(n_filas=("pmcid", "size"), n_articulos=("pmcid", "nunique")).reset_index()
    counts.to_csv(RESULTS / "distribucion_folds_clases.csv", index=False, encoding="utf-8-sig")
    audit = {
        "filas": len(data), "articulos": data.pmcid.nunique(), "filas_por_fold": {str(k): int(v) for k, v in data.groupby("fold").size().items()},
        "articulos_por_fold": {str(k): int(v) for k, v in data.groupby("fold").pmcid.nunique().items()},
        "articulos_con_fold_importado": len(set(data.pmcid) & set(official.index)), "articulos_fallback": missing,
        "valores_fuera_de_rango_vaciados": filtered,
        "datos_validos": {k: int(data[k].notna().sum()) for k in ("size_nm", "pdi", "zeta_mV")},
        "proporcion_medio_no_declarado": float(1 - data.medio_declarado.mean()),
        "tiene_TEM": "Incluye TEM, HRTEM, STEM y cryoTEM; tiene_cryoTEM identifica además el subconjunto cryo.",
        "validacion_1": "PASS", "protected_inputs": before,
    }
    save_json(RESULTS / "validacion_datos.json", audit)
    print(json.dumps({k: v for k, v in audit.items() if k != "protected_inputs"}, ensure_ascii=False, indent=2))
    return data


def load_dataset():
    data = pd.read_csv(DATASET, encoding="utf-8-sig", keep_default_na=False)
    for field in ("size_nm", "pdi", "zeta_mV", "year"):
        data[field] = pd.to_numeric(data[field], errors="coerce")
    data["fold"] = data.fold.astype(int)
    return data


if __name__ == "__main__":
    build_dataset()
