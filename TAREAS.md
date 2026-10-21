# Tareas del equipo (actualizado el 2026-10-20; los plazos son tentativos)

**Plazo duro:** el video del hackatón se entrega el **domingo 25 de octubre, 5:45 pm (hora de Costa Rica)**.

**Estado de los datos hoy:** 85 artículos en el repositorio: 66 con licencia CC BY y 19 NC/ND, sin conflictos de licencia. Se quitó uno retractado. Las imágenes aún no están extraídas y la verificación humana no está hecha. Todo es provisional.

Cada persona tiene su archivo:
- **Bryan:** [TAREAS_BRYAN.md](TAREAS_BRYAN.md)
- **Carlos:** [TAREAS_CARLOS.md](TAREAS_CARLOS.md) (trabaja en Codex y lee GitHub, pero no escribe: entrega sus archivos a Héctor)
- **Héctor:** abajo.

## Reglas de trabajo
- Cada persona trabaja en su rama y en su carpeta. Nada va a `main` sin que lo revise otra persona.
- **Imágenes solo de artículos con licencia verde.** Los valores numéricos se pueden usar de todos, citando la fuente.
- Quien verifica a mano no mira la clave del modelo ni las revisiones por IA hasta terminar.
- Todo modelo se evalúa partiendo **por artículo** (`pmcid`), nunca por fila ni por imagen.
- La política vigente de la puerta está en [curation/POLITICA_PUERTA.md](curation/POLITICA_PUERTA.md).

## Héctor: decidir, resolver y entregar el hackatón
| # | Tarea | Cuándo |
|---|---|---|
| 1 | Decir «ok» a la política de la puerta o cambiarla (`curation/POLITICA_PUERTA.md`) | 20 oct |
| 2 | Preguntas para el organizador del hackatón (Tarea F del brief): son las más sensibles al tiempo | 20 oct |
| 3 | Resolver los 7 casos difíciles en `curation/casos_dificiles_hector.csv` | 21 oct |
| 4 | Revisar y aprobar los pull requests de Bryan | cada día |
| 5 | Aprobar la congelación de la v0.1 (etiqueta en GitHub) | 22 oct |
| 6 | Hackatón con datos congelados: modelo de línea base (C), interfaz (B), modelo de imágenes si hay paneles (D) | 22 a 24 oct |
| 7 | Guion y grabación del video (E) | 24 y 25 oct |

## Claude
Rescate del medio no declarado (unos 30 artículos), pares imagen–formulación con los paneles de Bryan, regeneración de tablas, cálculo de acuerdos y subida a GitHub.

## Ruta crítica
- **20 oct:** Héctor 1 y 2. Bryan empieza la tarea 1 (figuras). Carlos empieza su tarea 1.
- **21 oct:** Héctor 3. Bryan: paneles y esquema. Carlos: hoja verde. Claude: rescate.
- **22 oct:** se integra lo aprobado y se **congela la v0.1**.
- **23 y 24 oct:** modelos, interfaz y guion.
- **25 oct, antes de las 5:45 pm:** subir el video.

Si el rescate no termina el 21 de octubre, la v0.1 sale con los 85 artículos actuales y el rescate pasa a la v0.2.
