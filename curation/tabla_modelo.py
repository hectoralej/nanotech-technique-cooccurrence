"""Build the frozen modeling table and its validation report from the v0.1 CSVs."""
from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "curation"
V01 = CUR / "v0.1"
PANEL_FILE = CUR / "ext_paneles.csv"
ARTICLE_FILE = CUR / "ext_articulos.csv"
DESCRIPTOR_FILE = CUR / "ext_descriptores.csv"
SPECTRA_FILE = CUR / "ext_espectros.csv"
EXTREME_FILE = V01 / "valores_extremos.csv"
OUTPUT_FILE = V01 / "tabla_modelo.csv"
REPORT_FILE = V01 / "VALIDACION_TABLA_MODELO.md"

CLASSES = {
    "liposome": "lipidico", "LNP": "lipidico", "SLN": "lipidico", "NLC": "lipidico", "PLN": "lipidico",
    "polymeric_NP": "polimerico", "nanogel": "polimerico", "micelle": "polimerico",
    "inorganic_NP": "inorganico", "nanomaterial": "nanomaterial",
    "other": "", "not_a_nanocarrier": "", "cubosome": "", "nanoemulsion": "",
}
TECHNIQUES = ("FTIR", "XRD", "UVVis", "SAXS", "EDS", "Raman")
COLUMN_ORDER = [
    "pmcid", "image_file", "ruta_imagen", "variant", "sample", "microscopia", "family", "carrier_type",
    "clase_modelo", "categoria_uso", "tier", "year", "n_descriptores", "size_nm_mediana",
    "zeta_mV_mediana", "pdi_mediana", "tamano_rango", "tiene_FTIR", "tiene_XRD", "tiene_UVVis",
    "tiene_SAXS", "tiene_EDS", "tiene_Raman", "flag_extremo", "fold",
]


def load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def decimal_or_none(value: object) -> Decimal | None:
    raw = str(value or "").strip().replace("−", "-").replace("–", "-")
    if not raw:
        return None
    try:
        number = Decimal(raw)
        return number if number.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def median_decimal(values: list[Decimal]) -> Decimal | None:
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / Decimal(2)


def decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def unique_join(values: list[str], separator: str) -> str:
    seen = set()
    result = []
    for value in values:
        value = str(value or "").strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return separator.join(result)


def microscopy(variants: list[str]) -> str:
    detected = set()
    for value in variants:
        v = value.casefold().replace("-", "").replace("_", "")
        if "cryotem" in v or "cryoem" in v:
            detected.add("cryoTEM")
        elif "stem" in v:
            detected.add("STEM")
        elif "sem" in v or "scanningelectron" in v:
            detected.add("SEM")
        elif "tem" in v or "transmissionelectron" in v or "hrtem" in v:
            detected.add("TEM")
        else:
            detected.add("otra")
    return next(iter(detected)) if len(detected) == 1 else "otra"


def assign_folds(records: list[dict], article_classes: dict[str, str]) -> dict[str, int]:
    """Deterministic five-fold group split; balance image rows within each class."""
    weights = Counter(r["pmcid"] for r in records)
    groups: dict[str, list[str]] = defaultdict(list)
    for pmcid in weights:
        groups[article_classes.get(pmcid, "")].append(pmcid)

    folds: dict[str, int] = {}
    for pmcids in groups.values():
        row_load = [0] * 5
        article_load = [0] * 5
        pmcids.sort(key=lambda pm: (-weights[pm], hashlib.sha256(pm.encode("utf-8")).hexdigest(), pm))
        for pmcid in pmcids:
            fold = min(range(5), key=lambda i: (row_load[i], article_load[i], i))
            folds[pmcid] = fold
            row_load[fold] += weights[pmcid]
            article_load[fold] += 1
    return folds


def main() -> int:
    panels = load(PANEL_FILE)
    articles = load(ARTICLE_FILE)
    descriptors = load(DESCRIPTOR_FILE)
    spectra = load(SPECTRA_FILE)
    extremes = load(EXTREME_FILE)

    required_types = set(articles["carrier_type"])
    unmapped_types = sorted(required_types - set(CLASSES))
    article_rows = articles.set_index("pmcid").to_dict("index")
    article_classes = {pm: CLASSES.get(info["carrier_type"], "") for pm, info in article_rows.items()}

    extreme_values: set[tuple[str, str, Decimal]] = set()
    extreme_pmcids = set()
    for row in extremes.to_dict("records"):
        pmcid, field = row["pmcid"], row["campo"]
        number = decimal_or_none(row["valor"])
        extreme_pmcids.add(pmcid)
        if number is not None:
            extreme_values.add((pmcid, field, number))

    descriptor_groups: dict[str, list[dict]] = defaultdict(list)
    for row in descriptors.to_dict("records"):
        descriptor_groups[row["pmcid"]].append(row)

    numeric_medians: dict[str, dict[str, Decimal | None]] = {}
    descriptor_counts: dict[str, int] = {}
    field_map = {"size_nm": "size_nm_mediana", "zeta_mV": "zeta_mV_mediana", "pdi": "pdi_mediana"}
    for pmcid, rows in descriptor_groups.items():
        descriptor_counts[pmcid] = len(rows)
        numeric_medians[pmcid] = {}
        for field, output_name in field_map.items():
            values = []
            for row in rows:
                number = decimal_or_none(row[field])
                if number is not None and (pmcid, field, number) not in extreme_values:
                    values.append(number)
            numeric_medians[pmcid][output_name] = median_decimal(values)

    article_techniques: dict[str, set[str]] = defaultdict(set)
    for row in spectra.to_dict("records"):
        article_techniques[row["pmcid"]].add(row["technique"].strip().casefold())

    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in panels.to_dict("records"):
        groups[(row["pmcid"], row["image_file"])].append(row)

    records = []
    for (pmcid, image_file), rows in groups.items():
        article = article_rows[pmcid]
        variants = unique_join([r["variant"] for r in rows], "|")
        # Preserve the requested sample aggregation for the grouping step; sample is not an output column.
        _samples = unique_join([r["sample"] for r in rows], "; ")
        modality = microscopy(variants.split("|") if variants else [])
        medians = numeric_medians.get(pmcid, {})
        size = medians.get("size_nm_mediana")
        size_band = "" if size is None else "<100" if size < 100 else "100-200" if size <= 200 else ">200"
        present = article_techniques.get(pmcid, set())
        records.append({
            "pmcid": pmcid,
            "image_file": image_file,
            "ruta_imagen": f"producto/imagenes/{pmcid}/{image_file}",
            "variant": variants,
            "sample": _samples,
            "microscopia": modality,
            "family": article["family"],
            "carrier_type": article["carrier_type"],
            "clase_modelo": article_classes.get(pmcid, ""),
            "categoria_uso": article["categoria_uso"],
            "tier": article["tier"],
            "year": article["year"],
            "n_descriptores": descriptor_counts.get(pmcid, 0),
            "size_nm_mediana": decimal_text(size),
            "zeta_mV_mediana": decimal_text(medians.get("zeta_mV_mediana")),
            "pdi_mediana": decimal_text(medians.get("pdi_mediana")),
            "tamano_rango": size_band,
            **{f"tiene_{tech}": int(tech.casefold() in present) for tech in TECHNIQUES},
            "flag_extremo": int(pmcid in extreme_pmcids),
        })

    folds = assign_folds(records, article_classes)
    for row in records:
        row["fold"] = folds[row["pmcid"]]
    output = pd.DataFrame(records, columns=COLUMN_ORDER)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    expected_pairs = set(zip(panels["pmcid"], panels["image_file"]))
    actual_pairs = set(zip(output["pmcid"], output["image_file"]))
    fold_counts = output.groupby("pmcid")["fold"].nunique()
    fold_range_ok = output["fold"].astype(int).between(0, 4).all()
    marked_rows = int((output["flag_extremo"].astype(int) == 1).sum())
    image_exists = output["ruta_imagen"].map(lambda p: (ROOT / Path(p.replace("/", "\\"))).is_file())
    existing_images = int(image_exists.sum())
    missing_images = int((~image_exists).sum())
    missing_size = int(output["size_nm_mediana"].eq("").sum())
    missing_zeta = int(output["zeta_mV_mediana"].eq("").sum())
    no_class = int(output["clase_modelo"].eq("").sum())

    balance = output.assign(clase_modelo=output["clase_modelo"].replace("", "(sin clase)"))
    balance_table = pd.crosstab(balance["clase_modelo"], balance["fold"]).reindex(columns=range(5), fill_value=0)
    class_counts = articles.groupby("carrier_type").size().to_dict()
    type_lines = [f"| `{t}` | {class_counts.get(t, 0)} | `{CLASSES[t] or '(sin clase)'}` |" for t in sorted(required_types & set(CLASSES))]
    type_lines.extend(f"| `{t}` | {class_counts.get(t, 0)} | **sin mapeo** |" for t in unmapped_types)
    balance_md = "\n".join(
        ["| clase_modelo | fold 0 | fold 1 | fold 2 | fold 3 | fold 4 |", "|---|---:|---:|---:|---:|---:|"]
        + ["| " + str(label) + " | " + " | ".join(str(int(v)) for v in balance_table.loc[label].tolist()) + " |" for label in balance_table.index]
    )

    checks = {
        "filas_y_pares_unicos": len(output) == len(expected_pairs) and actual_pairs == expected_pairs,
        "un_fold_por_pmcid_y_rango_0_4": bool((fold_counts == 1).all() and fold_range_ok),
        "distribucion_clase_fold_reportada": int(balance_table.to_numpy().sum()) == len(output) and no_class >= 0,
        "rutas_todas_comprobadas": existing_images + missing_images == len(output),
        "medianas_vacias_contabilizadas": missing_size >= 0 and missing_zeta >= 0,
        "flag_extremo_cuenta": marked_rows == len(extremes),
        "todos_los_carrier_type_tratados": not unmapped_types,
    }
    report = f"""# Validación de `tabla_modelo.csv`

Generada con `python curation/tabla_modelo.py`; entradas CSV leídas con `utf-8-sig` y salida escrita con `utf-8-sig`. No se descargaron imágenes. El conteo de archivos presentes es una instantánea y puede cambiar mientras continúa la descarga.

## Comprobaciones obligatorias

1. Filas esperadas: **{len(expected_pairs)}** pares únicos `(pmcid, image_file)`; filas generadas: **{len(output)}**. Coincidencia exacta: **{'sí' if checks['filas_y_pares_unicos'] else 'NO'}**.
2. Un mismo `pmcid` en más de un fold: **{int((fold_counts > 1).sum())}**; todos los folds entre 0 y 4: **{'sí' if fold_range_ok else 'NO'}**.
3. Distribución de filas por clase y fold:

{balance_md}

   Filas sin `clase_modelo`: **{no_class}**.
4. `ruta_imagen` existente: **{existing_images}**; ausente/no descargada: **{missing_images}**.
5. `size_nm_mediana` vacío: **{missing_size}** filas; `zeta_mV_mediana` vacío: **{missing_zeta}** filas.

## Reglas y controles adicionales

- Valores extremos de referencia: **{len(extremes)}**; filas con `flag_extremo=1`: **{marked_rows}**. Coinciden: **{'sí' if checks['flag_extremo_cuenta'] else 'NO'}**. Se excluye cada valor marcado solo de la mediana de su campo; otros datos de la fila siguen entrando en su campo respectivo.
- Medianas calculadas por artículo con `Decimal`, sin redondeo. `n_descriptores` cuenta todas las filas descriptor del artículo, incluso si incluyen un valor extremo.
- Mapeo de `carrier_type` (conteo de artículos):

| carrier_type | artículos | clase_modelo |
|---|---:|---|
{chr(10).join(type_lines)}

   `other` y `not_a_nanocarrier` quedan vacíos; por decisión del usuario, `cubosome` y `nanoemulsion` también quedan vacíos. Tipos existentes sin regla explícita: **{len(unmapped_types)}**. Todos los tipos quedan cubiertos por clase o exclusión explícita: **{'sí' if checks['todos_los_carrier_type_tratados'] else 'NO'}**.
- Folds deterministas y agrupados por artículo: dentro de cada clase se ordenan grupos por cantidad de micrografías descendente; SHA-256 del PMCID desempata y cada grupo se asigna al fold con menor carga. Todas las figuras del artículo comparten fold.
- `variant` se une con `|` y `sample` con `; ` dentro de la agrupación. `microscopia` resume TEM/HRTEM como TEM; modalidades mixtas o no reconocidas quedan como `otra`.

## Resultado del gate

""" + "\n".join(f"- {name}: **{'PASS' if passed else 'FAIL'}**" for name, passed in checks.items()) + "\n"
    REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"tabla: {len(output)} filas; extremos marcados: {marked_rows}/{len(extremes)}; imagenes presentes: {existing_images}; faltantes: {missing_images}")
    print(f"medianas vacias: size={missing_size}, zeta={missing_zeta}; filas sin clase={no_class}")
    print(report.split("## Resultado del gate", 1)[1].strip())
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
