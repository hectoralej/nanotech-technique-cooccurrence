# nanotech-technique-cooccurrence

Matriz de probabilidades condicionales entre técnicas de caracterización (TEM, SEM, cryo-EM, DLS, zeta, SAXS, XRD, FTIR…)
en artículos de acceso abierto sobre nanoportadores (LNP, liposomas, SLN/NLC, PLN, poliméricas, inorgánicas, AAV),
construida con datos medidos de Europe PMC. Proyecto del curso de Quimioinformática (nanoinformática y nanoentrega).

**Empiece por `REPORT.md`** (método, resultados, hipótesis H1–H10, implicaciones para el esquema de la base y limitaciones).
`PREREGISTRATION.md` tiene las hipótesis fechadas antes del análisis y sus enmiendas.

> **Pendiente para el equipo:** la validación del detector usa una anotación **provisional de un solo anotador (Claude)**.
> Falta la doble anotación humana: ver `GOLD_GUIDELINES.md` y `data/gold_set_human_template.csv`.

## Estructura

| Ruta | Contenido |
|---|---|
| `config/` | `families.yaml` (consultas), `techniques.yaml` (taxonomía y regex), `sampling.yaml` (semilla, estratos, parada, definición principal) |
| `src/` | `search`, `fulltext`, `detect`, `sample`, `extract`, `gold`, `stats`, `analyze`, `hypotheses`, `plots`, `report` |
| `tests/` | pruebas del detector (frases con las trampas del brief) y de la estadística (datos sintéticos de probabilidades conocidas) |
| `data/` | `articles.csv`, `pairs.csv`, `pairs_sensitivity.csv`, `evidence.csv`, `prevalence.csv`, `hypotheses.csv`, `gold_*.csv`, `ids/`, `cell_pmcids/` |
| `figures/` | figuras 1–7 en PNG y SVG; HTML interactivo (con modo claro/oscuro) para 1, 2, 5 y 6 |
| `logs/queries.jsonl` | cada consulta y descarga con fecha |

## Reproducir

Requiere Python ≥ 3.11 (`pip install -r requirements.txt`). Con conexión a Europe PMC:

```bash
make all            # Linux/macOS
```
```powershell
.\run_all.ps1       # Windows (sin make)
```

La primera ejecución descarga ≈ 2.400 textos completos a `data/cache/` (≈ 25 min a ~1,5 artículos/s; ≤ 3 solicitudes/s con
`User-Agent` identificable). La caché no se redistribuye (`.gitignore`). La semilla está fija en `config/sampling.yaml`.

En Windows las rutas largas se manejan con el prefijo `\\?\` (ver `src/common.py`).

## Cumplimiento

Solo artículos con `OPEN_ACCESS:y` y licencia registrada, vía los servicios web de Europe PMC. No se redistribuye texto
completo ni figuras: se guardan metadatos, banderas por sección y fragmentos de evidencia de ≤ 25 palabras.
