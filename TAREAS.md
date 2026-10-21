# Tareas del equipo (propuesta del 2026-10-20; los plazos son tentativos)

**Plazo duro:** el video del hackatón se entrega el **domingo 25 de octubre, 5:45 pm (hora de Costa Rica)**. Todo lo demás se ordena hacia atrás desde esa fecha.

**Estado de los datos hoy:** 85 artículos en el repositorio (66 con licencia CC BY, 17 NC/ND, 2 en conflicto). Se quitó uno que estaba retractado. Las cifras de los artículos CC BY no cambiaron. Las imágenes aún no están extraídas y la verificación humana no está hecha. Todo es provisional.

## Reglas de trabajo
- Cada persona trabaja en su rama (`hector/…`, `bryan/…`, `carlos/…`) y en su carpeta. Nada va a `main` sin que lo revise otra persona.
- **Imágenes solo de los artículos con licencia verde.** Los valores numéricos (tamaño, zeta) se pueden usar de todos, citando la fuente.
- Quien verifica a mano **no mira** la copia de otro ni `curation/work/clave_modelo.csv` hasta terminar.
- Todo modelo se evalúa partiendo **por artículo** (`pmcid`), nunca por fila ni por imagen.

## Héctor: decidir, resolver y cerrar
| # | Tarea | Archivo | Cuándo |
|---|---|---|---|
| 1 | Pasar tus 15 filas ya revisadas: copia de `curation/verificacion_humana_80.csv` como `verificacion_humana_80_hector.csv` | `curation/` | 20 oct |
| 2 | Decidir las dos reglas de la puerta (ver abajo) | `curation/POLITICA_PUERTA.md` | 20 oct |
| 3 | Resolver los 7 casos difíciles; en cada fila hay una recomendación para que solo marques o corrijas | `curation/casos_dificiles_hector.csv` | 21 oct |
| 4 | Cerrar los 2 artículos con conflicto de licencia | `curation/articles_curated.csv` | 21 oct |
| 5 | Revisar lo que suban Bryan y Carlos y aprobar los cambios a `main` | GitHub | cada día |
| 6 | Aprobar la congelación de la v0.1 (etiqueta en GitHub) | GitHub | 22 oct |
| 7 | Con la v0.1 congelada: entrenar y evaluar los modelos, hacer la interfaz y el guion del video (ver `brief_chatgpt_hackathon.md`) | por definir | 22 a 25 oct |

**Las dos reglas por decidir** (recomendación de Claude: sí a las dos, siempre con bandera visible):
1. ¿Se acepta el medio declarado en cualquier parte de Métodos, si es del mismo instrumento?
2. ¿Se aceptan valores leídos de una figura, marcados como «aproximado»?

## Bryan: crecer y conectar
| # | Tarea | Cuándo |
|---|---|---|
| C1 | Revisar los artículos rescatados (aceptar o rechazar) que Claude le pase | 22 oct |
| C2 | Proponer palabras de búsqueda para inorgánicas y SAXS; conseguir y revisar las listas de DOI de LipoDB, LNP Atlas y PLGA NP | 21 a 22 oct |
| D1 | Redactar el esquema v0.1 (campos obligatorios del plan, licencia por fila, cita, confianza del vínculo) | 21 oct |
| D2 | Descargar las figuras de los artículos verdes y recortar los paneles (herramienta de la Tarea A del brief); verificar a ojo el vínculo imagen–formulación | 21 a 22 oct |
| D3 | Decidir qué espectros entran en la v0.1 (FTIR, XRD, UV-Vis, SAXS) | 21 oct |

## Carlos: validar de forma independiente
| # | Tarea | Cuándo |
|---|---|---|
| 1 | Revisar por su cuenta los **mismos 15 artículos** que revisó Héctor, sin ver sus respuestas, y luego 20 más (`verificacion_humana_80_carlos.csv`). Se salta el n49, que está retractado | 21 a 22 oct |
| 2 | Verificar la licencia en la página del editor de los artículos verdes que van a tener imágenes | 21 a 22 oct |
| 3 | Buscar retractaciones, erratas y expresiones de preocupación en el repositorio y en la lista de 78 | 22 oct |
| 4 | Doble anotación del detector de la fase 1 (`GOLD_GUIDELINES.md`), en los huecos | antes del 25 oct |

## Claude: lo automático
Rescate de falsos negativos con las reglas decididas, tabla de pares imagen–formulación, cálculo de acuerdo y kappa, regeneración de las tablas y subida a GitHub.

## Ruta crítica
- **20 oct:** Héctor 1 y 2. Bryan D1. Claude sube todo a GitHub.
- **21 oct:** Héctor 3 y 4. Bryan C2, D2 y D3. Carlos 1 y 2. Claude hace el rescate.
- **22 oct:** se integra lo aprobado y se **congela la v0.1**. Desde aquí los modelos usan datos fijos.
- **23 a 24 oct:** modelos, interfaz y guion.
- **25 oct, antes de las 5:45 pm:** subir el video.

Si el rescate no termina el 21 de octubre, la v0.1 sale con los 85 artículos actuales y el rescate pasa a la v0.2.
