# Estado de la curación (2026-10-12)

**Repositorio: 86 artículos** (26 del piloto + 21 de la ronda 1 + 16 de la ronda 2 + 23 de la lista de verificación humana, tras la auditoría de Claude). Todas las métricas son **provisionales** hasta la revisión humana.

**Actualización del 2026-10-20:** el repositorio tiene **87 artículos** (68 CC BY, 19 NC/ND, 0 en conflicto). Cambios de hoy: el rescate del medio no declarado (`rescue.py`, regla 1 de `POLITICA_PUERTA.md`) aportó 1 artículo; la regla de duplicados se hizo más estricta (antes sacaba artículos distintos por coincidir en 3 valores redondeados) y recuperó otro; se descartó a mano PMC11377347 por varias inconsistencias. Quedan **14 artículos que la revisión de Codex aprueba y que mi extracción no**; en casi todos Sonnet extrajo con una sola pasada y le faltó DLS o zeta útil (límite de 12 filas, valores en el suplemento, identidad de muestra dudosa).

**Lista para la revisión humana: `curation/verificacion_humana_80.csv`** (78 artículos, solo licencia CC BY, con el DOI como enlace). Guía en `GUIA_REVISION.md`. La clave del modelo está en `work/clave_modelo.csv`: **no abrirla hasta terminar**.

**Corrección de licencias (2026-10-18):** el clasificador trataba los códigos cortos de Europe PMC («cc by-nc», «cc by-nc-nd») como CC BY. Ya está corregido. Con la regla nueva el repositorio tiene 66 artículos en verde (CC BY), 18 en amarillo (NC o ND) y 2 en conflicto. Las cifras de licencia que se dieron antes (43 verdes, 20 en conflicto) estaban mal.

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

1. **Revisión humana** de `verificacion_humana_80.csv` (78 artículos): dos personas, cada una en su copia, sin ver la del otro. Luego `python -m curation.human_sheet agreement a.csv b.csv` y `vs_model a.csv`. Revisar también las exclusiones a mano (`manual_review.csv`, `verificacion_excluidas.csv`). Sin eso no se certifica ningún umbral.
2. **Licencias:** de los 86 artículos del repositorio, 18 son CC BY-NC/-ND (amarillo) y 2 tienen conflicto entre fuentes. Las figuras solo se redistribuyen de los 66 en verde. El editor bloquea la consulta automática en la mayoría de los casos (403), así que la verificación es con Europe PMC y el XML del artículo; la página del editor se revisa a mano en la lista de verificación.
3. **Vacíos:** inorgánicas (2 artículos) y SAXS (7 mediciones en 3 artículos). Necesitan búsqueda dirigida de artículos nuevos (paso 7, no iniciado).
4. **Archivo abierto en Excel:** `articles_curated.csv` estaba abierto y no se pudo sobrescribir. La versión nueva es `articles_curated_nuevo.csv`; al cerrar Excel, renombrarla.
5. Quedan 530 candidatos sin leer con modelos (`pending.csv`) si se quisiera ampliar más. Hay 148 casi-aprobados en `near_miss.csv`.

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
