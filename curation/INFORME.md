# Informe de curación de calidad (fase 2) — PROVISIONAL

> **Alcance de estas cifras:** 175 de los 766 candidatos leídos con modelos (100 al azar como piloto y 75 elegidos con un filtro barato por código), 63 artículos en el repositorio. La validación humana (Bryan y Carlos) **no está hecha**: todas las métricas son provisionales.

## 1. Embudo

- Procesados antes: 2.396 → sin AAV/virus/fuera de alcance → **766 candidatos** con señal de micrografía + DLS + zeta (prefiltro, `data/funnel.csv`).
- Con extracción LLM: **175**. Pasan la puerta estricta: **73**. En el repositorio (≥ 60 puntos y auditoría): **63**. 24 artículos se descartaron tras una sola lectura (no se gasta una segunda en ellos).
- Principales motivos de salida: DLS sin valor numerico con medio declarado (68); sin micrografia util (19); zeta sin valor numerico con medio o pH declarado (10); micrografia y DLS/zeta son de muestras distintas (3); el nanoportador es una herramienta, no el objeto de estudio (2); desacuerdo no resuelto (2); portador viral o caracterizacion dependiente de PCR (1).

![Embudo](grafico_embudo.png)

### Rendimiento por grupo

| Grupo | Extraídos | En el repositorio | % |
|---|---|---|---|
| piloto (azar) | 100 | 26 | 26 % |
| ronda 1 | 44 | 21 | 48 % |
| ronda 2 | 31 | 16 | 52 % |

El piloto se eligió al azar; las rondas 1 y 2 se eligieron con un filtro por código (tabla con tamaño y zeta, y medio declarado junto a DLS y zeta), por eso rinden más. No son comparables como una tasa de la población: la tasa del azar (piloto) es la que describe a los 766 candidatos.

![Rendimiento](grafico_rendimiento_por_ronda.png)

## 2. Niveles y familias

Niveles: S 8, A 48, B 7. Por familia: LNP 14, PLN 13, SLN_NLC 15, inorganic 2, liposome 8, polymeric 11.
Micrografía del repositorio: TEM 40, SEM 19, cryo 4 artículos (proporción SEM 30 %); variantes registradas: TEM_negstain 74, SEM 42, TEM_prep_not_declared 18, TEM_dried_unstained 18, cryoTEM 9, HRTEM 2, STEM 1.

![Niveles](grafico_niveles_por_familia.png)

## 3. Técnicas, lotes y licencias

- Combinaciones de técnicas útiles (repositorio): `TEM+DLS+zeta` ×28; `SEM+DLS+zeta` ×10; `cryo+DLS+zeta` ×3; `TEM+DLS+zeta+FTIR` ×3; `SEM+DLS+zeta+UVVis` ×2; `SEM+DLS+zeta+FTIR` ×2.
- Cobertura de lotes (formulaciones con DLS o zeta medidos por artículo): 1: 7, 2: 11, 3: 3, 4: 15, 5: 4, 6: 7, 8: 5, 9: 1, 10: 2, 11: 2, 12: 6 (clave: nº de formulaciones: artículos).
- Licencia (verificada contra Europe PMC, XML del artículo y página del editor cuando fue accesible): verde 43, conflicto 20. Solo `verde` permite redistribuir figuras.
- DOI que no resuelven: 0.

## 4. Pistas secundarias y expansión

- **SAXS:** 7 mediciones de SAXS entre los artículos extraídos; 7 en 3 artículos del repositorio: **sigue sin haber muestra para evaluar un subconjunto de calidad**; con la prevalencia observada en el análisis previo (≈ 1 % de los artículos) se necesita una búsqueda dirigida de SAXS (no iniciada).
- **Inorgánicas:** el repositorio tiene 2 artículos de esta familia. Es el vacío más claro; se necesita una búsqueda dirigida (no iniciada).
- **Expansión dirigida (paso 7):** no iniciada. Las rondas 1 y 2 salieron de los artículos ya descargados; no se buscaron artículos nuevos.

## 5. Efecto del material suplementario

- Europe PMC marca material suplementario en el 57 % de los candidatos. El texto completo de Europe PMC **no incluye** ese material.
- 25 de 151 artículos con dos pasadas (17 %) tienen mediciones cuyos valores solo están en el suplemento o en figuras sin cifras: se marcan `valores_solo_en_SI` y **no cumplen la puerta**. No se descargó el suplemento; es una limitación clave y subestima el repositorio.

## 6. Cómo se trabajó y qué costó

- Filtro barato por código (0 tokens): tabla con tamaño y zeta, y medio declarado junto a DLS y zeta. En el piloto, ese criterio dejaba pasar a 19 de 23 artículos que luego aprobaron la puerta (83 %).
- Ronda 1: Haiku sobre un paquete corto (solo frases clave, pies de figura y tablas), luego Sonnet sobre el paquete completo en los que pasaban o casi. Haiku descartó por error a 8 de los 23 que Sonnet aprobó (recall 65 %), así que la ronda 2 fue directo a Sonnet y Haiku se usó como segunda lectura de los aprobados.
- Tokens de subagentes: 10.5 millones en total (haiku 4.5 M, sonnet 6.0 M). Por artículo leído: haiku ≈ 31 mil, sonnet ≈ 34 mil.
- Auditoría de Claude sobre lo que agregaron los agentes: 3 artículos excluidos a mano (`manual_review.csv`; Bryan y Carlos pueden revertirlos) y una regla nueva por código: la micrografía, el DLS y el zeta deben ser de una misma muestra.

## 7. Limitaciones y qué falta validar

- Falta la revisión humana de los 60 artículos (`hoja_revision_humana.csv`) y con ella los umbrales de precisión de la puerta (≥ 0,95), kappa de variante/grupo (≥ 0,80) y licencia (100 %). Mi auditoría no es independiente de los modelos.
- Las rondas 1 y 2 usaron una pasada sobre un extracto corto (Haiku) o una sola pasada completa (Sonnet) según el caso, y arbitraje solo de la puerta y los valores; los grupos de equivalencia salen de la pasada de Sonnet.
- Dos pasadas con modelos de la misma familia comparten sesgos; el arbitraje usó Sonnet (no un modelo más fuerte).
- Solo se procesaron los artículos ya descargados (2.396).
- Los DOI se comprobaron con la respuesta de `doi.org` (redirección), no con la página final del editor.
