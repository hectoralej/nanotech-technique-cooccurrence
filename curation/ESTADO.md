# Estado de la curación (2026-10-12)

**Repositorio: 63 artículos** (26 del piloto + 21 de la ronda 1 + 16 de la ronda 2, tras la auditoría de Claude). Todas las métricas son **provisionales** hasta la revisión humana.

## Hecho

| Paso | Estado |
|---|---|
| Prefiltro (2.396 → 766 candidatos) | Hecho |
| Piloto al azar (100 artículos, dos pasadas Haiku + Sonnet, arbitraje) | Hecho (26 en el repositorio) |
| Filtro barato por código (`cheap_filter.py`) | Hecho sobre los 618 candidatos restantes; en el piloto, tabla con tamaño y zeta + medio junto a DLS y zeta = 83 % de aprobación |
| Ronda 1 (44 artículos): Haiku con paquete corto → Sonnet con paquete completo en los que pasan o casi → arbitraje de la puerta | Hecho (21 en el repositorio) |
| Ronda 2 (31 artículos): Sonnet directo con paquete completo → Haiku como segunda lectura de los aprobados → arbitraje | Hecho (16 en el repositorio) |
| Auditoría de Claude | 3 artículos excluidos a mano (`manual_review.csv`) y regla por código: micrografía, DLS y zeta de una misma muestra |
| Salidas (`articles_curated`, `near_miss`, `excluded`, `pending`, `measurements`, grupos de equivalencia, Word APA 7, gráficos, INFORME.md) | Generadas |

## Pendiente

1. **Revisión humana (Bryan y Carlos)** de `hoja_revision_humana.csv` (60 artículos del conjunto H001–H015, que aún no pasaron por los modelos) y de los 3 excluidos a mano. Sin eso no se certifica ningún umbral.
2. **20 de los 63 artículos tienen conflicto de licencia** entre Europe PMC y el XML o el editor (CC BY-NC / -ND). No se redistribuyen figuras de ellos hasta revisarlo.
3. **Vacíos:** inorgánicas (2 artículos) y SAXS (7 mediciones en 3 artículos). Necesitan búsqueda dirigida de artículos nuevos (paso 7, no iniciado).
4. **Archivo abierto en Excel:** `articles_curated.csv` estaba abierto y no se pudo sobrescribir. La versión nueva es `articles_curated_nuevo.csv`; al cerrar Excel, renombrarla.
5. Quedan 591 candidatos sin leer con modelos (`pending.csv`; incluye los 60 del conjunto humano) si se quisiera ampliar más. Hay 89 casi-aprobados en `near_miss.csv`.

## Cómo reanudar una ronda

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m curation.select_direct R3 "SLN_NLC=6,polymeric=6"      # elige artículos (nivel A del filtro barato) y escribe lotes QB##
# Sonnet: un agente por lote QB## (paquete completo, extract_common.md + variant_B.md) -> work/llm/B/QB##.json
python -m curation.validate_llm B
# segunda lectura barata de los aprobados: lotes QA## con paquete corto (cheap_filter.write_short_packets) -> work/llm/A/QA##.json
python -m curation.validate_llm A
python -m curation.merge conflicts main --gate-only                # solo desacuerdos de la puerta y de valores
# Sonnet: un agente por archivo MC### (arbitrate.md) -> work/llm/C/MC###.json
python -m curation.finalize all ; python -m curation.score
python -m curation.build_outputs
```

## Consumo (tokens de subagentes; ver `consumption_log.csv`)

Ampliación (rondas 1 y 2): 4,0 millones de tokens (Haiku 1,2 M, Sonnet 2,8 M) para 75 artículos nuevos y 143 lecturas. Proyecto completo hasta hoy: 10,5 millones.
