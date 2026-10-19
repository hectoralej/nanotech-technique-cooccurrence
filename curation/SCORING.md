# Puntuación y reglas fijadas ANTES de ver resultados de la extracción

**Fecha de registro: 2026-10-10.** Se calcula de forma determinista (`curation/score.py`) a partir de los campos que sobreviven a la
verificación de citas y al arbitraje. Ningún modelo opina sobre la puntuación. No se ajusta para obtener un número deseado; si se cambia
algo, se anota aquí como enmienda con fecha.

## Puerta (obligatoria)

El artículo entra al repositorio principal solo si cumple las tres:

1. **Micrografía útil** (TEM y variantes, o SEM): hay una medición de micrografía con `shown_as` = `figure_panel` o `raw_curve`, sobre una muestra
   `nanoparticle_loaded` o `nanoparticle_empty` (no control ni componente puro), con variante identificada (el estado de preparación puede ser
   `no_declarado`) y con enlace a la formulación `explicit` o `inferred`.
2. **DLS útil:** valor numérico de tamaño (Z-promedio u otra magnitud declarada) **con medio declarado**, para una muestra identificable.
3. **Zeta útil:** valor numérico **con medio o pH declarado**, para una muestra identificable.

Si DLS o zeta tienen valor pero no medio: **dato dudoso** (`quality_flags` = `medio_no_declarado`); no cumple el criterio estricto y el artículo va a
`near_miss.csv`. Artículos con solo microscopía, o sin DLS o sin zeta: fuera del principal.

## Puntos (100)

| Bloque | Máx. | Reglas |
|---|---|---|
| Micrografía | 20 | útil 10; estado de preparación declarado (no `no_declarado`) 5; tamaño medido con n de partículas o histograma 5 |
| DLS | 20 | valor 10; medio **y** al menos una condición (temperatura, ángulo o dilución) 5; réplicas o SD 5 |
| Zeta | 20 | valor 10; medio o pH 5; réplicas o SD 5 |
| Enlace a formulación | 15 | composición y parámetros declarados y enlazados a la muestra medida (`explicit`): 15; `inferred`: 8; `paper_level`: 0 |
| Variedad de lotes | 10 | formulaciones o condiciones distintas con datos medidos (DLS o zeta): 1 → 0; 2–3 → 5; ≥ 4 → 10 |
| Técnicas complementarias | 15 | por cada técnica complementaria útil **sobre la partícula** (no componente puro, no ensayo): espectro mostrado como dato 3; solo valor o lista de picos 1; tope 15. Complementarias: UV-Vis (solo tipo (a) intrínseca), FTIR, XRD, EDS (inorgánicas), DSC/TGA (poliméricas, SLN/NLC), Raman, NMR, XPS, NTA |

**Niveles:** S ≥ 85; A 70–84; B 60–69; < 60 o sin puerta: fuera del principal. SEM y TEM puntúan igual; se reporta la proporción de SEM por nivel.

## Reglas de agrupación equivalentes (clave del grupo)

`technique | variante | magnitud | clase de identidad de muestra | condiciones que cambian la interpretación`; una condición no declarada es el valor
`no_declarado` y **separa** el grupo (nunca se asume que coincide con otra). Detalle en `curation/equivalence.py`.

## Decisiones de interpretación (declaradas aquí para que se puedan cuestionar)

- **Virus y PCR:** se excluyen del repositorio los artículos de AAV y de otros vectores virales o partículas virales (el portador es un virus, VLP o fago) y
  aquellos cuya caracterización depende de PCR (títulos, copias de genoma). Un artículo de LNP/liposomas con RT-qPCR solo como lectura biológica de
  expresión **no** se excluye por eso: se marca `pcr_lectura_biologica` y se reporta cuántos artículos se perderían si se aplicara la lectura estricta.
- **Modelos:** pasada A con Haiku, pasada B con Sonnet (prompts distintos y orden de lectura distinto), arbitraje con Sonnet con instrucciones más estrictas.
  No se usó un modelo más fuerte para el arbitraje (decisión del usuario: Haiku y Sonnet).
- **Validación humana:** mientras `hoja_revision_humana.csv` no esté completada por dos personas, todas las métricas son **provisionales**.
