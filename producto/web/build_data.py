#!/usr/bin/env python3
"""Build static Atlas JSON from canonical curation and figure-flow CSVs."""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TABLES = {
    "articulos": "ext_articulos.csv",
    "paneles": "ext_paneles.csv",
    "descriptores": "ext_descriptores.csv",
    "espectros": "ext_espectros.csv",
}
MODEL_TABLE = "v0.1/tabla_modelo.csv"
MODEL_FILES = ("metricas.json", "predicciones.json", "similares.json")
TEXT_FIELDS = {
    "articulos": ("title",),
    "paneles": ("fig", "variant", "sample", "scale_bar_in_caption", "quote"),
    "descriptores": ("sample", "medium", "source", "quote"),
    "espectros": ("technique", "fig", "sample", "applies_to"),
}
FIGURE_CSV = Path("modelos/flujo_figuras/figuras_vision.csv")
PANEL_CSV = Path("modelos/flujo_figuras/segmentacion/cajas/paneles.csv")
PANEL_INDEX_CSV = Path("modelos/flujo_figuras/segmentacion/cajas/indice_recortes.csv")
DESCRIPTOR_V03_CSV = Path("modelos/descriptores_v02/descriptores_v03.csv")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def clean_text(value: str) -> str:
    """Decode repeated HTML entities and return safe, readable plain text."""
    text = value
    for _ in range(5):
        decoded = html.unescape(text)
        if decoded == text:
            break
        text = decoded
    text = text.replace("\xa0", " ")
    # Keep scientific/biological italics as a visible plain-text convention.
    text = re.sub(r"<(?:i|em)\b[^>]*>(.*?)</(?:i|em)\s*>", r"*\1*", text,
                  flags=re.IGNORECASE | re.DOTALL)
    # No raw markup reaches the UI; textContent renders the resulting text safely.
    text = re.sub(r"</?\s*[a-z][^>]*>", "", text, flags=re.IGNORECASE)
    return text


def clean_table_text(table_name: str, rows: list[dict[str, str]]) -> None:
    for row in rows:
        for field in TEXT_FIELDS.get(table_name, ()):
            if row.get(field):
                row[field] = clean_text(row[field])


def as_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"true", "1", "yes", "si", "sí"}


def public_image_path(repo: Path, source_path: str) -> tuple[str, bool]:
    """Return a relative web path only when the source image exists locally."""
    normalized = (source_path or "").replace("\\", "/").strip()
    if not normalized:
        return "", False
    # CSV paths are repository-relative (for example producto/imagenes/...).
    parts = Path(normalized).parts
    if Path(normalized).is_absolute() or ".." in parts:
        return "", False
    local = repo.joinpath(*parts).resolve()
    if not local.is_relative_to(repo.resolve()):
        return "", False
    if not local.is_file():
        return "", False
    if normalized.startswith("producto/"):
        normalized = normalized[len("producto/"):]
    return "../" + "/".join(quote(part) for part in normalized.split("/")), True


def reuse_license_allows_image(license_name: str) -> bool:
    normalized = (license_name or "").lower().replace("_", " ")
    return bool(re.search(r"\bcc\s*by\b|\bcc0\b", normalized)) and not bool(re.search(r"\bnc\b|\bnd\b", normalized))


TECHNIQUE_FAMILIES = {
    "Microscopía electrónica y de sonda": ("SEM", "TEM", "cryo-TEM", "STEM", "HRTEM", "FIB-SEM", "SAED", "EELS", "AFM"),
    "Espectroscopías": ("FTIR", "UV-vis", "EDS", "Raman", "XPS", "RMN", "Dicroísmo circular", "AFM-IR", "Mössbauer", "AAS", "MS"),
    "Térmicas": ("DSC", "TGA", "DTA"),
    "Dispersión de luz/rayos X": ("XRD", "DLS", "SAXS", "SANS", "Potencial zeta"),
    "Fluorescencia y óptica": ("Fluorescencia/confocal", "Fluorescencia in vivo", "Fotoluminiscencia", "Histología H&E"),
    "Otras": ("VSM", "DCS", "HPLC", "GPC", "BET", "MRI"),
}
TECHNIQUE_TO_FAMILY = {technique: family for family, names in TECHNIQUE_FAMILIES.items() for technique in names}
# A compound thermal label denotes several methods, not a synonym of one method.
TECHNIQUE_ALIASES: dict[str, tuple[str, ...]] = {
    "ft-ir": ("FTIR",), "ftir": ("FTIR",),
    "uvvis": ("UV-vis",), "uv-vis": ("UV-vis",), "uvvis spectroscopy": ("UV-vis",),
    "edx": ("EDS",), "eds": ("EDS",), "eds-mapas": ("EDS",),
    "zeta": ("Potencial zeta",), "potencial zeta": ("Potencial zeta",),
    "cryo-tem": ("cryo-TEM",), "cryotem": ("cryo-TEM",), "cryo-em": ("cryo-TEM",), "cryoem": ("cryo-TEM",),
    "haadf": ("STEM",), "haadf-stem": ("STEM",), "stem": ("STEM",),
    "h&e": ("Histología H&E",), "he": ("Histología H&E",), "histologia h&e": ("Histología H&E",),
    "fluorescencia": ("Fluorescencia/confocal",), "confocal": ("Fluorescencia/confocal",), "clsm": ("Fluorescencia/confocal",),
    "fluorescencia in vivo": ("Fluorescencia in vivo",), "pl": ("Fotoluminiscencia",),
    "1h-nmr": ("RMN",), "nmr": ("RMN",), "cd": ("Dicroísmo circular",),
    "mossbauer": ("Mössbauer",),
    "dsc-tga": ("DSC", "TGA"), "tga/dsc": ("DSC", "TGA"), "tga/dta": ("TGA", "DTA"),
    "dsc": ("DSC",), "tga": ("TGA",), "dta": ("DTA",),
}
# These are dyes, imaging modes, an element/adsorbate, a stain or a measured
# property; they are not counted as a characterization technique in this view.
NON_TECHNIQUE_MARKERS = {
    "dapi", "fitc", "pi", "dic", "bf", "dioc6", "n2", "citometria",
    "au m", "pas", "distribucion de tamano",
}


def normalize_technique(value: str) -> tuple[str, ...]:
    """Map source labels to methods; leave unrecognized labels auditable."""
    token = re.sub(r"\s+", " ", (value or "").strip())
    if not token or token.casefold() in NON_TECHNIQUE_MARKERS:
        return ()
    return TECHNIQUE_ALIASES.get(token.casefold(), (token,))


def figure_techniques(value: str) -> list[str]:
    return sorted({technique for token in re.split(r"[|;+]", value or "") for technique in normalize_technique(token)}, key=str.casefold)


def build_new_sources(repo: Path, output: Path) -> dict[str, int]:
    figures = read_csv(repo / FIGURE_CSV)
    panels = read_csv(repo / PANEL_INDEX_CSV)
    panel_base = read_csv(repo / PANEL_CSV)
    descriptors = read_csv(repo / DESCRIPTOR_V03_CSV)
    if len(panels) != len(panel_base):
        raise ValueError(f"Los CSV de paneles no coinciden: índice={len(panels)}, cajas={len(panel_base)}")

    # The index is canonical for class/fold; validate that both panel tables
    # describe the same keys before publishing any generated JSON.
    key = lambda row: (row.get("fig_id", ""), row.get("panel", ""))
    if {key(row) for row in panels} != {key(row) for row in panel_base}:
        raise ValueError("paneles.csv e indice_recortes.csv no contienen las mismas claves de panel")

    thumbnail_manifest_path = HERE / "img" / "paneles_web.csv"
    thumbnail_paths: dict[tuple[str, str], str] = {}
    if thumbnail_manifest_path.is_file():
        thumbnail_rows = read_csv(thumbnail_manifest_path)
        for row in thumbnail_rows:
            relative = (row.get("miniatura", "") or "").replace("\\", "/").strip()
            parts = Path(relative).parts
            if len(parts) < 3 or parts[0] != "paneles" or ".." in parts:
                raise ValueError(f"Ruta de miniatura no válida en {thumbnail_manifest_path}: {relative}")
            thumbnail_paths[key(row)] = relative
        if len(thumbnail_paths) != len(thumbnail_rows):
            raise ValueError("paneles_web.csv contiene claves de panel duplicadas")
        if set(thumbnail_paths) != {key(row) for row in panels}:
            raise ValueError("paneles_web.csv no coincide con las claves del indice_recortes.csv")

    article_meta = {
        row.get("pmcid", ""): row
        for row in read_csv(repo / "curation" / TABLES["articulos"])
    }
    accepted = {"aceptada_auto", "aceptada_arbitrada"}
    reuse_allowed_pmcs = {
        pmcid for pmcid, article in article_meta.items()
        if reuse_license_allows_image(article.get("license_epmc", ""))
    }
    by_figure: dict[str, list[dict[str, str]]] = {}
    for panel in panels:
        by_figure.setdefault(panel.get("fig_id", ""), []).append(panel)

    for figure in figures:
        meta = article_meta.get(figure.get("pmcid", ""), {})
        image_path, image_exists = public_image_path(repo, figure.get("imagen", ""))
        doi = meta.get("doi_link", "")
        license_name = meta.get("license_epmc", "")
        figure["doi_link"] = doi if doi.startswith("https://doi.org/") else ""
        figure["title"] = meta.get("title", "")
        figure["title"] = clean_text(figure["title"])
        figure["license"] = license_name
        figure["license_allows_image"] = reuse_license_allows_image(license_name)
        figure["image_web"] = image_path if figure["license_allows_image"] else ""
        figure["image_available"] = image_exists and figure["license_allows_image"]
        figure["accepted"] = figure.get("estado", "") in accepted
        figure["tecnicas_normalizadas"] = figure_techniques(figure.get("tecnicas", ""))
        figure["familias_tecnicas"] = sorted({TECHNIQUE_TO_FAMILY.get(technique, "Otras") for technique in figure["tecnicas_normalizadas"]})

    for panel in panels:
        thumbnail = thumbnail_paths.get(key(panel), "")
        thumbnail_file = (HERE / "img" / thumbnail).resolve() if thumbnail else None
        within_img = thumbnail_file is not None and thumbnail_file.is_relative_to((HERE / "img").resolve())
        crop_exists = bool(within_img and thumbnail_file.is_file())
        panel["crop_web"] = "img/" + thumbnail if crop_exists and panel.get("pmcid", "") in reuse_allowed_pmcs else ""
        panel["crop_available"] = crop_exists and panel.get("pmcid", "") in reuse_allowed_pmcs
        panel["elegible_morfologia_bool"] = as_bool(panel.get("elegible_morfologia"))
        panel["cascada_bool"] = as_bool(panel.get("cascada"))

    usable = [row for row in descriptors if as_bool(row.get("usable_v03"))]
    for row in usable:
        row["revisar_v03_bool"] = as_bool(row.get("revisar_v03"))
        for field in ("quote", "sample", "source", "medium"):
            if row.get(field):
                row[field] = clean_text(row[field])

    (output / "figuras.json").write_text(json.dumps(figures, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (output / "paneles_recortados.json").write_text(json.dumps(panels, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (output / "descriptores_v03.json").write_text(json.dumps(usable, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    visible_figures = [row for row in figures if row["accepted"] and row.get("destino_vision") != "excluir"]
    visible_technique_counts = {
        technique: sum(technique in row["tecnicas_normalizadas"] for row in visible_figures)
        for technique in sorted({tech for row in figures for tech in row["tecnicas_normalizadas"]}, key=str.casefold)
    }
    top_techniques = [name for name, _ in sorted(visible_technique_counts.items(), key=lambda item: (-item[1], item[0].casefold()))[:10]]
    stats = {
        "figures_total": len(figures),
        "figures_accepted": sum(row["accepted"] for row in figures),
        "figures_accepted_visible": sum(row["accepted"] and row.get("destino_vision") != "excluir" for row in figures),
        "figures_queue": sum(row.get("estado") == "cola_revision" for row in figures),
        "figures_excluded_destination": sum(row["accepted"] and row.get("destino_vision") == "excluir" for row in figures),
        "figures_queue_excluded_destination": sum(row.get("estado") == "cola_revision" and row.get("destino_vision") == "excluir" for row in figures),
        "figures_queue_visible": sum(row.get("estado") == "cola_revision" and row.get("destino_vision") != "excluir" for row in figures),
        "panels_total": len(panels),
        "panels_crop_available": sum(row["crop_available"] for row in panels),
        "figures_original_available": sum(row["image_available"] for row in figures),
        "figures_original_files_local": sum(public_image_path(repo, row.get("imagen", ""))[1] for row in figures),
        "descriptors_v03_source": len(descriptors),
        "descriptors_v03_usable": len(usable),
        "descriptors_v03_review": sum(row["revisar_v03_bool"] for row in usable),
        "descriptors_v03_review_all": sum(as_bool(row.get("revisar_v03")) for row in descriptors),
        "figure_technique_counts": {
            technique: sum(technique in row["tecnicas_normalizadas"] for row in figures)
            for technique in sorted({tech for row in figures for tech in row["tecnicas_normalizadas"]}, key=str.casefold)
        },
        "figures_without_technique": sum(not row["tecnicas_normalizadas"] for row in figures),
        "visible_figures_without_technique": sum(not row["tecnicas_normalizadas"] for row in visible_figures),
        "figures_without_raw_technique": sum(not row.get("tecnicas", "").strip() for row in figures),
        "visible_figures_without_raw_technique": sum(not row.get("tecnicas", "").strip() for row in visible_figures),
        "visible_figure_technique_counts": visible_technique_counts,
        "top_techniques": top_techniques,
        "technique_other_visible_figures": sum(any(name not in top_techniques for name in row["tecnicas_normalizadas"]) for row in visible_figures),
        "technique_family_visible_counts": {
            family: sum(family in row["familias_tecnicas"] for row in visible_figures)
            for family in TECHNIQUE_FAMILIES
        },
        "technique_families": TECHNIQUE_FAMILIES,
        "technique_aliases": {alias: list(names) for alias, names in sorted(TECHNIQUE_ALIASES.items())},
        "non_technique_markers": sorted(NON_TECHNIQUE_MARKERS),
    }
    (output / "figuras_summary.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=REPO / "curation")
    parser.add_argument("--output-dir", type=Path, default=HERE / "data")
    parser.add_argument("--images-csv", type=Path, default=REPO / "producto" / "imagenes" / "descargas.csv")
    args = parser.parse_args()

    tables = {name: read_csv(args.source_dir / filename) for name, filename in TABLES.items()}
    for name, rows in tables.items():
        clean_table_text(name, rows)
    # The Atlas includes evidence-bearing E1/E2 articles only. Do not infer
    # exclusions from title keywords.
    articles = [r for r in tables["articulos"] if r.get("tier") in {"E1", "E2"}]
    kept_pmcs = {r.get("pmcid", "") for r in articles}
    # Retain evidence rows belonging to the included E1/E2 article set.
    for name in ("paneles", "descriptores", "espectros"):
        tables[name] = [r for r in tables[name] if r.get("pmcid", "") in kept_pmcs]

    image_status: dict[tuple[str, str], bool] = {}
    if args.images_csv.exists():
        for row in read_csv(args.images_csv):
            image_status[(row.get("pmcid", ""), row.get("image_file", ""))] = row.get("ok") == "1"
    for panel in tables["paneles"]:
        panel["imagen_local"] = image_status.get(
            (panel.get("pmcid", ""), panel.get("image_file", "")), False
        )

    model_path = args.source_dir / MODEL_TABLE
    if model_path.exists():
        model_rows = read_csv(model_path)
        model_by_image = {
            (row.get("pmcid", ""), row.get("image_file", "")): row
            for row in model_rows
            if row.get("pmcid", "") in kept_pmcs
        }
        for panel in tables["paneles"]:
            model_row = model_by_image.get((panel.get("pmcid", ""), panel.get("image_file", "")))
            if model_row:
                panel["clase_modelo"] = model_row.get("clase_modelo", "")
                panel["microscopia"] = model_row.get("microscopia", "")
                panel["fold"] = model_row.get("fold", "")
    tables["articulos"] = articles

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        (args.output_dir / f"{name}.json").write_text(
            json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    new_stats = build_new_sources(REPO, args.output_dir)
    summary = {
        "articles": len(articles),
        "panels": len(tables["paneles"]),
        "descriptors": len(tables["descriptores"]),
        "spectra": len(tables["espectros"]),
        **new_stats,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    model_dir = REPO / "producto" / "modelo"
    model_status = {"available": all((model_dir / name).is_file() for name in MODEL_FILES)}
    (args.output_dir / "model-status.json").write_text(
        json.dumps(model_status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    comparison_dir = REPO / "modelos" / "comparacion"
    for source_name, output_name in (
        ("ANALISIS_04_RECORTES.json", "analisis_recortes.json"),
        ("ANALISIS_FUSION_04.json", "analisis_fusion_04.json"),
        ("ANALISIS_04_RECORTES.md", "analisis_04_recortes.md"),
        ("entrada_kabre/06_nffa/metricas_06.json", "metricas_06_nffa.json"),
    ):
        source = comparison_dir / source_name
        if source.is_file():
            shutil.copyfile(source, args.output_dir / output_name)
    nffa_source = comparison_dir / "ANALISIS_06_NFFA.md"
    if nffa_source.is_file():
        shutil.copyfile(nffa_source, args.output_dir / "analisis_06_nffa.md")
    final_card = REPO / "modelos/modelo_final/02_onnx/modelo_card.json"
    if final_card.is_file():
        shutil.copyfile(final_card, args.output_dir / "modelo_card_final.json")
    (args.output_dir / "round3_sources.json").write_text(
        json.dumps({"recortes": (comparison_dir / "ANALISIS_04_RECORTES.json").is_file(), "fusion": (comparison_dir / "ANALISIS_FUSION_04.json").is_file(), "nffa": nffa_source.is_file()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    onnx_dir = REPO / "producto" / "modelo_onnx"
    model_payload = onnx_dir / "02_onnx"
    model_files = [model_payload / name for name in ("ensamble3_int8.onnx", "clases.json", "preprocesado.json", "modelo_card.json")]
    model_files.append(onnx_dir / "03_verificacion" / "verificacion_onnx.csv")
    verification_dir = onnx_dir / "03_verificacion" / "entradas"
    test_images = list(verification_dir.glob("*.png")) if verification_dir.is_dir() else []
    runtime_dir = HERE / "vendor" / "onnxruntime-web"
    runtime_files = [runtime_dir / name for name in ("ort.min.js", "ort-wasm-simd-threaded.mjs", "ort-wasm-simd-threaded.wasm", "LICENSE.txt", "package.json")]
    try:
        runtime_package = json.loads((runtime_dir / "package.json").read_text(encoding="utf-8"))
        runtime_version = runtime_package.get("version")
    except (OSError, json.JSONDecodeError):
        runtime_version = None
    demo_available = all(path.is_file() for path in [*model_files, *runtime_files]) and len(test_images) >= 20 and runtime_version == "1.30.0"
    (args.output_dir / "demo-status.json").write_text(
        json.dumps({"available": demo_available, "test_images": len(test_images), "runtime_version": runtime_version, "reason": "Faltan archivos locales del modelo, verificación o runtime fijado" if not demo_available else "ready"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

