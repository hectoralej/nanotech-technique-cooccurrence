# Preregistro de hipótesis

**Fecha de registro: 2026-10-09**, antes de extraer texto completo de ningún artículo y antes de calcular
cualquier prevalencia o co-ocurrencia de técnicas.

**Lo que ya se había visto cuando se registró:** únicamente los conteos de la etapa de búsqueda (cuántos artículos
de acceso abierto devuelve cada consulta por familia; ver `data/ids/query_totals.json`) y la prueba de acceso
(un artículo descargado como prueba, PMC7464915, sin análisis). Ninguna técnica había sido detectada en ningún artículo.

Las hipótesis son las del brief (sección 6), tal cual, con la regla de decisión que se usará para declararlas
confirmadas, refutadas o inconclusas. Cualquier desviación posterior se documenta en `REPORT.md` como tal.

## Definiciones usadas en las reglas de decisión

- "Técnica reportada" = definición primaria: aparece en Métodos **y** (Resultados **o** pie de figura).
- P(B|A) con IC de Wilson 95 %. "Mayor que" significa que los IC 95 % de ambas probabilidades no se solapan **o** que
  el OR de Mantel-Haenszel/logístico entre las condiciones tiene IC 95 % que excluye 1, en la dirección indicada.
- Solo se evalúan celdas con n(A) ≥ 20; si no hay celdas evaluables, la hipótesis se declara **inconclusa**.
- Si el detector de una técnica involucrada tiene recall < 0,85 en el conjunto de validación, la conclusión se marca
  "con detector poco fiable".
- Comparaciones múltiples: Benjamini-Hochberg al 5 % cuando la hipótesis se contraste con varios pares.

## Hipótesis

| # | Hipótesis (dirección) | Regla de decisión |
|---|---|---|
| H1 | Dado TEM, P(DLS) es alta en todas las familias orgánicas (liposomas, LNP, SLN/NLC, PLN, poliméricas) y mayor que P(DLS \| SEM). | Confirmada si P(DLS\|TEM) ≥ 0,5 en todas las familias orgánicas evaluables y P(DLS\|TEM) > P(DLS\|SEM) en la agregada y en la mayoría de familias. |
| H2 | Dado cryo-EM, P(SAXS) es mayor que dado TEM seco en LNP y liposomas. | Confirmada si P(SAXS\|cryoEM) > P(SAXS\|TEM) en LNP y en liposomas (TEM = detectado sin subbandera cryo). Inconclusa si n(cryoEM) < 20 en alguna. |
| H3 | Dado TEM en inorgánicas, UV-Vis y XRD son más probables que en lípidos y polímeros. | Confirmada si P(UVVis\|TEM) y P(XRD\|TEM) en inorgánicas superan a las de LNP, liposomas, SLN/NLC y poliméricas. |
| H4 | Dado SEM, EDS es más probable que dado TEM en inorgánicas; en orgánicas EDS es raro. | Confirmada si P(EDS\|SEM) > P(EDS\|TEM) en inorgánicas y P(EDS\|·) < 0,10 en las familias orgánicas. |
| H5 | DLS y zeta están fuertemente asociados (phi alto) por compartir equipo. | Confirmada si phi(DLS, zeta) ≥ 0,3 agregada y en ≥ 4 familias, y es de las asociaciones más altas entre las técnicas de núcleo. |
| H6 | FTIR y DSC/TGA son más frecuentes en poliméricas y SLN/NLC que en LNP. | Confirmada si la prevalencia marginal de ambas en poliméricas y SLN/NLC supera la de LNP (IC no solapados). |
| H7 | En AAV, cryo-EM o TEM se asocian con AUC o qPCR más que con DLS; no hay SEM. | Confirmada si P(AUC∪qPCR \| EM) > P(DLS \| EM) y la prevalencia de SEM en AAV < 0,05. (Extendido: depende de la fiabilidad de AUC/qPCR.) |
| H8 | P(zeta \| DLS) < 1 (a nivel de artículo). | Confirmada si el IC superior de P(zeta\|DLS) < 0,95 en la agregada. |
| H9 | Co-ocurrencia micrografía + espectro **en la misma figura**: < 25 % de los artículos con EM, con alta variación por familia. | Proxy: figura/pie con término de microscopía y de espectroscopia (UV-Vis, FTIR, XRD, NMR, EDS, SAXS, Raman). Confirmada si la proporción agregada < 0,25 y el rango entre familias > 0,10. |
| H10 | Estado de preparación de EM difiere por familia: lípidos con cryo, polímeros con TEM teñido o SEM seco, inorgánicas con TEM seco. | Confirmada si, entre artículos con EM, P(cryo) es la más alta en LNP/liposomas, y P(neg_stain ∪ SEM) en poliméricas supera a la de lípidos, y P(dried_unstained, sin cryo/tinción) es la mayor en inorgánicas. |

## Análisis y decisiones que se fijan antes de ver los datos

- Muestreo: aleatorio estratificado proporcional (familia primaria × {2018-2021, 2022-2026} × {CC BY, resto}),
  semilla 20261009; criterio de parada de `config/sampling.yaml`.
- Técnica reportada: definición primaria arriba; sensibilidades: solo Métodos, cualquier sección, solo pie de figura.
- Familia primaria: la más mencionada en título+resumen; sensibilidad con duplicación multietiqueta.
- Matrices por familia + agregada con OR de Mantel-Haenszel por familia + regresión logística con errores robustos
  agrupados por revista, `B ~ A + familia + año`.
- Los diccionarios se pueden ajustar **solo** con el piloto y el conjunto de validación, nunca con las prevalencias
  de la muestra completa.

---

## Enmiendas (con fecha; todas anteriores al cálculo de cualquier co-ocurrencia)

### Enmienda 1: definición principal de "técnica reportada" (2026-10-09)

- **Qué cambia:** la definición principal pasa de `primary` (Métodos **y** Resultados/pie) a `body_any`
  (Métodos **o** Resultados **o** pie de figura/tabla; se excluyen Introducción, Discusión y resumen).
  `primary` se conserva como análisis de sensibilidad (a), junto con "solo Métodos", "cualquier sección" y "solo pie".
- **Por qué:** el conjunto de validación (56 artículos, 8 por familia) mostró que la definición `primary` tiene recall
  < 0,85 frente a "usada y mostrada" en 9 de las 13 técnicas con positivos, por razones estructurales: muchos
  artículos nombran la técnica en una sola sección (p. ej. describen el DLS en Métodos y en Resultados dicen solo
  "tamaño hidrodinámico y PDI", o dan el SEM solo en Resultados). Con `body_any` el recall fue 1,00 en esas 13 técnicas.
- **Lo que se había visto:** solo métricas del detector contra el conjunto de validación; ninguna prevalencia ni
  co-ocurrencia de la muestra. Las hipótesis H1 a H10 y sus reglas de decisión no cambian; donde la regla decía
  "reportada" ahora se lee `body_any`.
- **Otras desviaciones de método registradas aquí:** (i) la consulta de AAV se restringió a artículos con términos de
  caracterización/manufactura del vector, porque el 100 % de una muestra inicial de 8 artículos eran estudios de
  neurociencia/hígado donde el AAV es solo un vector (8.459 → 985 resultados en la búsqueda); (ii) la familia
  polimérica incluye micelas, quitosano, dendrímeros y nanogeles; (iii) el conjunto de validación tiene 56 artículos
  (7 familias × 8) porque "50 con ≥ 8 por familia" es incompatible; (iv) la anotación del conjunto de validación es
  **provisional, de un solo anotador (Claude)**, no la doble anotación humana que pide el brief.
