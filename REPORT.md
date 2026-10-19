# Co-ocurrencia de técnicas de caracterización en artículos de nanoportadores

> Informe generado por `python -m src.report` desde `data/`. Fecha de las consultas a Europe PMC: 2026-10-09 a 2026-10-09. Definición principal de «técnica reportada»: `body_any` (ver Enmienda 1 en `PREREGISTRATION.md`). Etiquetas: **[medido]** = salida de una consulta/cálculo registrado; **[literatura]** = tomado del brief con su fuente; **[inferido]** = proyección o interpretación.

> **Aviso principal (léalo antes de citar números):** la validación del detector usó una anotación **provisional de un solo anotador (Claude)**, no la doble anotación humana que pide el brief. Las métricas de fiabilidad son por eso optimistas y deben confirmarse con `GOLD_GUIDELINES.md`. Las técnicas *extendidas* no se validaron.

## 1. Resumen

- **[medido]** Muestra principal: 2.025 artículos de acceso abierto en alcance (de 2.141 procesados), 2018–2026, 7 familias, texto completo vía Europe PMC.
- **[medido]** Dado TEM, el DLS aparece en 87 % de los artículos orgánicos (IC95 % 84 %–90 %) frente a 52 % en inorgánicos: **el DLS es una etiqueta casi gratuita para lípidos y polímeros con TEM, no para inorgánicos**.
- **[medido]** DLS y zeta son la asociación más fuerte entre técnicas (phi = 0.76; P(zeta|DLS) = 85 %); la base debería capturarlas como un par.
- **[medido]** Solo 16 % de los artículos con micrografía (IC95 % 14 %–18 %) muestran micrografía y espectro en la misma figura (proxy por pie de figura); varía de 0 % a 31 % según la familia.
- **[medido]** Hipótesis (reglas del preregistro): H1 confirmada; H2 parcial; H3 confirmada; H4 parcial; H5 confirmada; H6 confirmada; H7 confirmada; H8 confirmada; H9 confirmada; H10 confirmada. Detalle en §3.6.
- **[medido]** SAXS es raro (29 de 2025 artículos): un módulo de SAXS **no tiene datos suficientes** con esta fuente; cryo-EM aparece en 6 % de los artículos (más en LNP).
- **[inferido]** Muchos artículos de las familias «liposoma», «inorgánica» y «AAV» no son estudios de nanoportadores sino usos del material como herramienta (p. ej., estructuras de proteínas en liposomas, vectores AAV en neurociencia); esto arrastra las matrices de esas familias (ver §5).

## 2. Método

### 2.1 Acceso y cumplimiento

- **[medido]** Prueba de acceso (2026-10-09): la API REST de Europe PMC respondió HTTP 200 a una consulta mínima (`pageSize=1`) y el endpoint `fullTextXML` entregó el texto completo de un artículo OA. El impedimento previo (429/403) venía del entorno en la nube, no del acceso local.
- Términos: la página de descargas de Europe PMC lista sus servicios web y FTP como vía para el subconjunto OA; las páginas de términos de la API REST devolvieron 403 desde WebFetch, así que **no pude leer la política de la API REST** (solo la lista de servicios permitidos). PMC prohíbe la recuperación sistemática fuera de cuatro servicios, y por eso solo se usó Europe PMC (no PMC directamente). Se respetó ≤ 3 solicitudes/s con `User-Agent` identificable, reintentos con espera exponencial y caché; solo artículos con `OPEN_ACCESS:y` y licencia registrada. No se redistribuye texto completo ni figuras (la caché cruda está en `.gitignore`).

### 2.2 Búsqueda, universo y muestreo

| Familia | Hits API (2015–2026, no revisión) |
|---|---|
| LNP | 3627 |
| Liposomas | 10112 |
| SLN/NLC | 1291 |
| PLN (híbridas) | 167 |
| Poliméricas | 8731 |
| Inorgánicas | 18503 |
| AAV | 985 |

Desviaciones de consulta registradas: AAV se restringió a artículos con términos de caracterización/manufactura del vector (sin restricción: 8.459 resultados, casi todos uso del AAV como vector); la familia polimérica añade micelas, quitosano, dendrímeros y nanogeles. Universo elegible: licencia registrada, 2018–2026, sin revisiones; familia primaria = la más mencionada en título+resumen (ver tabla). Muestreo aleatorio estratificado proporcional (familia primaria × {2018–2021, 2022–2026} × {CC BY, resto}), semilla 20261009, lotes de 100, parada cuando la mitad de ancho mediana del IC95 % de las celdas con n(A) ≥ 30 fue ≤ 0.08 y se alcanzó el mínimo de la familia.

| Familia | Población 2018–26 | Procesados | En alcance | Objetivo | Mitad de ancho mediana IC95 % (celdas n(A)≥30) | Celdas | CC BY (muestra) |
|---|---|---|---|---|---|---|---|
| LNP | 2606 | 399 | 374 | 300 | 0.068 | 98 | 64 % |
| Liposomas | 8338 | 396 | 349 | 300 | 0.060 | 84 | 68 % |
| SLN/NLC | 1107 | 220 | 214 | 150 | 0.057 | 112 | 76 % |
| PLN (híbridas) | 119 | 119 | 114 | 150 | 0.069 | 70 | 55 % |
| Poliméricas | 7283 | 396 | 380 | 300 | 0.062 | 126 | 72 % |
| Inorgánicas | 15426 | 310 | 303 | 300 | 0.068 | 126 | 74 % |
| AAV | 879 | 301 | 291 | 150 | 0.058 | 14 | 56 % |

**[medido]** Proporción CC BY en la población elegible 2018–2026: 71 %.

**[medido]** Todas las familias cumplieron el criterio de precisión (≤ 0,08) y el mínimo de artículos, salvo PLN: su población completa es de 119 artículos (114 en alcance, por debajo de los 150 del objetivo; se tomaron todos los disponibles). El tope de 4.000 artículos no se alcanzó. El conjunto de validación (56 artículos) está dentro de la muestra; por eso, como el muestreo toma «los siguientes sin procesar», la muestra es un prefijo del orden estratificado más algunos artículos adicionales aleatorios de la validación.

Exclusiones tras la descarga (muestra principal): tipo: case-report 34; tipo: correction 24; tipo: abstract 11; tipo: letter 8; tipo: retraction 8; no_fulltext 7; tipo: methods-article 7; tipo: news 4; tipo: data-paper 3; tipo: editorial 3; tipo: article-commentary 3; tipo: case-study 2; tipo: discussion 1; unparsable_or_short 1.

### 2.3 Detección

Diccionarios (regex con límites de palabra) en `config/techniques.yaml`, aplicados por sección (Métodos, Resultados, pies de figura/tabla, otras). Reglas para las trampas del brief: siglas ambiguas (SEM, TEM-1, NTA, AUC, EDS, TGA, DSC) aceptadas solo con el término completo en el artículo o contexto a ≤ 80 caracteres y con exclusiones (p. ej. «mean ± SEM», «Ni-NTA»); cryo-TEM se clasifica antes y se excluye del conteo de TEM; revisiones y artículos que no son de investigación se excluyen; se normalizan los guiones Unicode. Subbanderas (tinción negativa, HRTEM, FE-SEM, etc.) y una proxy de «micrografía y espectro en el mismo pie de figura».

Ajustes tras el piloto y la validación (permitidos por el preregistro): patrones de magnitudes derivadas (z-average, PDI, diffractograms, ZP) que cuentan solo en Resultados/pies; contenido de encabezados de tablas como «dato mostrado»; exclusión de listas de referencias y secciones administrativas; corrección de un patrón extendido erróneo (`Quant-?iT` coincidía con «quantitative»: RiboGreen/EE pasó de 59 % a 8 %, detectado revisando prevalencias, no en la validación: **las técnicas extendidas pueden tener errores no detectados**). No se usó ningún LLM (costo 0 USD).

### 2.4 Estadística

P(B|A) con IC de Wilson 95 %; OR con corrección de Haldane-Anscombe cuando hay una celda cero; lift, phi, Jaccard; prueba exacta de Fisher; BH (FDR 5 %) dentro de cada estrato; OR de Mantel-Haenszel estratificado por familia primaria; regresión logística `B ~ A + familia + año` con errores estándar robustos agrupados por revista; reglas de celda (n(A) < 20 atenuada; IC > 0,3 señalado); Apriori con soporte mínimo 0,05 por familia; prueba de Cochran-Armitage para tendencia; ajuste de Rogan-Gladen con sensibilidad/especificidad de la validación. Todas las funciones puras se prueban con datos sintéticos de probabilidades conocidas (`tests/test_stats.py`).

## 3. Resultados

### 3.1 Validación del detector

56 artículos (8 por familia, fuera del piloto). **Anotación provisional de un solo anotador (Claude); no hay kappa.** Verdad terreno: técnica usada y con datos presentados (`GOLD_GUIDELINES.md`).

| Técnica | Positivos | Precisión (body_any) | Recall (body_any) | F1 | Recall «primary» | Fiabilidad |
|---|---|---|---|---|---|---|
| cryoEM | 6 | 0.86 | 1.00 | 0.92 | 0.83 | ok |
| STEM | 0 |  |  |  |  | unvalidated |
| TEM | 22 | 0.96 | 1.00 | 0.98 | 0.73 | ok |
| SEM | 18 | 0.95 | 1.00 | 0.97 | 0.89 | ok |
| AFM | 3 | 1.00 | 1.00 | 1.00 | 0.67 | ok |
| DLS | 29 | 0.91 | 1.00 | 0.95 | 0.76 | ok |
| zeta | 29 | 1.00 | 1.00 | 1.00 | 0.79 | ok |
| NTA | 4 | 1.00 | 1.00 | 1.00 | 0.50 | ok |
| SAXS | 0 |  |  |  |  | unvalidated |
| XRD | 11 | 0.92 | 1.00 | 0.96 | 0.73 | ok |
| FTIR | 15 | 1.00 | 1.00 | 1.00 | 0.87 | ok |
| UVVis | 15 | 0.74 | 0.93 | 0.82 | 0.53 | precision_low |
| EDS | 5 | 1.00 | 1.00 | 1.00 | 0.60 | ok |
| DSC_TGA | 8 | 1.00 | 1.00 | 1.00 | 1.00 | ok |
| NMR | 2 | 1.00 | 1.00 | 1.00 | 1.00 | unvalidated |

**[medido]** F1 medio (técnicas con positivos): 0.97 con `body_any` frente a 0.86 con la definición `primary` preregistrada (recall < 0,85 en 9 técnicas): por eso se promovió `body_any` (Enmienda 1). STEM y SAXS no tuvieron positivos en la validación (**sin validar**, sus resultados deben leerse con cautela); UV-Vis tiene precisión baja (convención de anotación: lectura colorimétrica vs. espectroscopía; detector UV de HPLC). **Optimismo:** el diccionario se ajustó mirando esos mismos 56 artículos, así que estas métricas sobreestiman el rendimiento en artículos nuevos.

Corrección de Rogan-Gladen (prevalencia observada → ajustada con la sensibilidad/especificidad de la validación; `data/prevalence.csv`): DLS 0.55 → 0.49; UVVis 0.34 → 0.27; TEM 0.38 → 0.37; cryoEM 0.06 → 0.04. Con una validación provisional y de un solo anotador estos ajustes son indicativos, no definitivos.

### 3.2 Prevalencia marginal

Prevalencia (%) en la muestra principal (con IC95 % en `data/prevalence.csv`; † recall < 0,85; ‡ precisión < 0,80; ° sin validar).

| Técnica | Todas | LNP | Liposomas | SLN/NLC | PLN (híbridas) | Poliméricas | Inorgánicas | AAV |
|---|---|---|---|---|---|---|---|---|
| DLS | 55 | 70 | 48 | 88 | 91 | 62 | 42 | 5 |
| zeta | 50 | 59 | 46 | 85 | 91 | 58 | 41 | 3 |
| TEM | 38 | 32 | 33 | 47 | 68 | 38 | 62 | 12 |
| UVVis‡ | 34 | 16 | 28 | 54 | 43 | 39 | 68 | 7 |
| qPCR_ddPCR° | 27 | 37 | 18 | 10 | 11 | 18 | 9 | 75 |
| SEM | 23 | 9 | 7 | 31 | 19 | 46 | 49 | 1 |
| FTIR | 21 | 7 | 9 | 36 | 29 | 33 | 43 | 0 |
| XRD | 12 | 4 | 5 | 20 | 17 | 13 | 36 | 1 |
| DSC_TGA | 11 | 5 | 4 | 32 | 22 | 14 | 15 | 1 |
| NMR° | 10 | 10 | 9 | 7 | 18 | 23 | 9 | 0 |
| RiboGreen_EE° | 8 | 35 | 2 | 1 | 4 | 1 | 1 | 4 |
| EDS | 7 | 2 | 4 | 2 | 2 | 7 | 30 | 0 |
| cryoEM | 6 | 14 | 7 | 2 | 5 | 1 | 1 | 8 |
| AFM | 4 | 3 | 3 | 5 | 6 | 5 | 7 | 1 |
| NTA | 4 | 7 | 4 | 3 | 4 | 4 | 1 | 1 |
| XPS° | 3 | 1 | 3 | 1 | 1 | 2 | 7 | 0 |
| Raman_SERS° | 2 | 1 | 1 | 3 | 1 | 2 | 9 | 0 |
| STEM° | 2 | 1 | 1 | 1 | 2 | 1 | 5 | 0 |
| BET° | 2 | 1 | 1 | 0 | 0 | 0 | 8 | 0 |
| VSM° | 1 | 0 | 1 | 0 | 0 | 2 | 6 | 0 |
| SAXS° | 1 | 4 | 1 | 1 | 2 | 2 | 1 | 0 |
| TNS_pKa° | 1 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| AUC° | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 5 |

### 3.3 Matriz de P(B | A)

Figura 1 (`figures/fig1_matriz_P_B_dado_A.*`): una subtrama por familia más la agregada, filas = A con n(A), ordenadas por agrupamiento sobre 1 − phi; celdas con n(A) < 20 en gris con hachurado y celdas con IC ancho pálidas. Valores completos: `data/pairs.csv`. Algunas celdas clave (P(B|A) [IC95 %] (n(A∧B)/n(A))):

| A → B | Todas | LNP | Liposomas | SLN/NLC | PLN (híbridas) | Poliméricas | Inorgánicas |
|---|---|---|---|---|---|---|---|
| TEM → DLS | 75 % [72–78] (588/779) | 89 % [82–94] (107/120) | 79 % [71–85] (90/114) | 96 % [90–98] (97/101) | 95 % [87–98] (73/77) | 83 % [76–88] (119/144) | 52 % [45–59] (98/187) |
| SEM → DLS | 60 % [55–64] (284/475) | 83 % [67–92] (29/35) | 73 % [54–86] (19/26) | 94 % [86–98] (63/67) | 91 % [72–97] (20/22) | 58 % [51–65] (101/174) | 35 % [28–43] (52/149) |
| DLS → zeta | 85 % [83–87] (939/1104) | 79 % [74–84] (209/263) | 85 % [79–90] (144/169) | 92 % [87–95] (174/189) | 97 % [92–99] (101/104) | 87 % [82–91] (205/235) | 80 % [72–86] (102/128) |
| zeta → DLS | 92 % [90–93] (939/1021) | 95 % [91–97] (209/220) | 89 % [83–93] (144/162) | 96 % [92–98] (174/181) | 97 % [92–99] (101/104) | 93 % [89–95] (205/221) | 82 % [74–87] (102/125) |
| TEM → zeta | 72 % [69–75] (562/779) | 78 % [70–85] (94/120) | 77 % [69–84] (88/114) | 90 % [83–95] (91/101) | 95 % [87–98] (73/77) | 81 % [73–86] (116/144) | 53 % [46–60] (99/187) |
| cryoEM → DLS | 70 % [61–77] (83/119) | 92 % [82–97] (48/52) | 81 % [62–91] (21/26) | 100 % [51–100] (4/4) (n(A)<20) | 83 % [44–97] (5/6) (n(A)<20) | 67 % [21–94] (2/3) (n(A)<20) | 50 % [15–85] (2/4) (n(A)<20) |
| cryoEM → SAXS | 10 % [6–17] (12/119) | 15 % [8–28] (8/52) | 4 % [1–19] (1/26) | 25 % [5–70] (1/4) (n(A)<20) | 33 % [10–70] (2/6) (n(A)<20) | 0 % [0–56] (0/3) (n(A)<20) | 0 % [0–49] (0/4) (n(A)<20) |
| TEM → SAXS | 1 % [1–3] (11/779) | 6 % [3–12] (7/120) | 0 % [0–3] (0/114) | 0 % [0–4] (0/101) | 0 % [0–5] (0/77) | 1 % [0–4] (1/144) | 2 % [1–5] (3/187) |
| TEM → UVVis | 50 % [46–53] (389/779) | 31 % [23–40] (37/120) | 41 % [33–50] (47/114) | 60 % [51–69] (61/101) | 45 % [35–57] (35/77) | 49 % [41–57] (71/144) | 72 % [65–78] (135/187) |
| TEM → XRD | 21 % [18–24] (160/779) | 8 % [4–14] (9/120) | 10 % [5–16] (11/114) | 25 % [17–34] (25/101) | 10 % [5–19] (8/77) | 18 % [13–25] (26/144) | 43 % [36–50] (81/187) |
| SEM → EDS | 24 % [20–28] (112/475) | 17 % [8–33] (6/35) | 23 % [11–42] (6/26) | 4 % [2–12] (3/67) | 0 % [0–15] (0/22) | 13 % [9–19] (23/174) | 50 % [42–58] (74/149) |
| TEM → EDS | 13 % [11–15] (100/779) | 5 % [2–10] (6/120) | 11 % [7–19] (13/114) | 3 % [1–8] (3/101) | 3 % [1–9] (2/77) | 11 % [7–17] (16/144) | 32 % [26–39] (60/187) |
| TEM → FTIR | 35 % [31–38] (269/779) | 18 % [12–25] (21/120) | 20 % [14–28] (23/114) | 40 % [31–49] (40/101) | 26 % [17–37] (20/77) | 47 % [39–55] (67/144) | 52 % [45–59] (98/187) |
| SEM → FTIR | 47 % [43–52] (225/475) | 34 % [21–51] (12/35) | 35 % [19–54] (9/26) | 48 % [36–60] (32/67) | 64 % [43–80] (14/22) | 43 % [36–51] (75/174) | 56 % [48–63] (83/149) |

### 3.4 Asociaciones y combinaciones

Diez asociaciones más fuertes entre técnicas (agregada, FDR < 5 %). En la mayoría de los pares el OR de MH y el ajustado son menores que el crudo, lo que indica el efecto de la composición por familia (paradoja de Simpson), aunque no en todos (p. ej. DLS–TEM):

| Par | phi | OR crudo | OR MH (por familia) | OR ajustado (logística, SE por revista) | IC95 % ajustado |
|---|---|---|---|---|---|
| DLS – zeta | 0.76 | 58.23 | 39.14 | 39.53 | 29.7–52.7 |
| FTIR – XRD | 0.46 | 15.01 | 8.50 | 9.30 | 6.0–14.3 |
| EDS – XRD | 0.40 | 14.95 | 8.30 | 8.38 | 5.3–13.3 |
| DSC_TGA – FTIR | 0.36 | 8.85 | 5.94 | 6.15 | 4.4–8.6 |
| FTIR – SEM | 0.36 | 6.08 | 2.97 | 3.14 | 2.4–4.2 |
| EDS – SEM | 0.35 | 13.36 | 8.16 | 8.71 | 5.8–13.0 |
| TEM – zeta | 0.34 | 4.44 | 4.39 | 4.41 | 3.4–5.7 |
| FTIR – UVVis | 0.34 | 5.53 | 3.03 | 3.15 | 2.3–4.3 |
| DLS – TEM | 0.33 | 4.36 | 4.78 | 4.74 | 3.6–6.3 |
| SEM – XRD | 0.33 | 6.89 | 3.74 | 3.95 | 2.9–5.4 |

**[medido]** Solo 24 de 253 parejas superan phi = 0,2 con FDR < 5 % (Figura 3). Los bloques son: dispersión de luz (DLS–zeta–TEM), sólidos (FTIR–XRD–EDS–SEM–DSC/TGA) y ensayos de EE (RiboGreen–TNS).

Combinaciones más frecuentes (soporte; agregada; Apriori, soporte mínimo 0,05):

| Conjunto | Soporte | Artículos |
|---|---|---|
| {DLS, zeta} | 46.4 | 939 |
| {TEM, DLS} | 29.0 | 588 |
| {TEM, zeta} | 27.8 | 562 |
| {TEM, DLS, zeta} | 25.8 | 523 |
| {DLS, UVVis} | 24.1 | 489 |
| {zeta, UVVis} | 23.0 | 465 |
| {DLS, zeta, UVVis} | 21.2 | 429 |
| {TEM, UVVis} | 19.2 | 389 |

- **[medido]** P(UVVis | TEM, DLS, zeta) = 53 % [48 %–57 %] (276/523).
- **[medido]** P(SEM | TEM, DLS, zeta) = 22 % [18 %–25 %] (113/523).
- **[medido]** P(SAXS | TEM, DLS, zeta) = 2 % [1 %–3 %] (8/523).
- **[medido]** P(FTIR | TEM, DLS, zeta) = 37 % [33 %–41 %] (193/523).

Figura 4 (UpSet) muestra las 15 combinaciones exactas más frecuentes por familia: ninguna domina fuera de AAV, donde un artículo típico solo usa qPCR/ddPCR.

### 3.5 Tendencia temporal (secundaria)

Prueba de Cochran-Armitage sobre año (2015–2026; 2015–2017 es una submuestra de ≈ 40 artículos por familia). Sin corrección por composición de familias.

| Técnica | CA_z | CA_p | Prev. primer año (%) | Prev. último año (%) |
|---|---|---|---|---|
| DLS | 1.28 | 0.2 | 53.8 | 52.2 |
| FTIR | 2.28 | 0.0224 | 7.69 | 16.9 |
| SEM | -1.47 | 0.142 | 17.3 | 17.6 |
| TEM | -0.152 | 0.879 | 36.5 | 34.6 |
| UVVis | -0.645 | 0.519 | 23.1 | 25.8 |
| XRD | 0.569 | 0.569 | 9.62 | 8.47 |
| qPCR_ddPCR | 6.86 | 6.82e-12 | 21.2 | 41.4 |
| zeta | 0.694 | 0.487 | 50 | 45.8 |

Con 8 pruebas, el umbral de Bonferroni es p < 0.0063: solo qPCR_ddPCR lo supera; en el resto no se detecta tendencia (FTIR, p = 0,02, no sobrevive a la corrección).

### 3.6 Contraste de hipótesis (reglas de `PREREGISTRATION.md`)

| # | Veredicto | Evidencia [medido] | Cautela |
|---|---|---|---|
| H1 | confirmada | liposome: P(DLS\|TEM)=0.79 [0.71-0.85] (90/114) vs P(DLS\|SEM)=0.73 [0.54-0.86] (19/26); LNP: P(DLS\|TEM)=0.89 [0.82-0.94] (107/120) vs P(DLS\|SEM)=0.83 [0.67-0.92] (29/35); SLN_NLC: P(DLS\|TEM)=0.96 [0.90-0.98] (97/101) vs P(DLS\|SEM)=0.94 [0.86-0.98] (63/67); PLN: P(DLS\|TEM)=0.95 [0.87-0.98] (73/77) vs P(DLS\|SEM)=0.91 [0.72-0.97] (20/22); polymeric: P(DLS\|TEM)=0.83 [0.76-0.88] (119/144) vs P(DLS\|SEM)=0.58 [0.51-0.65] (101/174); organicas agregadas: P(DLS\|TEM)=0.87 [0.84-0.90] (486/556) vs P(DLS\|SEM)=0.72 [0.66-0.76] (232/324); p(z)=5.38e-09 |  |
| H2 | parcial (ver evidencia) | LNP: P(SAXS\|cryoEM)=0.15 [0.08-0.28] (8/52) vs P(SAXS\|TEM seco)=0.02 [0.01-0.07] (2/98) (Fisher unilateral p=0.00338); liposome: P(SAXS\|cryoEM)=0.04 [0.01-0.19] (1/26) vs P(SAXS\|TEM seco)=0.00 [0.00-0.04] (0/100) (Fisher unilateral p=0.206) | detector no plenamente fiable/validado: SAXS:unvalidated |
| H3 | confirmada | P(UVVis\|TEM): inorganica=0.72 [0.65-0.78] (135/187) vs organicas=0.45 [0.41-0.49] (251/556) (p=1.51e-10); P(XRD\|TEM): inorganica=0.43 [0.36-0.50] (81/187) vs organicas=0.14 [0.12-0.17] (79/556) (p=0) | detector no plenamente fiable/validado: UVVis:precision_low |
| H4 | parcial (ver evidencia) | inorganica: P(EDS\|SEM)=0.50 [0.42-0.58] (74/149) vs P(EDS\|TEM)=0.32 [0.26-0.39] (60/187) (p=0.00108); liposome: P(EDS\|SEM)=0.23 [0.11-0.42] (6/26); liposome: P(EDS\|TEM)=0.11 [0.07-0.19] (13/114); LNP: P(EDS\|SEM)=0.17 [0.08-0.33] (6/35); LNP: P(EDS\|TEM)=0.05 [0.02-0.10] (6/120); SLN_NLC: P(EDS\|SEM)=0.04 [0.02-0.12] (3/67); SLN_NLC: P(EDS\|TEM)=0.03 [0.01-0.08] (3/101); PLN: P(EDS\|SEM)=0.00 [0.00-0.15] (0/22); PLN: P(EDS\|TEM)=0.03 [0.01-0.09] (2/77); polymeric: P(EDS\|SEM)=0.13 [0.09-0.19] (23/174); polymeric: P(EDS\|TEM)=0.11 [0.07-0.17] (16/144) |  |
| H5 | confirmada | phi(DLS,zeta) ALL=0.76; familias con phi>=0.3: ['LNP', 'liposome', 'SLN_NLC', 'PLN', 'polymeric', 'inorganic', 'AAV']; rango entre pares de nucleo (ALL): 1 de 105 |  |
| H6 | confirmada | FTIR: polymeric=0.33 [0.29-0.38] (126/380) vs LNP=0.07 [0.05-0.10] (25/374) (IC no solapados); FTIR: SLN_NLC=0.36 [0.30-0.43] (77/214) vs LNP=0.07 [0.05-0.10] (25/374) (IC no solapados); DSC_TGA: polymeric=0.14 [0.11-0.18] (53/380) vs LNP=0.05 [0.03-0.07] (18/374) (IC no solapados); DSC_TGA: SLN_NLC=0.32 [0.26-0.39] (69/214) vs LNP=0.05 [0.03-0.07] (18/374) (IC no solapados) |  |
| H7 | confirmada | AAV: P(AUC o qPCR; cryoEM o TEM)=0.87 [0.75-0.93] (46/53) vs P(DLS; cryoEM o TEM)=0.09 [0.04-0.20] (5/53); prevalencia SEM=2/291 | detector no plenamente fiable/validado: AUC:unvalidated, qPCR_ddPCR:unvalidated |
| H8 | confirmada | P(zeta\|DLS) ALL=0.85 [0.83-0.87] (939/1104); por familia: LNP: 0.79 [0.74-0.84] (209/263); liposome: 0.85 [0.79-0.90] (144/169); SLN_NLC: 0.92 [0.87-0.95] (174/189); PLN: 0.97 [0.92-0.99] (101/104); polymeric: 0.87 [0.82-0.91] (205/235); inorganic: 0.80 [0.72-0.86] (102/128); AAV: 0.25 [0.10-0.49] (4/16) |  |
| H9 | confirmada | micrografia+espectro en la misma figura entre articulos con EM: ALL=0.16 [0.14-0.18] (185/1144); por familia: LNP=16/168=0.10; liposome=28/138=0.20; SLN_NLC=6/154=0.04; PLN=8/99=0.08; polymeric=45/268=0.17; inorganic=82/262=0.31; AAV=0/55=0.00; rango=0.31  [proxy: pie con termino de microscopia y de espectroscopia; el detector de pie es mas estricto que el de articulo] |  |
| H10 | confirmada | LNP(n=168): cryo=0.31 negstain\|SEM=0.43 TEM seco sin teñir (explicito)=0.02 TEM sin cryo ni tincion declarada=0.32; liposome(n=138): cryo=0.19 negstain\|SEM=0.56 TEM seco sin teñir (explicito)=0.03 TEM sin cryo ni tincion declarada=0.33; SLN_NLC(n=154): cryo=0.03 negstain\|SEM=0.73 TEM seco sin teñir (explicito)=0.04 TEM sin cryo ni tincion declarada=0.29; PLN(n=99): cryo=0.06 negstain\|SEM=0.46 TEM seco sin teñir (explicito)=0.03 TEM sin cryo ni tincion declarada=0.45; polymeric(n=268): cryo=0.01 negstain\|SEM=0.76 TEM seco sin teñir (explicito)=0.04 TEM sin cryo ni tincion declarada=0.35; inorganic(n=262): cryo=0.02 negstain\|SEM=0.62 TEM seco sin teñir (explicito)=0.11 TEM sin cryo ni tincion declarada=0.60; AAV(n=55): cryo=0.44 negstain\|SEM=0.56 TEM seco sin teñir (explicito)=0.00 TEM sin cryo ni tincion declarada=0.11 |  |

Notas: **H2**: P(SAXS|cryo-EM) supera a TEM seco en LNP (diferencia significativa) pero no en liposomas (n pequeño; 1 positivo): veredicto *parcial*. **H4** parcial: EDS es más probable dado SEM que dado TEM en inorgánicas, pero EDS **no** es raro (< 10 %) en todas las familias orgánicas. **H7** depende de qPCR/ddPCR, que en AAV mide títulos pero en otras familias mide expresión génica (interpretar solo en AAV; extendidas sin validar). **H9** usa un proxy por pie de figura. **H10**: compara lípidos, polímeros e inorgánicas (AAV queda fuera de la hipótesis; su cryo-EM es 44 %).

### 3.7 Sensibilidad

| Escenario | Pares | Correlación P(B|A) con la principal | Acuerdo en dirección (lift) | Pares que cambian de significancia FDR |
|---|---|---|---|---|
| cc_by_only | 420 | 0.995 | 0.943 | 44 |
| def:any | 506 | 0.998 | 0.976 | 22 |
| def:caption_only | 240 | 0.943 | 0.900 | 40 |
| def:methods_only | 420 | 0.993 | 0.957 | 38 |
| def:primary | 306 | 0.964 | 0.908 | 46 |
| multilabel_duplicated | 506 | 0.999 | 0.988 | 20 |
| reliable_techniques_only | 132 | 1.000 | 1.000 | 0 |

**[medido]** Las probabilidades condicionales casi no cambian entre definiciones y escenarios (r ≥ 0,94), y la dirección de la asociación coincide en ≥ 90 % de los pares; los cambios están en qué pares alcanzan significancia FDR; **[inferido]** son más numerosos con definiciones más restrictivas o con solo CC BY, donde baja la potencia. Excluir las técnicas con detector poco fiable no cambia ninguna conclusión. Lista de pares que cambian: `data/sensitivity_summary.csv`; todas las tablas: `data/pairs_sensitivity.csv`.

## 4. Implicaciones para el esquema de la base

Regla usada **[inferido]**: *obligatorio* si la técnica se reporta en ≥ 30 % de los artículos de alguna familia núcleo (LNP, liposomas, SLN/NLC, PLN, poliméricas); *opcional* si en ≥ 10 %; si no, *solo bandera de texto*. Inorgánicas y AAV se evalúan aparte. † = detector poco fiable, ° = sin validar.

| Técnica | Nivel | Máx. familias núcleo (%) | Inorgánicas (%) | AAV (%) |
|---|---|---|---|---|
| zeta | obligatorio | 91 | 41 | 3 |
| DLS | obligatorio | 91 | 42 | 5 |
| TEM | obligatorio | 68 | 62 | 12 |
| UVVis‡ | obligatorio | 54 | 68 | 7 |
| SEM | obligatorio | 46 | 49 | 1 |
| qPCR_ddPCR° | obligatorio solo en AAV (títulos) | 37 | 9 | 75 |
| FTIR | obligatorio | 36 | 43 | 0 |
| RiboGreen_EE° | obligatorio | 35 | 1 | 4 |
| DSC_TGA | obligatorio | 32 | 15 | 1 |
| NMR° | opcional | 23 | 9 | 0 |
| XRD | opcional | 20 | 36 | 1 |
| cryoEM | opcional | 14 | 1 | 8 |
| EDS | solo bandera | 7 | 30 | 0 |
| NTA | solo bandera | 7 | 1 | 1 |
| TNS_pKa° | solo bandera | 6 | 0 | 0 |
| AFM | solo bandera | 6 | 7 | 1 |
| SAXS° | solo bandera | 4 | 1 | 0 |
| XPS° | solo bandera | 3 | 7 | 0 |
| Raman_SERS° | solo bandera | 3 | 9 | 0 |
| VSM° | solo bandera | 2 | 6 | 0 |
| STEM° | solo bandera | 2 | 5 | 0 |
| BET° | solo bandera | 1 | 8 | 0 |
| AUC° | solo bandera | 1 | 0 | 5 |

Campos de preparación de EM (obligatorio para toda micrografía, brief §1.2): entre los artículos con EM, la tinción negativa se declara en una fracción grande de TEM de lípidos/polímeros y el cryo solo es frecuente en LNP y AAV (H10, §3.6); en inorgánicas la mayoría de TEM no declara tinción (seco por defecto), por lo que el valor «no declarado» debe existir en el esquema.

### Pares micrografía–espectro realistas por familia

| Familia | Artículos muestra | Con EM | EM + algún espectro (artículo) | EM + espectro en la misma figura (n) | … como % de EM | IC95 % | [inferido] Población × % misma figura |
|---|---|---|---|---|---|---|---|
| LNP | 374 | 168 | 84 | 16 | 10 | 6–15 | 111 |
| Liposomas | 349 | 138 | 78 | 28 | 20 | 14–28 | 669 |
| SLN/NLC | 214 | 154 | 121 | 6 | 4 | 2–8 | 31 |
| PLN (híbridas) | 114 | 99 | 68 | 8 | 8 | 4–15 | 8 |
| Poliméricas | 380 | 268 | 196 | 45 | 17 | 13–22 | 862 |
| Inorgánicas | 303 | 262 | 232 | 82 | 31 | 26–37 | 4175 |
| AAV | 291 | 55 | 5 | 0 | 0 | 0–7 | 0 |

La última columna proyecta a la población de cada familia (2018–2026, acceso abierto, con licencia) la fracción de artículos con micrografía y espectro en la misma figura observada en la muestra; es una **proyección [inferida]** que asume que la muestra es representativa y que el proxy por pie de figura se comporta igual en toda la población. Solo una minoría de los artículos con EM tiene el par a nivel de figura; solo con licencia CC BY (≈ 71 % de la población elegible) se podría redistribuir la imagen.

## 5. Limitaciones y desviaciones

- **Validación provisional de un solo anotador (Claude):** falta la doble anotación humana, el kappa y la confirmación de recall/precisión. STEM y SAXS no tuvieron positivos en la validación; las técnicas extendidas (Raman, XPS, BET, VSM, AUC, SEC-MALS, FFF, fotometría de masas, CDMS, qPCR/ddPCR, RiboGreen, TNS) no se validaron y un error de regex ya se encontró en una (RiboGreen).
- **Mención ≠ dato:** detectar una técnica en Métodos/Resultados/pies no garantiza que los datos sean útiles (p. ej. «DLS» como control de calidad sin datos mostrados, UV-Vis como lectura de ensayos). El proxy de «misma figura» se basa en pies de figura y es más estricto que la detección a nivel de artículo.
- **Definición principal cambiada tras la validación** (Enmienda 1), antes de calcular co-ocurrencias; las demás definiciones están en sensibilidad.
- **Familias ruidosas:** las consultas por título/resumen incluyen artículos donde el nanoportador es un reactivo (liposomas en estructural, AuNP/AgNP como material en recubrimientos o biosensores, vectores AAV). Esto es parte de «el corpus real» pero diluye los resultados de esas familias; no se hizo un filtro semántico por tema.
- **Sesgo de acceso abierto y de revista:** solo OA con licencia registrada (la proporción CC BY es 71 % de la población elegible); el reporte de técnicas depende de la revista (se agrupó por revista en la logística, sin efecto aleatorio).
- **Texto en el suplemento:** el texto completo de Europe PMC no incluye el material suplementario; técnicas descritas solo allí no se ven (p. ej. artículos de Chem. Sci. con Métodos en el SI).
- **Tendencia 2015–2017** proviene de una submuestra pequeña; no controla composición de familia/revista.
- **Familia primaria** = la más mencionada en título+resumen; la sensibilidad con duplicación multietiqueta se reporta (r = 0,999, sin cambios de conclusión).
- **No obtenido:** ningún dato requirió «no obtenido» salvo la política de términos de la API REST de Europe PMC (403) y la lectura de los artículos/listas mencionados en el brief §2.4 (no se intentó; no eran necesarios para el cálculo).
- **Tamaño del conjunto de validación:** 56 en lugar de 50 (7 familias × 8); recall con pocos positivos tiene IC amplios.

## 6. Reproducibilidad

`make all` (Linux/macOS) o `.\run_all.ps1` (Windows). Semilla fija en `config/sampling.yaml`; consultas y descargas con fecha en `logs/queries.jsonl`; listas de PMCID por celda en `data/cell_pmcids/`; evidencia por detección (≤ 25 palabras) en `data/evidence.csv`. Si no se vuelve a descargar, la caché de XML (no redistribuible) reproduce todo. Archivos principales: `data/articles.csv`, `data/pairs.csv`, `data/pairs_sensitivity.csv`, `data/gold_set.csv`, `data/gold_metrics.csv`, `figures/`.
