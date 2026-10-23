#!/usr/bin/env python3
"""Build the static atlas data from the four canonical curation CSVs."""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
from pathlib import Path


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
    summary = {
        "articles": len(articles),
        "panels": len(tables["paneles"]),
        "descriptors": len(tables["descriptores"]),
        "spectra": len(tables["espectros"]),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    model_dir = REPO / "producto" / "modelo"
    model_status = {"available": all((model_dir / name).is_file() for name in MODEL_FILES)}
    (args.output_dir / "model-status.json").write_text(
        json.dumps(model_status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

