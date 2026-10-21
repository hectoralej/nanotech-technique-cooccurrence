# Léeme para Claude: proyecto de técnicas de caracterización en nanoportadores

**Para quién es esto:** Héctor me pasó este proyecto en un `.rar`. Descomprímelo, abre la carpeta `nanotech-technique-cooccurrence/` en tu sesión de Claude y pega el prompt del final. Este archivo resume lo que se hizo en una conversación larga con Claude para que tu sesión arranque con el mismo contexto.

## 1. Qué es el proyecto

Proyecto del curso de Quimioinformática (nanoinformática y nanoentrega), con Bryan, Carlos y Héctor. Objetivo: decidir qué técnicas de caracterización capturar para una **base de datos multimodal (micrografía + espectros) de nanoportadores** que sirva para entrenar modelos de machine learning. Familias estudiadas: LNP, liposomas, SLN/NLC, PLN (lípido-polímero), poliméricas, inorgánicas y AAV.

Todo sale de **texto completo de acceso abierto de Europe PMC**, con citas literales verificadas por código.

## 2. Lo que se hizo

**Fase 1: matriz de co-ocurrencia entre técnicas** (carpeta raíz, `REPORT.md`)
- 2.396 artículos procesados (2.025 en el análisis principal, 2018–2026). Un detector por secciones (regex con máscaras) marca qué técnicas aparecen en cada artículo.
- Probabilidades condicionales P(B|A) entre técnicas, por familia, con IC de Wilson, odds ratio, lift, phi, FDR, Mantel-Haenszel y regresión con errores robustos por revista. Hipótesis H1–H10 registradas antes del análisis (`PREREGISTRATION.md`).
- Hallazgos principales (`entrega/REPORTE_SIMPLE.md`):
  1. DLS, zeta y TEM dominan en lípidos y polímeros; en inorgánicas mandan UV-Vis, TEM y SEM.
  2. Las técnicas secundarias van en bloque: UV-Vis, SEM, FTIR, XRD (y EDS en inorgánicas).
  3. AAV es la excepción: casi sin DLS ni zeta, y se apoya en qPCR/ddPCR.
  4. El qPCR fuera de AAV es lectura biológica (expresión génica), no caracterización del nanoportador.
  5. Pares micrografía + espectro: abundantes por artículo, escasos por figura (4–31 %).
- Limitación: el detector se validó con una anotación **provisional de un solo anotador (Claude)**. Falta la doble anotación humana (`GOLD_GUIDELINES.md`, `data/gold_set_human_template.csv`).

**Fase 2: curación estricta de calidad** (carpeta `curation/`)
- Objetivo: un repositorio de artículos con **micrografía útil (TEM y variantes, o SEM) + DLS + zeta de una misma muestra**, con el medio declarado, sin virus ni dependientes de PCR. Reglas y puntaje fijados antes de ver resultados en `curation/SCORING.md` (niveles S ≥ 85, A 70–84, B 60–69).
- Método: filtro por código → lectura con agentes Haiku y Sonnet → verificación de citas por código → arbitraje de desacuerdos → puerta y puntaje por código → licencia, duplicados y laboratorios → auditoría de Claude.
- **Resultado: 86 artículos en el repositorio** (S 9, A 67, B 10): SLN/NLC 21, LNP 18, PLN 15, liposomas 15, poliméricas 14, inorgánicas 3. 273 artículos leídos con modelos; 148 casi-aprobados. Licencias: 66 CC BY (verde), 18 NC/ND (amarillo), 2 en conflicto.
- **Lista de verificación humana (2026-10-18):** `curation/verificacion_humana_80.csv`, 78 artículos solo con CC BY, con el DOI como enlace (`https://doi.org/...`). Incluye una muestra aleatoria y artículos elegidos para llenar vacíos (SAXS, cryo-EM, inorgánicas, espectroscopía sobre la partícula). La clave del modelo está en `curation/work/clave_modelo.csv`: no abrir hasta terminar.
- Piloto al azar de 100 artículos: 26 entraron (26 %). Las rondas 1 y 2 usaron un filtro barato por código (tabla con tamaño y zeta, y medio declarado junto a DLS y zeta) y rindieron 48–52 %.
- Aprendizaje: Haiku sobre un extracto corto dejó fuera a 8 de 23 artículos que Sonnet aprobó (recall 65 %). Por eso la ronda 2 fue Sonnet primero y Haiku como segunda lectura.
- Costo: unos 10,5 millones de tokens de subagentes en total; la ampliación bajó a ≈ 110 mil por artículo nuevo en el repositorio.

## 3. Mapa de la carpeta

| Ruta | Qué hay |
|---|---|
| `REPORT.md`, `PREREGISTRATION.md`, `README.md` | informe de la fase 1, hipótesis fechadas, cómo reproducir |
| `entrega/` | reporte simple, diagrama del procedimiento y las 4 figuras de decisión (PNG) |
| `figures/` | figuras 1–7 de la fase 1 (PNG, SVG y HTML interactivo) |
| `data/` | `articles_all.csv` (2.396 artículos y técnicas detectadas), `pairs.csv`, `evidence.csv`, `prevalence.csv`, `trend.csv` (tendencias), `hypotheses.csv`, `gold_*.csv` |
| `data/cache/` | texto completo XML de Europe PMC (≈ 790 MB). Puede no venir en el `.rar`; se regenera con `run_all.ps1` (≈ 25 min) |
| `src/`, `config/`, `tests/` | código de la fase 1, taxonomía de técnicas (`techniques.yaml`) y pruebas |
| `curation/articles_curated.csv` | **la base de datos: los 86 artículos** con DOI, familia, nivel, puntaje, técnicas y licencia |
| `curation/measurements.csv` | una fila por medición, con valores, condiciones y cita literal verificada |
| `curation/near_miss.csv`, `excluded.csv`, `pending.csv` | casi-aprobados (148), excluidos con motivo, candidatos aún sin leer (530) |
| `curation/Repositorio_articulos.docx` | referencias APA 7 |
| `curation/INFORME.md`, `ESTADO.md` | informe completo y cómo reanudar |
| `curation/verificacion_humana_80.csv`, `GUIA_REVISION.md` | 78 artículos para revisión humana, con el DOI como enlace; `curation/verificacion_excluidas.csv` lista los que se quitaron y por qué |
| `curation/manual_review.csv` | 3 artículos que Claude excluyó a mano (se pueden revertir) |
| `curation/prompts/` | instrucciones de los agentes (extracción, arbitraje) |
| `curation/work/` | salidas crudas de los agentes y paquetes de texto (se pueden regenerar) |

## 4. Para trabajar con el código

- Windows y PowerShell. Python 3.11 o superior. Desde la carpeta del proyecto: `$env:PYTHONPATH=(Get-Location).Path` y luego `python -m curation.<módulo>`. Dependencias en `requirements.txt` (más `python-docx`, `rapidfuzz`, `networkx`).
- Cómo reanudar una ronda de curación: sección «Cómo reanudar una ronda» de `curation/ESTADO.md`.
- No edites archivos con tildes usando `Set-Content` ni `Get-Content`: corrompen la codificación. Usa la herramienta de edición o Python.
- Si un CSV está abierto en Excel, no se puede sobrescribir: ciérralo antes.
- Rutas largas: el código usa el prefijo `\\?\` (`src/common.py`).

## 5. Pendiente y decisiones abiertas

1. **Revisión humana** de `verificacion_humana_80.csv` (cada persona en su copia, sin ver la del otro) y de los artículos excluidos a mano. Certifica los umbrales: puerta ≥ 0,95, kappa ≥ 0,80, licencia 100 %. Hasta entonces, todo es **provisional**.
2. **Licencias:** de los 86 artículos, 18 son CC BY-NC/-ND y 2 tienen conflicto entre fuentes. Solo se redistribuyen figuras de los 66 en verde. (Un error del clasificador, ya corregido, había inflado antes los conflictos.)
3. **Vacíos:** inorgánicas (2 artículos) y SAXS (7 mediciones en 3 artículos). Necesitan búsqueda dirigida de artículos nuevos.
4. Decidir si se sigue ampliando con los 530 candidatos sin leer.
5. No se descargó el material suplementario (57 % de los candidatos lo tiene); el repositorio probablemente está subestimado.

## 6. Cómo prefiere Héctor que se trabaje

- Respuestas en español, concisas y al grano.
- Calidad sobre cantidad. Si hay que relajar un criterio, preguntar antes.
- Agentes Haiku para lo repetitivo y masivo; Sonnet solo para revisión compleja y en pocos casos. Ser eficiente con los tokens: buscar palabras clave antes de leer un artículo completo.
- Mostrar un diagrama simple del plan antes de empezar un trabajo grande.
- Marcar como provisional todo lo que no tenga validación humana.

## Prompt para pegar en tu sesión de Claude

> Lee `LEEME_PARA_CLAUDE.md` en esta carpeta y luego `curation/ESTADO.md` y `curation/INFORME.md`. Resúmeme en 10 líneas dónde está el proyecto y qué falta. No ejecutes nada todavía. Después te diré qué sigue: revisión humana de la hoja, resolver los conflictos de licencia, buscar artículos de inorgánicas y SAXS, o seguir ampliando el repositorio.
