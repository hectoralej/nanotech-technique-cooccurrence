# Carlos: instrucciones actualizadas (versión 2, 21 de octubre)

**Para ti y para tu Codex.** Este archivo reemplaza a `TAREAS_CARLOS.md`. Se entiende solo. Lee todo antes de empezar.

**Plazo duro del hackatón: domingo 25 de octubre, 5:45 pm (hora de Costa Rica). Los datos se congelan el 22 de octubre.** Por eso el orden de abajo importa más que hacerlo todo.

## 1. Lo que revisamos de tus jornadas 1 a 5

Gracias: el trabajo está bien documentado y es honesto sobre sus límites. Lo importante:

**Lo que sirve tal cual**
- Las **pasadas hechas por IA se presentaron como lo que son** (pre-revisión), y dejaste en blanco los campos científicos de n=1–39, que debían ser de una persona. Eso era lo correcto.
- La **Jornada 3** aporta algo nuevo: 4 erratas y 1 retractado localizados con evidencia. El retractado coincide con el n49 que ya habíamos marcado.
- La **Jornada 4** da una primera lectura útil del detector de la fase 1: con la definición que usa el análisis principal (`body_any`) el F1 medio es 94,9 %. El UV-Vis es el punto débil (precisión 57 %), probablemente porque cuenta ensayos UV-Vis que no son del nanoportador. **Es acuerdo entre dos IA, no un gold humano.**
- La **Jornada 5** (diccionario y README) es un borrador útil para Bryan.

**Lo que NO cuenta todavía como verificación humana**
- Las jornadas 1, 2 (campos científicos), 3 y 4 son **trabajo asistido por IA**. Una pre-revisión sirve para saber dónde mirar, pero no reemplaza que **tú** abras el artículo y decidas.
- Un `no` de la IA puede significar «no encontré la evidencia», no «el dato está mal».

**Lo que cambia de prioridad**
- **Jornada 5 (esquema y README):** ya no hagas más. Mándale los archivos a Bryan, que define las taxonomías. No hay que seguir trabajando en eso.
- **Jornada 4 (detector):** se pospone para después del hackatón. Etiqueta siempre esas hojas como «IA», nunca como humanas.
- **Jornada 3 (avisos):** ya no hace falta resolver los 70 casos no concluyentes. Solo importan los artículos con licencia verde que van a tener imágenes (ver tarea 1). Las retractaciones ya están cubiertas por la marca de Europe PMC, que automatizamos.

## 2. Reglas de trabajo (siguen igual)
- Tu Codex puede **abrir páginas, buscar y resumir evidencia**, pero **la decisión `si` o `no` de cada campo científico la tomas tú**, y no se completa automáticamente.
- **No abras ni uses** `clave_modelo.csv` ni ninguna revisión por IA de otras personas (la de Codex de Héctor, `qc_codex`) para llenar tus hojas independientes.
- Marca siempre el origen: lo que hizo la IA se llama «pre-revisión IA»; lo que decidiste tú, «revisión humana». No los mezcles en la misma columna.
- Solo imágenes de artículos con licencia verde (CC BY o CC0). No descargues figuras por tu cuenta.
- Sin AAV ni virus.
- **Cómo entregar:** no tienes acceso de escritura a GitHub. Guarda tus archivos con tu nombre y mándaselos a Héctor por el chat del equipo; él los sube.

## 3. Qué hacer ahora, en este orden

### Tarea 1 (urgente, para el 22 de octubre): decidir tú los casos que la IA dejó en duda
**Archivo:** tu copia `verificacion_repositorio_verde_codex.csv` (68 filas). No rehagas las 68: concéntrate donde la pre-revisión de la IA marcó problemas, que son las filas que más pueden afectar a los modelos.

Orden de trabajo:
1. **Licencias** (las 22 filas en `no la encuentro`): abre el DOI en tu navegador, mira la etiqueta de licencia del editor y escribe `CC BY`, `CC0`, otra licencia o `no localizada`. Estas filas deciden si se pueden usar imágenes de ese artículo.
2. **Los 5 casos señalados:** el corrigendum de la Figura 7I (10.1016/j.bioactmat.2026.02.031), la posible desalineación de fila (10.3390/gels8070402), la errata de la Figura 5 (10.3390/biomedicines10050985), las unidades meV de zeta (10.3390/bioengineering5010004) y la micrografía del registro 10.3390/polym13193350.
3. **Las filas donde la IA puso `no`** en tamaño (7), zeta (10) o micrografía de la misma muestra (16). Abre el artículo, busca el dato donde dice la columna `donde_buscar_*` y decide `si` o `no`. Escribe una nota corta con la evidencia (tabla o figura) en `notas`.
4. **Control de calidad de lo que la IA marcó `si`:** abre **8 filas al azar** de las que salieron todo `si`. Si encuentras errores, avísale a Héctor antes de seguir.
5. **Medio de DLS/zeta:** la IA marcó `no` en 37 filas. Eso puede ser evidencia insuficiente, no un error. Revisa las que ya estés abriendo por los puntos anteriores; no hace falta abrir todas.

**Qué hacemos con tus respuestas:** una fila con `no` y nota no se borra: la muestra queda marcada y fuera de los modelos hasta que se resuelva.
**Entrega:** `verificacion_repositorio_verde_carlos_FINAL.csv`, con una columna `origen` que diga `humano` o `pre-IA` en cada decisión.

### Tarea 2 (22 y 23 de octubre): verificar el conjunto ampliado
**Archivo (nuevo):** `curation/verificacion_conjunto_ampliado.csv` (en el repositorio de GitHub, que puedes leer). Son **20 artículos** de un conjunto grande que otra IA (ChatGPT) está extrayendo. Antes de ampliarlo a miles de artículos necesitamos medir si lo que extrae es fiable.

Por cada fila:
1. Abre `doi_link`.
2. Mira lo que se extrajo (`paneles_extraidos`, `descriptores_extraidos`, `espectros_extraidos`) y compáralo con el artículo.
3. Llena:

| Columna | Qué poner |
|---|---|
| `micrografias_correctas` | `si` / `no`: ¿esas figuras son micrografías de la nanopartícula, con la técnica y la muestra que se dicen? |
| `descriptores_correctos` | `si` / `no`: ¿tamaño, PDI y zeta corresponden a esa muestra? |
| `espectros_correctos` | `si` / `no`: ¿los espectros existen y son del nanoportador (no de un fármaco puro ni de un ensayo)? |
| `es_nanoportador` | `si` / `no`: ¿el artículo estudia nanopartículas propias? Las de síntesis verde o comerciales cuentan como `si` aquí; anota en `notas` si no son de entrega |
| `licencia_en_pagina_del_editor` | `CC BY`, `CC0`, otra o `no localizada` |
| `notas` | Lo que veas raro |

Regla: **si dudas, `no` y explica.** Unos 5 a 8 minutos por artículo.

### Tarea 3 (solo si te sobra tiempo, hasta el 24 de octubre): revisión independiente de la lista de 78
**Archivo:** `curation/verificacion_humana_80.csv`, artículos `n` del 1 al 39, siguiendo `GUIA_REVISION.md`. Aquí sí es **lectura desde cero, sin ayuda de la IA para decidir**. Empieza por n=1–20 (ahí ya cerraste `licencia_ok`). Los 9 DOI de `licencia_ok=no` los cubre la tarea 1 si aparecen en la hoja verde; si no, ábrelos aparte.
Esta tarea sirve para medir la precisión del filtro y **no es necesaria para el hackatón**; es mejor entregarla bien y tarde que mal y a tiempo.

### Para después del hackatón
- Doble anotación **humana** del detector (56 artículos), con otra persona y sin ver las etiquetas de la IA.
- Los 70 avisos editoriales no concluyentes, si el equipo decide que hacen falta.

## 4. Resumen de entregas
| Archivo | Cuándo |
|---|---|
| `verificacion_repositorio_verde_carlos_FINAL.csv` (tarea 1) | 22 de octubre |
| `verificacion_conjunto_ampliado_carlos.csv` (tarea 2) | 23 de octubre |
| `verificacion_humana_80_carlos.csv` (tarea 3) | 24 de octubre, si da tiempo |
| Archivos de Jornada 5 a Bryan | hoy |

Si algo no se entiende, pregúntale a Héctor antes de adivinar.
