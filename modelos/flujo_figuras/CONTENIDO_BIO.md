# Contenido biológico: informe descriptivo

Estado: **COBERTURA LOCAL PARCIAL**.
Plan: 2066 figuras; revisadas localmente: 1800; sin JSONL local: 266.
B061–B069 se comunicaron como completados en un ZIP; el usuario indicó omitir su revisión. No se infieren etiquetas de archivos ausentes.

No se generan variantes B ni listas de exclusión. figuras_vision.csv permanece intacto.

## Figuras por contenido

| Contenido | Figuras |
|---|---:|
| particulas | 1743 |
| biologico | 2 |
| particulas_en_contexto_biologico | 23 |
| mixto | 15 |
| indeterminado | 17 |

## Cruce con el modelo de clase

2100 imágenes de 1641 artículos. Unión: pmcid + archivo en tipología, luego pmcid + figura normalizada en bio_plan.
Las siguientes tablas cuentan imágenes del índice, no artículos únicos ni recortes. Indeterminado y falta de anotación se mantienen separados.

### Por clase de portador

| Grupo | Total | particulas | biologico | particulas_en_contexto_biologico | mixto | indeterminado | Sin revisión/enlace local |
|---|---:|---:|---:|---:|---:|---:|---:|
| inorganico | 371 | 309 | 0 | 9 | 0 | 0 | 53 |
| lipidico | 319 | 262 | 0 | 2 | 1 | 3 | 51 |
| nanomaterial | 953 | 807 | 0 | 12 | 10 | 6 | 118 |
| polimerico | 457 | 365 | 2 | 0 | 4 | 8 | 78 |

### Por fold

| Grupo | Total | particulas | biologico | particulas_en_contexto_biologico | mixto | indeterminado | Sin revisión/enlace local |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 422 | 353 | 0 | 4 | 2 | 6 | 57 |
| 1 | 423 | 360 | 0 | 5 | 4 | 6 | 48 |
| 2 | 416 | 334 | 0 | 3 | 1 | 1 | 77 |
| 3 | 417 | 348 | 0 | 4 | 5 | 4 | 56 |
| 4 | 422 | 348 | 2 | 7 | 3 | 0 | 62 |

## Validación y límites

- Esquema, longitud y secuencia n: PASS (60 lotes).
- Identificadores únicos, cruce sin multiplicación/pérdidas, un fold por artículo: PASS.
- Estado del cruce: {'revisada': 1800, 'sin_anotacion_local': 266, 'sin_enlace_bio': 34}.
- Lotes sin JSONL: B061, B062, B063, B064, B065, B066, B067, B068, B069.
- La validación estructural no certifica la exactitud semántica de las etiquetas visuales.
- Procedencia, cruce y hashes se conservan en resultados/codex; sin recomendaciones de exclusión para entrenar.
