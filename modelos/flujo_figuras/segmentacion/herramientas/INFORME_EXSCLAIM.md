# Prueba local de EXSCLAIM! — control previo detenido

Fecha: 24/10/2026. Encargo leído completo: `equipo/encargos/CODEX_HERRAMIENTAS_EXSCLAIM.md`.

**Resultado: no instalado ni ejecutado en esta tarea.** El control previo de licencias no se pudo dar por válido. La prueba de rendimiento queda pendiente; no se declara validado ningún paso de inferencia.

## 1. Fuente, versión y mantenedores

| Implementación | Fuente oficial | Último commit consultado, UTC | Versión |
|---|---|---|---|
| Original, correspondiente al método del artículo | MaterialEyes/exsclaim | 26/03/2022 18:30:10; `003400ee7486568cd229d3ff012613baa2fa6554` | `setup.py`: 0.1.0; PyPI conserva 0.1.0 |
| Actual | MaterialEyes/exsclaim2.0 | 25/09/2026 21:41:32; `af44fe3bc9ccdf4cd117608513fd59ab6653f8ce` | PyPI: 2.5.2 |

Los metadatos oficiales de PyPI enlazan respectivamente con esos repositorios. El original identifica a Eric Schwenker, Trevor Spreadbury, Weixin Jiang y Maria Chan. La página actual de PyPI identifica a Len Washington III como mantenedor y muestra las cuentas `lwashington3`, `materialeyes` y `tspread`. El JSON actual deja vacíos algunos campos de autor/licencia: esos vacíos, por sí solos, no prueban que falte una licencia. [PyPI](https://pypi.org/project/exsclaim/), [original](https://github.com/MaterialEyes/exsclaim), [actual](https://github.com/MaterialEyes/exsclaim2.0).

El paquete actual es una evolución oficial, no un paquete ajeno; sin embargo, no reproduce sin cambios el método original. Cambia, entre otros componentes, el distribuidor de pies a LLM. No se debe instalar la última versión sin fijarla y atribuirle las métricas del artículo original.

## 2. Licencias y pesos: motivo de parada

- **Código original:** `LICENSE` contiene GPL-3.0, mientras `setup.py` declara el clasificador MIT. Conservo ambos archivos como evidencia. Esta discrepancia necesita aclaración para fijar una distribución y sus condiciones. No estoy afirmando que GPL sea incompatible con nuestra investigación.
- **Código actual:** el archivo `LICENSE` declara MIT. No lo considero desconocido por los campos vacíos de PyPI.
- **Pesos de EXSCLAIM!:** el código original identifica checkpoints externos en Google Drive; el actual añade descargas del servidor oficial para YOLO11 y conserva componentes externos de escala. En los README y archivos revisados no encontré una declaración inequívoca que establezca la licencia aplicable a esos checkpoints. No descargué binarios para intentar inferir sus condiciones.
- **Regla aplicada:** el encargo dice: «Si la licencia es incompatible o desconocida […] detente y repórtalo». Al quedar sin verificar el permiso aplicable a los pesos necesarios, detuve la prueba antes de instalar. No se solicitó autorización para saltarse esa regla.

Evidencia del código: [licencia original](https://github.com/MaterialEyes/exsclaim/blob/003400ee7486568cd229d3ff012613baa2fa6554/LICENSE), [metadatos originales](https://github.com/MaterialEyes/exsclaim/blob/003400ee7486568cd229d3ff012613baa2fa6554/setup.py), [licencia actual](https://github.com/MaterialEyes/exsclaim2.0/blob/af44fe3bc9ccdf4cd117608513fd59ab6653f8ce/LICENSE), [origen de checkpoints actuales](https://github.com/MaterialEyes/exsclaim2.0/blob/af44fe3bc9ccdf4cd117608513fd59ab6653f8ce/exsclaim/utilities/models.py).

## 3. Estado de las tareas, en orden

| Paso | Estado comprobado |
|---|---|
| Control de fuente | Repositorios, versiones, fechas y mantenedores identificados |
| Control de licencia | No superado: condiciones de checkpoints sin verificar y discrepancia del original |
| Instalar y separar 22 figuras | No iniciado por la parada previa; el CSV contiene 22 figuras |
| Normalizar cajas y mapear clases | Pendiente; no generé un JSON vacío que pudiera confundirse con una predicción |
| Comparar con humanos | No hay archivos `cajas_humano_*.json` en `anotador/` al comprobarlo |
| Comparar con Haiku C001 | Pendiente por falta de predicciones EXSCLAIM; no abrí sus resultados |
| Distribuir pies de 22 figuras | Pendiente por la misma parada previa |
| Ampliar a 100 figuras | No autorizado por los criterios: no existen métricas de aceptación |

**Tiempo por figura: no medido. IoU medio: no disponible. Cajas con IoU >=0,7: no disponible. Figuras con número correcto de paneles: no evaluadas (0 de 22 procesadas; no significa 0 aciertos).** No se inició ejecución de modelos y se detuvo antes del tope de 90 minutos. La consulta reproducible de metadatos tardó 1,49 segundos; no representa el tiempo total de revisión ni inferencia.

## 4. Aspectos metodológicos a resolver al reanudar

El formato solicitado y el mapeo siguen siendo apropiados: microscopía → `micro`; gráfica/difracción/ilustración → `otro`; parent/omit/unclear → `otro` y `revisar: true`. Hay que conservar `clase_exsclaim` y normalizar las cajas respecto de la figura completa. No se debe convertir toda gráfica en espectro.

El comparador existente requiere cuidado: si hay menos cajas predichas que de referencia, agota los candidatos y puede fallar en `max()`; además, el porcentaje de tipo igual está fijado a 100 % mediante `tip = 1.0`. No ejecuté ni modifiqué ese script. Antes de usar sus cifras como criterio de cierre habrá que manejar cajas faltantes y no interpretar ese campo como una medición de clasificación. Estos defectos se observaron por lectura del código; no son resultados de una prueba de EXSCLAIM!.

Insets, cuadrículas densas y baja resolución continúan como casos que deben medirse, no como errores locales ya demostrados. El valor mediano de 476 px procede del encargo y no fue recalculado.

## 5. FigEx2 y comprobaciones anteriores

Mantengo lo acordado: evaluación de ejecución en HPC más adelante; no se instaló ni lanzó allí. Código y pesos son públicos. El árbol de código revisado no contiene un archivo de licencia; los metadatos de los pesos no contienen `cardData` y el listado no incluye README ni LICENSE. Por ello su licencia también queda sin verificar, pese a su disponibilidad pública. La licencia del modelo base no basta para establecer la de los adaptadores y el detector. [Repositorio](https://github.com/Huang-AI4Medicine-Lab/FigEx2), [pesos](https://huggingface.co/Huang-AI4Medicine-Lab/FigEx2-8B).

El análisis anterior de arquitectura y hardware se conserva. No repetí el intento previo de `ensurepip`, que fallaba con PermissionError en temporales de Windows. Ese es un bloqueo técnico adicional documentado anteriormente; **la causa de parada de esta tarea es el control previo de licencia**. Python observado previamente: 3.13.7; dependencias e importación funcional sin validar.

## 6. Recomendación y reanudación

**Recomendación entre las opciones del encargo: descartar su incorporación por ahora.** Es una decisión provisional de integración, no una conclusión de que el separador sea malo. No hay evidencia para nombrarlo tercer revisor ni separador principal.

Para reanudar se necesita una declaración oficial que aclare las condiciones de los checkpoints elegidos y, si se usa el original, la discrepancia GPL/MIT. Después: fijar versión, crear entorno propio aquí, resolver instalación, ejecutar un ejemplo en CPU y luego las 22 figuras. Solo tras superar IoU >=0,7 y >=80 % de figuras con conteo esperado correspondería ampliar a 100.

## Evidencias y reproducibilidad

Comando ejecutado desde el proyecto:

```powershell
py -3.13 modelos\flujo_figuras\segmentacion\herramientas\auditar_fuentes.py
```

No hubo comandos de instalación en esta tarea. `resultados/auditoria_fuentes.json` registra endpoints, fechas y versiones; los archivos `LICENSE_*`, `setup_exsclaim_original.txt` y `origen_pesos_*` conservan evidencias leídas de las fuentes oficiales descargadas previamente por commit. `CHECKPOINT.md` permite reanudar.

No se ejecutaron scraper, entrenamiento, git ni HPC; no se modificaron curation, producto, imágenes, comparador ni resultados de otros revisores. Todos los archivos nuevos de esta tarea están dentro de herramientas.
